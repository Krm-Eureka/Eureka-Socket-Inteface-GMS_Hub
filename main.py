import uvicorn
import socketio
import asyncio
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from contextlib import asynccontextmanager
from loguru import logger

_base_dir = os.environ.get("ESIG_BASE_DIR", ".")
_log_dir = os.path.join(_base_dir, "logs")

# Ensure logs directory exists
if not os.path.exists(_log_dir):
    os.makedirs(_log_dir)

from app.core.config import settings
from app.services.gms_client import GMSClient
from app.services.mock_gms_client import MockGMSClient
from app.behaviors.polling_manager import PollingManager
from app.behaviors.system_monitor import SystemMonitor
from app.api.v1.gms_router import router as gms_router
from app.api.v1.ui_router import router as ui_router

# --- Server Orchestration ---
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# ─── Socket.IO Rooms ───────────────────────────────────────────────────────────
# Clients are placed in page-specific rooms so heavy GMS messages (LocationListMsg,
# RobotInfoMsg) are only broadcast to clients who are actually viewing the Map.
# All other messages continue to broadcast globally.
PAGE_ROOMS = {"map", "taskmonitoring", "containers", "workflows", "dashboard"}
MAP_ONLY_EVENTS = {"gms:data:LocationListMsg", "gms:data:RobotInfoMsg"}
if settings.MOCK_MODE:
    logger.warning(">>> RUNNING IN MOCK MODE <<<")
    gms_client = MockGMSClient(sio)
else:
    gms_client = GMSClient(sio)

polling_manager = PollingManager(gms_client)
system_monitor = SystemMonitor(sio, gms_client)


# Configure Loguru to write to file
def _week_log_dir() -> str:
    """Return (and create) a weekly subdirectory: logs/YYYY-WXX/"""
    import datetime as _dt

    iso = _dt.datetime.now().isocalendar()  # (year, week, weekday)
    week_folder = os.path.join(_log_dir, f"{iso[0]}-W{iso[1]:02d}")
    os.makedirs(week_folder, exist_ok=True)
    return week_folder


def _cleanup_old_logs(retention_days: int = 90):
    """Delete weekly log sub-folders older than retention_days (default 3 months)."""
    import datetime as _dt

    cutoff = _dt.datetime.now() - _dt.timedelta(days=retention_days)
    if not os.path.isdir(_log_dir):
        return
    for entry in os.scandir(_log_dir):
        if entry.is_dir():
            try:
                mtime = _dt.datetime.fromtimestamp(entry.stat().st_mtime)
                if mtime < cutoff:
                    import shutil

                    shutil.rmtree(entry.path, ignore_errors=True)
                    logger.info(f"[LOG CLEANUP] Deleted old log folder: {entry.name}")
            except Exception as e:
                logger.warning(
                    f"[LOG CLEANUP] Could not check/delete {entry.path}: {e}"
                )


def init_logging():
    # 0. Clear all previous handlers to prevent duplicates on reload
    logger.remove()

    # Add back the standard terminal sink (sys.stderr)
    import sys

    logger.add(sys.stderr, level=settings.LOG_LEVEL)

    week_dir = _week_log_dir()

    # 1. Main Server Log — daily rotation into weekly subfolder
    logger.add(
        os.path.join(week_dir, "server_{time:YYYY-MM-DD}.log"),
        rotation="00:00",  # Rotate at midnight
        retention=None,  # Retention managed by _cleanup_old_logs
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        filter=lambda record: "app.services.gms_client" not in record["name"]
        and "app.behaviors.polling_manager" not in record["name"],
        enqueue=True,  # Thread-safe
    )

    # 2. Service Log (GMS Client & Polling) — daily rotation into weekly subfolder
    logger.add(
        os.path.join(week_dir, "service_{time:YYYY-MM-DD}.log"),
        rotation="00:00",  # Rotate at midnight
        retention=None,  # Retention managed by _cleanup_old_logs
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        filter=lambda record: "app.services" in record["name"]
        or "app.behaviors.polling_manager" in record["name"],
        enqueue=True,  # Thread-safe
    )

    # 3. Auto-cleanup: delete log folders older than 3 months
    try:
        _cleanup_old_logs(retention_days=90)
    except Exception as e:
        logger.warning(f"[LOG CLEANUP] Startup cleanup warning: {e}")


