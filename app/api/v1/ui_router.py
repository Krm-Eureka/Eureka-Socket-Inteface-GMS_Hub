import json
import os
import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from fastapi.responses import FileResponse
from loguru import logger

router = APIRouter(prefix="/api/v1/ui", tags=["UI Config"])

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # ESIG root
DATA_DIR = BASE_DIR / "app" / "data"
CONFIG_FILE = DATA_DIR / "ui_config.json"
ASSETS_DIR = BASE_DIR / "static" / "ui_assets"

# Ensure directories exist at startup
DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
(ASSETS_DIR / "ContainerImg").mkdir(parents=True, exist_ok=True)

# ─── Admin Password ────────────────────────────────────────────────────────────
# Loaded from environment variable or defaults to "admin1234"
ADMIN_PASSWORD = os.environ.get("UI_CONFIG_PASSWORD", "admin1234")

# ─── Allowed file types for upload ─────────────────────────────────────────────
ALLOWED_IMAGE_EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg"}

# ─── Helpers ───────────────────────────────────────────────────────────────────


def _load_config() -> dict:
    """Load the current ui_config.json from disk."""
    if not CONFIG_FILE.exists():
        raise HTTPException(
            status_code=404, detail="ui_config.json not found. Please initialize it."
        )
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_config(data: dict) -> None:
    """Save updated configuration back to disk."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def _check_password(x_admin_password: str | None) -> None:
    """Validate admin password provided in the X-Admin-Password header."""
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=403, detail="Invalid admin password. Access denied."
        )


# ─── Endpoints ─────────────────────────────────────────────────────────────────


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
    body: dict, x_admin_password: str | None = Header(default=None)
):
    """
    PATCH /api/v1/ui/config/map
    Update map settings (MULTIPLIER, ANGLE_OFFSET, etc).
    Requires X-Admin-Password header.
    """
    _check_password(x_admin_password)
    config = _load_config()
    config["map"].update(body)
    _save_config(config)
    logger.info(f"UI Config [map] updated: {body}")
    return {"success": True, "message": "Map config updated."}


@router.post("/config/stations")
async def add_station(
    code: str, body: dict, x_admin_password: str | None = Header(default=None)
):
    """
    POST /api/v1/ui/config/stations?code=STATION_CODE
    Add a new station entry. Requires X-Admin-Password header.
    Body: { "alias": "...", "angle": 90, "containerType": ["T2000001"] }

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
    if not isinstance(body.get("angle"), (int, float)):
        raise HTTPException(status_code=422, detail="Station angle must be a number.")

    config = _load_config()
    upper_code = code.strip().upper()
    if upper_code in config["stations"]:
        raise HTTPException(
            status_code=409,
            detail=f"Station '{upper_code}' already exists. Use PATCH to update.",
        )

    config["stations"][upper_code] = body
    _save_config(config)
    logger.info(f"UI Config: Added station '{upper_code}' -> {body}")
    return {"success": True, "message": f"Station '{upper_code}' added.", "data": body}


@router.patch("/config/stations/{code}")
async def update_station(
    code: str, body: dict, x_admin_password: str | None = Header(default=None)
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
    config["stations"][upper_code].update(body)
    _save_config(config)
    logger.info(f"UI Config: Updated station '{upper_code}' -> {body}")
    return {
        "success": True,
        "message": f"Station '{upper_code}' updated.",
        "data": config["stations"][upper_code],
    }


@router.delete("/config/stations/{code}")
async def delete_station(
    code: str, x_admin_password: str | None = Header(default=None)
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
    logger.info(f"UI Config: Deleted station '{upper_code}'")
    return {"success": True, "message": f"Station '{upper_code}' deleted."}


@router.post("/config/floors")
async def add_floor(body: dict, x_admin_password: str | None = Header(default=None)):
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
    logger.info(f"UI Config: Added floor {body}")
    return {"success": True, "message": f"Floor {body['id']} added.", "data": body}


@router.delete("/config/floors/{floor_id}")
async def delete_floor(
    floor_id: int, x_admin_password: str | None = Header(default=None)
):
    """DELETE /api/v1/ui/config/floors/{floor_id} — Remove a floor."""
    _check_password(x_admin_password)
    config = _load_config()
    original_count = len(config["floors"])
    config["floors"] = [f for f in config["floors"] if f["id"] != floor_id]
    if len(config["floors"]) == original_count:
        raise HTTPException(status_code=404, detail=f"Floor id={floor_id} not found.")
    _save_config(config)
    logger.info(f"UI Config: Deleted floor id={floor_id}")
    return {"success": True, "message": f"Floor {floor_id} deleted."}


@router.post("/config/container-types")
async def add_container_type(
    body: dict, x_admin_password: str | None = Header(default=None)
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
    logger.info(f"UI Config: Added container type '{body['id']}'")
    return {
        "success": True,
        "message": f"Container type '{body['id']}' added.",
        "data": body,
    }


@router.delete("/config/container-types/{type_id}")
async def delete_container_type(
    type_id: str, x_admin_password: str | None = Header(default=None)
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
    logger.info(f"UI Config: Deleted container type '{type_id}'")
    return {"success": True, "message": f"Container type '{type_id}' deleted."}


# ─── Asset (Image) Endpoints ───────────────────────────────────────────────────


@router.post("/assets/upload")
async def upload_asset(
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

    relative_path = (
        f"/api/v1/ui/assets/{subfolder + '/' if subfolder else ''}{file.filename}"
    )
    logger.info(f"UI Asset uploaded: {save_path}")
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
    asset_path = ASSETS_DIR / file_path
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
