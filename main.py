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

# Ensure logs directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

from app.core.config import settings
from app.services.gms_client import GMSClient
from app.services.mock_gms_client import MockGMSClient
from app.behaviors.polling_manager import PollingManager
from app.behaviors.system_monitor import SystemMonitor
from app.api.v1.gms_router import router as gms_router

# --- Server Orchestration ---
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
if settings.MOCK_MODE:
    logger.warning(">>> RUNNING IN MOCK MODE <<<")
    gms_client = MockGMSClient(sio)
else:
    gms_client = GMSClient(sio)

polling_manager = PollingManager(gms_client)
system_monitor = SystemMonitor(sio, gms_client)


# Configure Loguru to write to file
def init_logging():
    # 0. Clear all previous handlers to prevent duplicates on reload
    logger.remove()

    # Add back the standard terminal sink (sys.stderr)
    import sys

    logger.add(sys.stderr, level=settings.LOG_LEVEL)

    # 1. Main Server Log (Exclude GMS Client & Polling Verbosity)
    logger.add(
        "logs/server_{time:YYYY-MM-DD}.log",
        rotation="30 minutes",
        retention="1 week",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        filter=lambda record: "app.services.gms_client" not in record["name"]
        and "app.behaviors.polling_manager" not in record["name"],
        enqueue=True,  # Thread-safe
    )

    # 2. Service Log (Only GMS Client & Polling)
    logger.add(
        "logs/service_{time:YYYY-MM-DD}.log",
        rotation="30 minutes",
        retention="1 week",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        filter=lambda record: "app.services" in record["name"]
        or "app.behaviors.polling_manager" in record["name"],
        enqueue=True,  # Thread-safe
    )


async def startup_diagnostics():
    """ตรวจสอบและ log สถานะการเชื่อมต่อทั้งหมดตอน startup"""
    import socket as _socket
    import pymysql

    # ─── Banner ─────────────────────────────────────────────────────────────
    logger.info("=" * 62)
    logger.info("   ESIG HUB v1.0.0  —  Startup Diagnostics")
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
    loop = asyncio.get_running_loop()
    gms_client.set_loop(loop)
    system_monitor.set_loop(loop)
    gms_client.set_monitor(system_monitor)  # Wire monitor for daily reset summary

    await startup_diagnostics()

    logger.info("ESIG HUB Initializing: Establishing GMS Polling Behavior...")
    gms_client.set_callbacks(on_message=polling_manager.handle_gms_message)
    polling_manager.start_service()
    system_monitor.start()

    try:
        yield
    finally:
        # Standard Shutdown Behavior (runs even on CancelledError / forced shutdown)
        logger.info("ESIG HUB Shutting Down: Cleaning up sessions...")
        polling_manager.stop_service()
        system_monitor.stop()


# --- FastAPI Initialization ---
app = FastAPI(
    title="ESIG HUB - EA Socket Interface GMS Hub", version="1.0.0", lifespan=lifespan
)

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
app.mount(
    "/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static"
)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Mount API Modules
app.include_router(gms_router)


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

    system_monitor.add_client(sid, client_ip)
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
    polling_manager.remove_client(sid)  # Clean up page watchers on disconnect


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
        success = gms_client.send_request(msg_type, client_code, channel_id, body)

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
        page = data.get("page", 1)
        page_size = data.get("pageSize", 80)
        start_time = data.get("startTime")
        end_time = data.get("endTime")

        result = polling_manager.get_paginated_tasks(
            page, page_size, start_time, end_time
        )

        await sio.emit("tasks_page_response", result, to=sid)
        logger.debug(
            f"Sent tasks page {page} ({len(result['tasks'])} items) to client {sid}"
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
        gms_client.send_request(
            msg_type, settings.GMS_CLIENT_CODE, settings.GMS_CHANNEL_ID, body
        )
    except Exception as e:
        logger.error(f"Refresh Data Error: {e}")


@sio.on("set_active_page")
async def handle_set_active_page(sid, data):
    """Handle page navigation signals for polling optimization (per-client)"""
    try:
        page = data.get("page", "")
        logger.info(f"Client {sid} entered page: {page}")
        polling_manager.set_client_page(sid, page)
    except Exception as e:
        logger.error(f"Set Active Page Error: {e}")


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