async def startup_diagnostics(app):
    """ตรวจสอบและ log สถานะการเชื่อมต่อทั้งหมดตอน startup"""
    import socket as _socket
    import pymysql

    # ─── Mandatory Config Validation ────────────────────────────────────────
    missing = []
    if not settings.GMS_IP:
        missing.append("GMS_IP")
    if not settings.GMS_CLIENT_CODE:
        missing.append("GMS_CLIENT_CODE")
    if missing:
        raise RuntimeError(
            f"❌ ESIG CANNOT START — Required .env values missing: {', '.join(missing)}\n"
            f"   กรุณาตั้งค่าใน ESIG/.env แล้วรัน ESIG ใหม่"
        )

    # ─── Banner ─────────────────────────────────────────────────────────────
    logger.info("=" * 62)
    logger.info(f"   ESIG HUB {app.version}  —  Startup Diagnostics")
    logger.info("=" * 62)
    logger.info(f"   MODE      : {'🔵 MOCK' if settings.MOCK_MODE else '🟢 LIVE'}")
    logger.info(
        f"   GMS       : {settings.GMS_IP}:{settings.GMS_PORT}  (CLIENT={settings.GMS_CLIENT_CODE})"
    )
    logger.info(
        f"   DB        : {settings.DB_HOST}:{settings.DB_PORT} / db='{settings.DB_NAME}'"
    )
    logger.info(f"   LOG LEVEL : {settings.LOG_LEVEL}")
    logger.info("-" * 62)

    # ─── Check 1: MySQL ─────────────────────────────────────────────────────
    if not settings.DB_NAME or settings.DB_PASS in ("", "your_password_here"):
        logger.warning(
            "   [DB]  ⚠️  MySQL SKIPPED    → DB_NAME หรือ DB_PASS ยังไม่ได้ตั้งค่าใน .env"
        )
    else:
        try:
            conn = pymysql.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASS,
                database=settings.DB_NAME,
                connect_timeout=3,
            )
            conn.close()
            logger.success(
                f"   [DB]  ✅ MySQL OK        → {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
            )
        except Exception as e:
            logger.error(f"   [DB]  ❌ MySQL FAILED    → {e}")

    # ─── Check 2: GMS TCP Reachability ──────────────────────────────────────
    if settings.MOCK_MODE:
        logger.info("   [GMS] 🔵 MOCK MODE       → ข้ามการตรวจสอบ GMS")
    else:
        try:
            s = _socket.create_connection(
                (settings.GMS_IP, settings.GMS_PORT), timeout=2
            )
            s.close()
            logger.success(
                f"   [GMS] ✅ GMS Reachable  → {settings.GMS_IP}:{settings.GMS_PORT}"
            )
        except Exception as e:
            logger.warning(f"   [GMS] ⚠️  GMS Unreachable → {e}")
            logger.warning("           (ปกติ — GMS จะเชื่อมต่อเมื่อกด START SERVICE)")

    logger.info("=" * 62)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Standard Startup Behavior
    init_logging()
    gms_client.set_monitor(system_monitor)  # Wire monitor for daily reset summary

    await startup_diagnostics(app)

    logger.info("ESIG HUB Initializing: Establishing GMS Polling Behavior...")
    gms_client.set_callbacks(on_message=polling_manager.handle_gms_message)

    # Async Start
    await polling_manager.start_service()
    await system_monitor.start()

    try:
        yield
    finally:
        # Async Stop
        logger.info("ESIG HUB Shutting Down: Cleaning up sessions...")
        await polling_manager.stop_service()
        await system_monitor.stop()


# --- FastAPI Initialization ---
app = FastAPI(
    title="ESIG HUB - EA Socket Interface GMS Hub", version="3.0.0", lifespan=lifespan
)
app.state.sio = sio

# Static & Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In production, this should be specific IPs/Domains
)

# Use absolute paths for static and templates to be robust in IIS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Check if ui_assets exists alongside static (typical for PyInstaller internal output)
ui_assets_path = os.path.join(BASE_DIR, "ui_assets")
if not os.path.exists(ui_assets_path):
    # Fallback for development: it's inside static
    ui_assets_path = os.path.join(BASE_DIR, "static", "ui_assets")

# NOTE: /api/v1/ui/assets is intentionally NOT mounted as StaticFiles here.
# The serve_asset() route in ui_router.py handles asset serving with proper 404
# validation. Having both a StaticFiles mount AND a router handler on the same
# prefix causes the router handler to be silently bypassed (mount takes priority in FastAPI).
app.mount(
    "/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static"
)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Mount API Modules
app.include_router(gms_router)
app.include_router(ui_router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(BASE_DIR, "static", "images", "esig_hub.png"))


@app.get("/.well-known/{path:path}", include_in_schema=False)
async def well_known(path: str):
    return {"message": "Discovery not implemented"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", tags=["Diagnostic"])
async def health_check():
    return {"status": "ok", "service": "ESIG HUB"}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="ESIG HUB - Swagger UI",
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
    )


# --- Socket.IO Event Handlers ---
@sio.event
async def connect(sid, environ):
    logger.info(f"Socket Client Connected: {sid}")
    # Extract IP
    client_ip = environ.get("REMOTE_ADDR", "Unknown")
    # WSGI/ASGI specific headers might store it elsewhere, but this is standard
    if "asgi.scope" in environ:
        client = environ["asgi.scope"].get("client")
        if client:
            client_ip = client[0]

    await system_monitor.add_client(sid, client_ip)
    # Default room: map (matches the app's default page)
    # set_active_page will move the client to the correct room once FE signals
    await sio.enter_room(sid, "page:map")
    await sio.emit(
        "status_update",
        {
            "status": "connected" if gms_client.is_connected() else "disconnected",
            "text": "Connected" if gms_client.is_connected() else "Disconnected",
        },
        to=sid,
    )


