import json
import os
import shutil
import time
import bcrypt
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Header, Request, Body
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from fastapi.responses import FileResponse
from loguru import logger
from app.services.config_log_service import log_config_change

router = APIRouter(prefix="/api/v1/ui", tags=["UI Config"])

# ─── Pydantic Models (Validation) ────────────────────────────────────────────────
class SiteConfigPatch(BaseModel):
    model_config = ConfigDict(extra='ignore')
    name: Optional[str] = None
    shortName: Optional[str] = None
    primaryColor: Optional[str] = None
    gmsClientCode: Optional[str] = None
    channelId: Optional[str] = None
    logoUrl: Optional[str] = None

class RobotConfigPatch(BaseModel):
    model_config = ConfigDict(extra='ignore')
    WIDTH: Optional[float] = None
    LENGTH: Optional[float] = None
    IDLE_COLOR: Optional[str] = None
    WORKING_COLOR: Optional[str] = None
    CHARGING_COLOR: Optional[str] = None
    ERROR_COLOR: Optional[str] = None
    OFFLINE_COLOR: Optional[str] = None

class MapConfigPatch(BaseModel):
    model_config = ConfigDict(extra='ignore')
    MULTIPLIER: Optional[float] = None
    SNAP_DISTANCE: Optional[float] = None
    ORIGIN_OFFSET_X: Optional[float] = None
    ORIGIN_OFFSET_Y: Optional[float] = None
    DEFAULT_LOC_SIZE: Optional[float] = None
    OPACITY: Optional[float] = None
    ANGLE_OFFSET: Optional[float] = None
    ENABLE_SOCKET_LOG: Optional[bool] = None

class StationConfigUpdate(BaseModel):
    alias: str
    containerCfg: Optional[Dict[str, float]] = None

class ContainerConfigUpdate(BaseModel):
    codePrefix: Optional[str] = None
    categories: Optional[Dict[str, Dict[str, Any]]] = None

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # ESIG root
DATA_DIR = BASE_DIR / "app" / "data"
CONFIG_FILE = DATA_DIR / "ui_config.json"

# Dynamic asset path: handles both development (static/ui_assets) and PyInstaller build (ui_assets next to static)
_built_assets = BASE_DIR / "ui_assets"
if _built_assets.exists():
    ASSETS_DIR = _built_assets
else:
    ASSETS_DIR = BASE_DIR / "static" / "ui_assets"

# Ensure directories exist at startup
DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
(ASSETS_DIR / "ContainerImg").mkdir(parents=True, exist_ok=True)

# ─── Admin Password ────────────────────────────────────────────────────────────
# Loaded from environment variable or defaults to "admin1234"
ADMIN_PASSWORD = os.environ.get("UI_CONFIG_PASSWORD", "admin1234")

# ─── Allowed file types for upload ─────────────────────────────────────────────
ALLOWED_IMAGE_EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg"}

# ─── Password Lockout State ────────────────────────────────────────────────────
FAILED_ATTEMPTS = {}

# ─── In-Memory Cache ───────────────────────────────────────────────────────────
_config_cache = None

# ─── Helpers ───────────────────────────────────────────────────────────────────


