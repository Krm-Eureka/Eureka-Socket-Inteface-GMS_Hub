import json
import time
import datetime
import asyncio
from typing import Dict, Optional, Callable, Any, Union, List
from loguru import logger
from app.core.config import settings
from app.core.constants import AppStatus, AppErrorCode
from app.services.log_service import write_debug_log as _log_debug


class GMSClient:
    """[SERVICE] Low-level Async Socket handler for GMS"""

    def __init__(self, sio):
        self._sio = sio
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock: Optional[asyncio.Lock] = None
        self._loop = None
        self._on_message_callback: Optional[Callable] = None
        self._on_status_callback: Optional[Callable] = None

        self.gms_ip = settings.GMS_IP
        self.gms_port = settings.GMS_PORT
        self.stats = {"rx": 0, "tx": 0}
        self.gms_stats = {
            "latency_ms": 0,
            "total_errors": 0,
            "rx_types": {},  # {msgType: count}
            "tx_types": {},  # {msgType: count}
            "last_activity": None,
        }
        self.last_rx_time = time.time()
        self.pending_requests = set()  # Track in-flight request types
        self._pending_times: Dict[str, float] = {}  # msgType → time.time() ตอนส่ง
        self._monitor = None  # Injected via set_monitor() after construction

        # ─── Socket.IO Room Routing ─────────────────────────────────────────────
        self._map_only_events = {
            "gms:data:LocationListMsg",
            "gms:data:RobotInfoMsg",
        }
        self._reset_task: Optional[asyncio.Task] = None

    def start_background_tasks(self):
        """Schedule daily counter reset."""
        if not self._reset_task:
            self._reset_task = asyncio.create_task(self._midnight_reset_loop())

    async def _midnight_reset_loop(self):
        """Async loop to reset RX/TX counters at midnight every day."""
        while True:
            try:
                now = datetime.datetime.now()
                next_midnight = (now + datetime.timedelta(days=1)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                sleep_secs = (next_midnight - now).total_seconds()
                await asyncio.sleep(sleep_secs)

                old_rx, old_tx = self.stats["rx"], self.stats["tx"]
                self.stats = {"rx": 0, "tx": 0}

                summary = self._monitor.get_daily_summary() if self._monitor else {}
                if self._monitor:
                    self._monitor.reset_daily_stats()

                log_msg = (
                    f"[DAILY RESET — {now.strftime('%Y-%m-%d')}]\n"
                    f"  GMS Counter  : RX={old_rx}  TX={old_tx}\n"
                )
                if summary:
                    log_msg += (
                        f"  CPU          : min={summary['cpu_min']}%  max={summary['cpu_max']}%  avg={summary['cpu_avg']}%\n"
                        f"  RAM          : min={summary['ram_min']}%  max={summary['ram_max']}%  avg={summary['ram_avg']}%\n"
                        f"  DB Latency   : min={summary['db_latency_min']}ms  max={summary['db_latency_max']}ms\n"
                        f"  DB QPS (max) : {summary['qps_max']}\n"
                        f"  DB Errors    : {summary['db_errors']}\n"
                        f"  Samples      : {summary['samples']}"
                    )

                logger.info(log_msg)
                await self.emit_log("SYS", "DAILY_RESET", {"report": log_msg})
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Midnight reset loop error: {e}")
                await asyncio.sleep(60)

    def set_loop(self, loop):
        self._loop = loop

    def set_monitor(self, monitor):
        self._monitor = monitor

    def set_callbacks(self, on_message=None, on_status=None):
        self._on_message_callback = on_message
        self._on_status_callback = on_status

    def is_connected(self) -> bool:
        return self._writer is not None

    async def connect(self):
        if self._lock is None:
            self._lock = asyncio.Lock()

        async with self._lock:
            try:
                await self._broadcast_status(
                    AppStatus.CONNECTING, f"Connecting to {self.gms_ip}..."
                )
                await self.emit_log(
                    "SYS", "CONNECTING", f"Attempting to connect to {self.gms_ip}..."
                )
                
                self._reader, self._writer = await asyncio.wait_for(
                    asyncio.open_connection(
                        self.gms_ip, 
                        self.gms_port,
                        limit=64 * 1024 * 1024  # 64MB — รองรับ GMS messages ขนาดใหญ่ (LocationList, WorkflowInstanceList)
                    ),
                    timeout=15.0
                )
                
                logger.success(f"Connected to GMS at {self.gms_ip}:{self.gms_port}")
                self.last_rx_time = time.time()
                await self._broadcast_status(AppStatus.CONNECTED, "Connected")
                return True
            except asyncio.TimeoutError:
                logger.error(f"Connect timed out (15s) for GMS at {self.gms_ip}:{self.gms_port}")
                await self.emit_log("SYS", "ERROR", "Connection timed out (15s)")
                return False
            except Exception as e:
                error_msg = str(e) or "Unknown Error"
                logger.error(f"Connect failed: {error_msg}")
                await self.emit_log("SYS", "ERROR", f"Connection failed: {error_msg}")
                await self._broadcast_status(AppStatus.DISCONNECTED, error_msg)
                await self.emit_error(AppErrorCode.SOCKET_ERROR, error_msg)
                return False

    async def disconnect(self):
        async with self._lock:
            if self._writer:
                try:
                    self._writer.close()
                    await self._writer.wait_closed()
                except:
                    pass
                self._reader = None
                self._writer = None
                self.pending_requests.clear()
                await self._emit_pending()
                await self._broadcast_status(AppStatus.DISCONNECTED, "Disconnected")

    async def read_loop(self, running_flag_func):
        logger.info(f"Read Loop Started (Source: {self.gms_ip})")
        while running_flag_func() and self._reader:
            try:
                line = await self._reader.readline()
                if not line:
                    logger.warning("Read Loop: Connection closed by remote")
                    break

                # Low-level tracing
                try:
                    raw_str = line.decode("utf-8", errors="replace").strip()
                    if raw_str:
                        logger.debug(f"📥 [RAW RX] {raw_str}")
                except:
                    logger.debug(f"📥 [RAW RX] {line}")

                if line.strip():
                    await self._handle_raw_message(line)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Read Loop Error: {e}")
                break
        logger.info("Read Loop Ended")
        await self.disconnect()

    async def _handle_raw_message(self, raw_bytes):
        self.last_rx_time = time.time()
        msg_type = "Unknown"
        byte_size = len(raw_bytes)
        size_kb = byte_size / 1024
        size_mb = byte_size / (1024 * 1024)
        size_label = f"{size_mb:.3f} MB" if size_mb >= 0.1 else f"{size_kb:.1f} KB"
        try:
            msg_str = raw_bytes.decode("utf-8")
            data = json.loads(msg_str)
            self.stats["rx"] += 1

            if not isinstance(data, dict):
                return

            header = data.get("header", {})
            body = data.get("body", {})
            msg_type = header.get("msgType") if isinstance(header, dict) else None
            if not msg_type and isinstance(body, dict):
                msg_type = body.get("msgType")

            if not msg_type:
                id_val = header.get("responseId") or header.get("requestId") if isinstance(header, dict) else None
                if id_val and "_" in str(id_val):
                    msg_type = str(id_val).split("_")[-1]

            msg_type = msg_type or "Unknown"

            if msg_type in self.pending_requests:
                self.pending_requests.remove(msg_type)
                await self._emit_pending()

            await self.emit_log("RX", msg_type, data)

            sent_at = self._pending_times.pop(msg_type, None)
            elapsed_ms = round((time.time() - sent_at) * 1000) if sent_at else None
            _log_debug("RX", msg_type, body, elapsed_ms=elapsed_ms, size_bytes=byte_size)

            self.gms_stats["last_activity"] = datetime.datetime.now().strftime("%H:%M:%S")
            self.gms_stats["rx_types"][msg_type] = self.gms_stats["rx_types"].get(msg_type, 0) + 1

            if isinstance(header, dict) and "responseId" in header:
                try:
                    res_id = header["responseId"]
                    parts = res_id.split("_")
                    if len(parts) >= 2 and parts[0] == "req":
                        sent_time = int(parts[1][:10])
                        self.gms_stats["latency_ms"] = int((time.time() - sent_time) * 1000)
                except:
                    pass

            event_name = f"gms:data:{msg_type}"
            await self.emit_socket(event_name, data)

            if self._on_message_callback:
                if asyncio.iscoroutinefunction(self._on_message_callback):
                    await self._on_message_callback(data)
                else:
                    self._on_message_callback(data)

        except json.JSONDecodeError:
            await self.emit_error(AppErrorCode.INVALID_JSON, "Malformed JSON from GMS")
        except Exception as e:
            logger.error(f"Error handling message ({msg_type}): {e}")
            if msg_type in self.pending_requests:
                self.pending_requests.remove(msg_type)
            await self.emit_error(AppErrorCode.INTERNAL_ERROR, str(e))

    async def send_request(self, msg_type: str, client_code: str, channel_id: str, body: Dict) -> bool:
        unique_id = int(time.time() * 1000) % 1000000
        req_id = f"req_{int(time.time())}{unique_id}_{msg_type}"
        if "msgType" not in body:
            body["msgType"] = msg_type

        if msg_type == "WorkflowInstanceListMsg":
            if "startTime" not in body or "endTime" not in body:
                today_dt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                body["startTime"] = (today_dt - datetime.timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
                body["endTime"] = (today_dt + datetime.timedelta(days=1)).strftime("%Y-%m-%d 23:59:59")

        req_data = {
            "header": {
                "requestId": req_id,
                "msgType": msg_type,
                "channelId": channel_id,
                "clientCode": client_code,
                "requestTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            "body": body,
        }

        if await self.send_raw(req_data):
            self.pending_requests.add(msg_type)
            self._pending_times[msg_type] = time.time()
            await self._emit_pending()

            self.gms_stats["tx_types"][msg_type] = self.gms_stats["tx_types"].get(msg_type, 0) + 1
            self.gms_stats["last_activity"] = datetime.datetime.now().strftime("%H:%M:%S")

            logger.debug(f"📤 [SEND] {msg_type} -> ID: {req_id}")
            await self.emit_log("TX", msg_type, req_data)
            _log_debug("TX", msg_type, body, elapsed_ms=None)
            return True
        return False

    async def send_raw(self, data_dict: Dict) -> bool:
        try:
            json_str = json.dumps(data_dict) + "\r\n"
            async with self._lock:
                if self._writer:
                    self._writer.write(json_str.encode("utf-8"))
                    await self._writer.drain()
                    self.stats["tx"] += 1
                    return True
        except Exception as e:
            self.gms_stats["total_errors"] += 1
            logger.error(f"Send Failed: {e}")
            await self.emit_error(AppErrorCode.SOCKET_ERROR, str(e))
        return False

    async def _broadcast_status(self, status: str, text: str):
        await self.emit_socket("status_update", {"status": status, "text": text})
        if self._on_status_callback:
            if asyncio.iscoroutinefunction(self._on_status_callback):
                await self._on_status_callback(status, text)
            else:
                self._on_status_callback(status, text)

    async def emit_log(self, direction: str, msg_type: str, payload: Dict):
        body = payload.get("body", payload) if isinstance(payload, dict) else payload
        if isinstance(body, list) and len(body) > 20:
            display_payload = {
                **{k: v for k, v in payload.items() if k != "body"},
                "body": f"[{len(body)} items — Use TASKS tab for details]",
            }
        else:
            display_payload = payload

        await self.emit_socket(
            "log",
            {
                "direction": direction,
                "msgType": msg_type,
                "payload": display_payload,
                "stats": self.stats.copy(),
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
            },
        )

    async def emit_error(self, code: str, message: str):
        await self.emit_socket(
            "gms:error",
            {
                "code": code,
                "message": message,
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
            },
        )

    async def emit_socket(self, event: str, data: Any, room: Optional[str] = None):
        try:
            target_room = room or ("page:map" if event in self._map_only_events else None)
            if target_room:
                await self._sio.emit(event, data, room=target_room)
            else:
                await self._sio.emit(event, data)
        except Exception as e:
            logger.error(f"Socket Emit Failed ({event}): {e}")

    async def refresh_pending_ui(self):
        await self._emit_pending()

    async def _emit_pending(self):
        now = time.time()
        formatted = []
        for msg_type in list(self.pending_requests):
            sent_at = self._pending_times.get(msg_type, now)
            elapsed = now - sent_at
            if elapsed < 1.0:
                ms = int(elapsed * 1000)
                formatted.append(f"{msg_type}__{ms}ms")
            else:
                s = round(float(elapsed), 1)
                formatted.append(f"{msg_type}__{s}s")

        def get_seconds(s):
            try:
                val_str = s.split("__")[-1]
                if val_str.endswith("ms"): 
                    return float(val_str[:-2]) / 1000
                if val_str.endswith("s"): 
                    return float(val_str[:-1])
            except: 
                pass
            return 0.0

        formatted.sort(key=get_seconds, reverse=True)
        await self.emit_socket("gms:pending", formatted)