@sio.event
async def disconnect(sid):
    logger.info(f"Socket Client Disconnected: {sid}")
    system_monitor.remove_client(sid)
    await polling_manager.remove_client(sid)  # Clean up page watchers on disconnect


@sio.event
async def client_command(sid, data):
    """
    Handle commands from Frontend via Socket instead of HTTP
    """
    try:
        msg_type = data.get("msgType")
        body = data.get("body", {})
        client_code = settings.GMS_CLIENT_CODE
        channel_id = settings.GMS_CHANNEL_ID

        if not gms_client.is_connected():
            await sio.emit(
                "command_ack",
                {
                    "status": "error",
                    "code": "503",
                    "message": "GMS Disconnected",
                    "reqId": data.get("reqId"),
                },
                to=sid,
            )
            return

        # Forward to GMS
        success = await gms_client.send_request(msg_type, client_code, channel_id, body)

        # Ack back to requester
        await sio.emit(
            "command_ack",
            {
                "status": "queued" if success else "error",
                "message": "Sent to GMS" if success else "Socket Send Failed",
                "reqId": data.get("reqId"),
                "msgType": msg_type,
            },
            to=sid,
        )

    except Exception as e:
        logger.error(f"Socket Command Error: {e}")
        await sio.emit(
            "command_ack",
            {
                "status": "error",
                "message": str(e),
                "reqId": data.get("reqId"),
            },
            to=sid,
        )


@sio.on("get_tasks_page")
async def handle_get_tasks_page(sid, data):
    """
    Handle paginated task requests from Frontend
    Data should include: { "page": 1, "pageSize": 20 }
    """
    try:

        start_time = data.get("startTime")
        end_time = data.get("endTime")

        result = await polling_manager.get_task_cache(start_time, end_time)

        result["last_update_ts"] = polling_manager._last_task_update_ts
        await sio.emit("tasks_page_response", result, to=sid)
        logger.debug(
            f"Sent {len(result['tasks'])} tasks (7-day history) to client {sid}"
        )

    except Exception as e:
        logger.error(f"Error handling get_tasks_page: {e}")
        await sio.emit(
            "tasks_page_response",
            {"status": "error", "message": str(e), "tasks": [], "totalCount": 0},
            to=sid,
        )


@sio.on("refresh_data")
async def handle_refresh_data(sid, data):
    """Handle on-demand data refresh (e.g. UI navigation triggers)"""
    try:
        msg_type = data.get("msgType")
        body = data.get("body") or {}
        if not msg_type:
            return

        logger.info(f"UI ({sid}) requested on-demand refresh for: {msg_type}")
        if not gms_client.is_connected():
            return

        # Forward to GMS with potential dates/filters from UI
        await gms_client.send_request(
            msg_type, settings.GMS_CLIENT_CODE, settings.GMS_CHANNEL_ID, body
        )
    except Exception as e:
        logger.error(f"Refresh Data Error: {e}")


@sio.on("set_active_page")
async def handle_set_active_page(sid, data):
    """Handle page navigation signals — move client to the correct Socket.IO room
    so map-only events (LocationListMsg, RobotInfoMsg) don't spam other pages."""
    try:
        page = data.get("page", "")
        logger.info(f"Client {sid} entered page: {page}")

        # Move client to the correct page room
        for room in PAGE_ROOMS:
            await sio.leave_room(sid, f"page:{room}")
        if page in PAGE_ROOMS:
            await sio.enter_room(sid, f"page:{page}")

        # Diagnostic: verify room membership
        rooms = sio.rooms(sid)
        logger.info(f"Client {sid} room state: {rooms}")

        await polling_manager.set_client_page(sid, page)
    except Exception as e:
        logger.error(f"Set Active Page Error: {e}")


@sio.on("join_admin")
async def handle_join_admin(sid, data=None):
    """Admin clients (ESIG Dashboard) call this to receive debug logs and pending status."""
    logger.info(f"Client {sid} joined admin room")
    await sio.enter_room(sid, "room:admin")


# Unified ASGI App
socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    logger.info(
        f"Launching Enterprise Server on {settings.BFF_HOST}:{settings.BFF_PORT}"
    )
    # Diagnostic: Print all registered routes
    logger.info("Registered Routes:")
    for route in app.routes:
        logger.info(f" -> {route.path} {getattr(route, 'methods', None)}")

    uvicorn.run(
        "main:socket_app",
        host=settings.BFF_HOST,
        port=settings.BFF_PORT,
        reload=settings.BFF_RELOAD,
    )