def _load_config() -> dict:
    """Load the current ui_config.json from memory or disk."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    if not CONFIG_FILE.exists():
        raise HTTPException(
            status_code=404, detail="ui_config.json not found. Please initialize it."
        )
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        _config_cache = json.load(f)
        return _config_cache


def _save_config(data: dict) -> None:
    """Save updated configuration back to disk atomically."""
    global _config_cache
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Atomic write: write to temp file then rename
    temp_file = CONFIG_FILE.with_suffix('.tmp')
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.flush()
        os.fsync(f.fileno())  # Ensure it is written to physical disk
    
    # os.replace is an atomic operation on POSIX, and close to it on Windows
    os.replace(temp_file, CONFIG_FILE)
    _config_cache = data  # Update in-memory cache


def _is_bcrypt_hash(s: str) -> bool:
    """Check if a string looks like a bcrypt hash (starts with $2y$, $2b$ or $2a$)."""
    # Standard bcrypt hashes are 60 characters long.
    return len(s) == 60 and (s.startswith('$2b$') or s.startswith('$2a$') or s.startswith('$2y$'))


def _check_password(x_admin_password: str | None) -> None:
    """Validate admin password provided in the X-Admin-Password header."""
    if not x_admin_password:
        raise HTTPException(
            status_code=403, detail="Admin password required. Access denied."
        )

    # Case 1: Hashed Comparison (Industry Standard)
    if _is_bcrypt_hash(ADMIN_PASSWORD):
        try:
            pw_bytes = x_admin_password.encode('utf-8')
            hash_bytes = ADMIN_PASSWORD.encode('utf-8')
            if bcrypt.checkpw(pw_bytes, hash_bytes):
                return
        except Exception as e:
            logger.error(f"Password hash check failed: {e}")
            raise HTTPException(
                status_code=403, detail="Security validation error. Access denied."
            )
        raise HTTPException(
            status_code=403, detail="Invalid admin password. Access denied."
        )

    # Case 2: Plain-text Fallback (Migration/Legacy Support)
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=403, detail="Invalid admin password. Access denied."
        )
    
    # Log warning if still using plain-text to remind about technical debt
    logger.warning("🔔 Security Alert: Admin access granted via PLAIN-TEXT password. Please upgrade to Bcrypt hash.")


async def _notify_ui_update(request: Request) -> None:
    """Emit Socket.IO event to tell frontend clients to reload UI Config."""
    if hasattr(request.app.state, "sio"):
        await request.app.state.sio.emit("esig:ui:config_updated", {"ts": time.time()})


# ─── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/verify-password")
async def verify_password(request: Request, x_admin_password: str | None = Header(default=None)):
    """
    POST /api/v1/ui/verify-password
    Endpoint to check if the password is correct, with Brute-Force lockout protection.
    """
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # ดึงค่าจาก config เพื่อความยืดหยุ่น ถ้าไม่มีให้ใช้ค่าเริ่มต้น 180 วิ และ แบน 5 ครั้ง
    try:
        cfg = _load_config()
        sec_cfg = cfg.get("security", {})
        lockout_duration = int(sec_cfg.get("lockout_duration", 180))
        max_failures = int(sec_cfg.get("max_failures", 5))
    except Exception:
        lockout_duration = 180
        max_failures = 5
    
    record = FAILED_ATTEMPTS.get(client_ip, {"failures": 0, "locked_until": 0})
    if now < record["locked_until"]:
        raise HTTPException(
            status_code=429, 
            detail=f"Too many failed attempts. Locked out for {int(record['locked_until'] - now)} seconds."
        )

    # Check Password with Hashing / Plain fallback
    is_valid = False
    if _is_bcrypt_hash(ADMIN_PASSWORD):
        try:
            pw_bytes = x_admin_password.encode('utf-8')
            hash_bytes = ADMIN_PASSWORD.encode('utf-8')
            if bcrypt.checkpw(pw_bytes, hash_bytes):
                is_valid = True
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            is_valid = False
    else:
        is_valid = (x_admin_password == ADMIN_PASSWORD)

    if not is_valid:
        record["failures"] += 1
        if record["failures"] >= max_failures:
            record["locked_until"] = now + lockout_duration
            record["failures"] = 0
        FAILED_ATTEMPTS[client_ip] = record
        raise HTTPException(
            status_code=403, detail="Invalid admin password. Access denied."
        )
        
    # Reset on success
    if client_ip in FAILED_ATTEMPTS:
        del FAILED_ATTEMPTS[client_ip]
        
    return {"success": True, "message": "Password verified."}


@router.get("/config")
async def get_ui_config():
    """
    GET /api/v1/ui/config
    Returns the full UI configuration for the React frontend.
    No authentication required (read-only).
    """
    config = _load_config()
    return {"success": True, "data": config}


@router.patch("/config/map")
async def update_map_config(
    request: Request, body: MapConfigPatch, x_admin_password: str | None = Header(default=None)
):
    """
    PATCH /api/v1/ui/config/map
    Update map settings (MULTIPLIER, ANGLE_OFFSET, etc).
    Requires X-Admin-Password header.
    """
    _check_password(x_admin_password)
    config = _load_config()
    update_data = body.model_dump(exclude_unset=True)
    config["map"].update(update_data)
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown", "map", "update", str(update_data)
    )
    logger.info(f"UI Config [map] updated: {update_data}")
    return {"success": True, "message": "Map config updated."}


@router.patch("/config/site")
async def update_site_config(
    request: Request, body: SiteConfigPatch, x_admin_password: str | None = Header(default=None)
):
    """PATCH /api/v1/ui/config/site - Update branding and site info."""
    _check_password(x_admin_password)
    config = _load_config()
    update_data = body.model_dump(exclude_unset=True)
    config["site"].update(update_data)
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "site",
        "update",
        str(update_data),
    )
    logger.info(f"UI Config [site] updated: {update_data}")
    return {"success": True, "message": "Site configuration updated."}


@router.patch("/config/robot")
async def update_robot_config(
    request: Request, body: RobotConfigPatch, x_admin_password: str | None = Header(default=None)
):
    """PATCH /api/v1/ui/config/robot - Update robot dimensions and colors."""
    _check_password(x_admin_password)
    config = _load_config()
    update_data = body.model_dump(exclude_unset=True)
    config["robot"].update(update_data)
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "robot",
        "update",
        str(update_data),
    )
    logger.info(f"UI Config [robot] updated: {update_data}")
    return {"success": True, "message": "Robot configuration updated."}


@router.patch("/config/colors")
async def update_colors_config(
    request: Request, body: Dict[str, str], x_admin_password: str | None = Header(default=None)
):
    """PATCH /api/v1/ui/config/colors - Update system status colors."""
    _check_password(x_admin_password)
    config = _load_config()
    config["colors"].update(body)
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "colors",
        "update",
        str(body),
    )
    logger.info(f"UI Config [colors] updated: {body}")
    return {"success": True, "message": "System colors updated."}


@router.post("/config/stations")
async def add_station(
    request: Request,
    code: str,
    body: dict,
    x_admin_password: str | None = Header(default=None),
):
    """
    POST /api/v1/ui/config/stations?code=STATION_CODE
    Add a new station entry. Requires X-Admin-Password header.
    Body: { "alias": "...", "containerCfg": { "T2000001": 90, "T0000005": 0 } }

    Validation:
    - 'code' must not be empty.
    - 'alias' must not be empty.
    - 'angle' must be a number.
    """
    _check_password(x_admin_password)
    if not code or not code.strip():
        raise HTTPException(
            status_code=422, detail="Station code (code) must not be empty."
        )
    if not body.get("alias", "").strip():
        raise HTTPException(status_code=422, detail="Station alias must not be empty.")
    if not isinstance(body.get("containerCfg"), dict):
        raise HTTPException(
            status_code=422, detail="Station 'containerCfg' must be a dictionary."
        )

    config = _load_config()
    upper_code = code.strip().upper()
    if upper_code in config["stations"]:
        raise HTTPException(
            status_code=409,
            detail=f"Station '{upper_code}' already exists. Use PATCH to update.",
        )

    config["stations"][upper_code] = body
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "stations",
        "add",
        f"Station: {upper_code} | Body: {body}",
    )
    logger.info(f"UI Config: Added station '{upper_code}' -> {body}")
    return {"success": True, "message": f"Station '{upper_code}' added.", "data": body}


@router.patch("/config/stations/{code}")
async def update_station(
    request: Request,
    code: str,
    body: dict,
    x_admin_password: str | None = Header(default=None),
):
    """
    PATCH /api/v1/ui/config/stations/{code}
    Update an existing station. Requires X-Admin-Password header.
    """
    _check_password(x_admin_password)
    config = _load_config()
    upper_code = code.strip().upper()
    if upper_code not in config["stations"]:
        raise HTTPException(
            status_code=404, detail=f"Station '{upper_code}' not found."
        )

    # Note: Extract newCode safely outside of the loop
    new_code = body.pop("newCode", None)

    if new_code:
        new_upper = new_code.strip().upper()
        if new_upper != upper_code:
            if new_upper in config["stations"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"Target station code '{new_upper}' already exists.",
                )
            # Rename the key
            config["stations"][new_upper] = config["stations"].pop(upper_code)
            upper_code = new_upper  # Keep reference for the update below

    config["stations"][upper_code].update(body)
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "stations",
        "update",
        f"Station: {upper_code} | Body: {body}",
    )
    logger.info(
        f"UI Config: Updated station '{upper_code}' -> {config['stations'][upper_code]}"
    )
    return {
        "success": True,
        "message": f"Station '{upper_code}' updated.",
        "data": config["stations"][upper_code],
    }


@router.delete("/config/stations/{code}")
async def delete_station(
    request: Request, code: str, x_admin_password: str | None = Header(default=None)
):
    """
    DELETE /api/v1/ui/config/stations/{code}
    Delete a station. Requires X-Admin-Password header.
    """
    _check_password(x_admin_password)
    config = _load_config()
    upper_code = code.strip().upper()
    if upper_code not in config["stations"]:
        raise HTTPException(
            status_code=404, detail=f"Station '{upper_code}' not found."
        )
    del config["stations"][upper_code]
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "stations",
        "delete",
        f"Station: {upper_code}",
    )
    logger.info(f"UI Config: Deleted station '{upper_code}'")
    return {"success": True, "message": f"Station '{upper_code}' deleted."}


@router.post("/config/floors")
async def add_floor(
    request: Request, body: dict, x_admin_password: str | None = Header(default=None)
):
    """
    POST /api/v1/ui/config/floors
    Add a new floor. Body: { "id": 4, "label": "FLOOR 4", "image": "/api/v1/ui/assets/Floor4.webp" }

    Validation:
    - 'id' must be a number.
    - 'label' must not be empty.
    - 'image' must not be empty (upload image first via /ui/assets/upload).
    """
    _check_password(x_admin_password)
    if not isinstance(body.get("id"), (int, float)):
        raise HTTPException(status_code=422, detail="Floor 'id' must be a number.")
    if not body.get("label", "").strip():
        raise HTTPException(status_code=422, detail="Floor 'label' must not be empty.")
    if not body.get("image", "").strip():
        raise HTTPException(
            status_code=422,
            detail="Floor 'image' URL must not be empty. Please upload the floor image first.",
        )

    config = _load_config()
    if any(f["id"] == body["id"] for f in config["floors"]):
        raise HTTPException(
            status_code=409, detail=f"Floor with id={body['id']} already exists."
        )
    config["floors"].append(body)
    config["floors"].sort(key=lambda f: f["id"])
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown", "floors", "add", str(body)
    )
    logger.info(f"UI Config: Added floor {body}")
    return {"success": True, "message": f"Floor {body['id']} added.", "data": body}


@router.delete("/config/floors/{floor_id}")
async def delete_floor(
    request: Request, floor_id: int, x_admin_password: str | None = Header(default=None)
):
    """DELETE /api/v1/ui/config/floors/{floor_id} — Remove a floor."""
    _check_password(x_admin_password)
    config = _load_config()
    original_count = len(config["floors"])
    config["floors"] = [f for f in config["floors"] if f["id"] != floor_id]
    if len(config["floors"]) == original_count:
        raise HTTPException(status_code=404, detail=f"Floor id={floor_id} not found.")
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "floors",
        "delete",
        f"Floor ID: {floor_id}",
    )
    logger.info(f"UI Config: Deleted floor id={floor_id}")
    return {"success": True, "message": f"Floor {floor_id} deleted."}


@router.patch("/config/floors/{floor_id}")
async def update_floor(
    request: Request,
    floor_id: int,
    body: dict,
    x_admin_password: str | None = Header(default=None),
):
    """PATCH /api/v1/ui/config/floors/{floor_id} — Update an existing floor."""
    _check_password(x_admin_password)
    config = _load_config()

    # Validation
    if not isinstance(body.get("id"), (int, float)):
        raise HTTPException(status_code=422, detail="Floor 'id' must be a number.")

    index = next((i for i, f in enumerate(config["floors"]) if f["id"] == floor_id), -1)
    if index == -1:
        raise HTTPException(status_code=404, detail=f"Floor id={floor_id} not found.")

    # Handle ID change if necessary (though ID is usually fixed for floors)
    new_id = body.get("id")
    if new_id != floor_id:
        if any(f["id"] == new_id for f in config["floors"]):
            raise HTTPException(
                status_code=409, detail=f"Target Floor id={new_id} already exists."
            )

    config["floors"][index].update(body)
    config["floors"].sort(key=lambda f: f["id"])
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "floors",
        "update",
        str(body),
    )
    logger.info(f"UI Config: Updated floor {floor_id} -> {body}")
    return {
        "success": True,
        "message": f"Floor {floor_id} updated.",
        "data": config["floors"][index],
    }


@router.post("/config/container-types")
async def add_container_type(
    request: Request, body: dict, x_admin_password: str | None = Header(default=None)
):
    """
    POST /api/v1/ui/config/container-types
    Add a new container type.

    Validation:
    - 'id' must not be empty.
    - 'name' must not be empty.
    - 'image' must not be empty (upload image first).
    - 'width', 'length' must be positive numbers.
    """
    _check_password(x_admin_password)
    if not body.get("id", "").strip():
        raise HTTPException(status_code=422, detail="Container 'id' must not be empty.")
    if not body.get("name", "").strip():
        raise HTTPException(
            status_code=422, detail="Container 'name' must not be empty."
        )
    if not body.get("image", "").strip():
        raise HTTPException(
            status_code=422,
            detail="Container 'image' must not be empty. Please upload the container image first.",
        )
    if not isinstance(body.get("width"), (int, float)) or body["width"] <= 0:
        raise HTTPException(
            status_code=422, detail="Container 'width' must be a positive number."
        )
    if not isinstance(body.get("length"), (int, float)) or body["length"] <= 0:
        raise HTTPException(
            status_code=422, detail="Container 'length' must be a positive number."
        )

    config = _load_config()
    if any(c["id"] == body["id"] for c in config["containerTypes"]):
        raise HTTPException(
            status_code=409, detail=f"Container type '{body['id']}' already exists."
        )
    config["containerTypes"].append(body)
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "container-types",
        "add",
        str(body),
    )
    logger.info(f"UI Config: Added container type '{body['id']}'")
    return {
        "success": True,
        "message": f"Container type '{body['id']}' added.",
        "data": body,
    }


@router.delete("/config/container-types/{type_id}")
async def delete_container_type(
    request: Request, type_id: str, x_admin_password: str | None = Header(default=None)
):
    """DELETE /api/v1/ui/config/container-types/{type_id} — Remove a container type."""
    _check_password(x_admin_password)
    config = _load_config()
    original_count = len(config["containerTypes"])
    config["containerTypes"] = [
        c for c in config["containerTypes"] if c["id"] != type_id
    ]
    if len(config["containerTypes"]) == original_count:
        raise HTTPException(
            status_code=404, detail=f"Container type '{type_id}' not found."
        )
    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "container-types",
        "delete",
        f"Type ID: {type_id}",
    )
    logger.info(f"UI Config: Deleted container type '{type_id}'")
    return {"success": True, "message": f"Container type '{type_id}' deleted."}


@router.patch("/config/container-types/{type_id}")
async def update_container_type(
    request: Request,
    type_id: str,
    body: dict,
    x_admin_password: str | None = Header(default=None),
):
    """
    PATCH /api/v1/ui/config/container-types/{type_id}
    Update an existing container type (name, width, length, color, image, etc.).
    Requires X-Admin-Password header.
    """
    _check_password(x_admin_password)
    config = _load_config()
    index = next(
        (
            i
            for i, c in enumerate(config.get("containerTypes", []))
            if c["id"] == type_id
        ),
        -1,
    )

    if index == -1:
        raise HTTPException(
            status_code=404, detail=f"Container type '{type_id}' not found."
        )

    # Note: Extract newType safely without triggering loop modifications later
    new_type_id = body.pop("newType", None)

    if new_type_id:
        if new_type_id != type_id:
            if any(c["id"] == new_type_id for c in config["containerTypes"]):
                raise HTTPException(
                    status_code=409,
                    detail=f"Target type id '{new_type_id}' already exists.",
                )
            # Update the ID immediately
            config["containerTypes"][index]["id"] = new_type_id
            type_id = new_type_id  # Update reference for logging/returning

    # Apply other updates
    config["containerTypes"][index].update(body)

    _save_config(config)
    await _notify_ui_update(request)
    log_config_change(
        request.client.host if request.client else "unknown",
        "container-types",
        "update",
        f"Type ID: {type_id} | Body: {body}",
    )
    logger.info(f"UI Config: Updated container type '{type_id}' -> {body}")
    return {
        "success": True,
        "message": f"Container type '{type_id}' updated.",
        "data": config["containerTypes"][index],
    }


# ─── Asset (Image) Endpoints ───────────────────────────────────────────────────


@router.post("/assets/upload")
async def upload_asset(
    request: Request,
    file: UploadFile = File(...),
    subfolder: str = "",
    x_admin_password: str | None = Header(default=None),
):
    """
    POST /api/v1/ui/assets/upload
    Upload an image asset (floor map or container icon).
    Use ?subfolder=ContainerImg for container icons.
    Requires X-Admin-Password header.

    Validation:
    - File must have an allowed image extension (.webp, .png, .jpg, .jpeg).
    """
    _check_password(x_admin_password)

    # Validate file extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid file type '{ext}'. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
        )

    # Determine save path
    if subfolder:
        save_dir = ASSETS_DIR / subfolder
        save_dir.mkdir(parents=True, exist_ok=True)
    else:
        save_dir = ASSETS_DIR

    save_path = save_dir / file.filename

    # Save file
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Append timestamp as cache-buster so browsers always fetch the latest image.
    ts = int(time.time())
    raw_path = (
        f"/api/v1/ui/assets/{subfolder + '/' if subfolder else ''}{file.filename}"
    )
    relative_path = f"{raw_path}?v={ts}"

    logger.info(f"UI Asset uploaded: {save_path}")
    log_config_change(
        request.client.host if request.client else "unknown",
        "assets",
        "upload",
        f"File: {file.filename} | Path: {relative_path}",
    )
    return {
        "success": True,
        "message": f"File '{file.filename}' uploaded successfully.",
        "url": relative_path,
    }


@router.get("/assets/{file_path:path}")
async def serve_asset(file_path: str):
    """
    GET /api/v1/ui/assets/{file_path}
    Serve a static UI asset (floor map image, container icon, etc.).
    """
    try:
        asset_path = (ASSETS_DIR / file_path).resolve()
        # Security Check: Prevent Path Traversal
        if not asset_path.is_relative_to(ASSETS_DIR.resolve()):
            raise HTTPException(status_code=403, detail="Path traversal not allowed.")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path.")
        
    if not asset_path.exists():
        raise HTTPException(status_code=404, detail=f"Asset '{file_path}' not found.")
    return FileResponse(str(asset_path))


@router.get("/assets")
async def list_assets():
    """
    GET /api/v1/ui/assets
    List all uploaded UI assets.
    """
    assets = []
    for f in ASSETS_DIR.rglob("*"):
        if f.is_file():
            relative = f.relative_to(ASSETS_DIR)
            assets.append(
                {
                    "filename": f.name,
                    "path": str(relative).replace("\\", "/"),
                    "url": f"/api/v1/ui/assets/{str(relative).replace(chr(92), '/')}",
                    "size_kb": round(f.stat().st_size / 1024, 1),
                }
            )
    return {"success": True, "data": assets, "count": len(assets)}
