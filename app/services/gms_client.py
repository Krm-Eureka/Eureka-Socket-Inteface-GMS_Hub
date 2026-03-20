import socket
import threading
import json
import time
import datetime
import asyncio
from typing import Dict, Optional, Callable
from loguru import logger
from app.core.config import settings
from app.core.constants import AppStatus, AppErrorCode
from app.services.log_service import write_debug_log as _log_debug


class GMSClient:
    """[SERVICE] Low-level Socket handler for GMS"""

    def __init__(self, sio):
        self._sio = sio
        self._sock = None
        self._lock = threading.Lock()
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
        # Events listed here are sent ONLY to clients in the 'page:map' room,
        # avoiding unnecessary JS processing on Task/Container/other pages.
        self._map_only_events = {
            "gms:data:LocationListMsg",
            "gms:data:RobotInfoMsg",
        }
        self._start_midnight_reset()  # Schedule daily counter reset at 00:00

    def _start_midnight_reset(self):
        """Start a background thread to reset RX/TX counters at midnight every day."""

        def _reset_loop():
            while True:
                try:
                    now = datetime.datetime.now()
                    # Calculate seconds until next midnight
                    next_midnight = (now + datetime.timedelta(days=1)).replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    sleep_secs = (next_midnight - now).total_seconds()
                    time.sleep(sleep_secs)

                    old_rx, old_tx = self.stats["rx"], self.stats["tx"]
                    self.stats = {"rx": 0, "tx": 0}

                    # Build daily summary from system monitor if available
                    summary = {}
                    if self._monitor:
                        summary = self._monitor.get_daily_summary()
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
                    self.emit_log("SYS", "DAILY_RESET", {"report": log_msg})
                except Exception as e:
                    logger.error(f"Midnight reset loop error: {e}")
                    time.sleep(
                        60
                    )  # Wait 1 minute before retrying on error to avoid CPU spike

        t = threading.Thread(target=_reset_loop, daemon=True, name="midnight-reset")
        t.start()

    def set_loop(self, loop):
        self._loop = loop

    def set_monitor(self, monitor):
        """Wire in a SystemMonitor instance for daily summary at midnight."""
        self._monitor = monitor

    def set_callbacks(self, on_message=None, on_status=None):
        self._on_message_callback = on_message
        self._on_status_callback = on_status

    def is_connected(self) -> bool:
        return self._sock is not None

    def connect(self):
        with self._lock:
            try:
                self._broadcast_status(
                    AppStatus.CONNECTING, f"Connecting to {self.gms_ip}..."
                )
                self.emit_log(
                    "SYS", "CONNECTING", f"Attempting to connect to {self.gms_ip}..."
                )
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.settimeout(1.0)  # 1 second timeout for faster failure
                self._sock.connect((self.gms_ip, self.gms_port))
                self._sock.settimeout(None)  # Reset to blocking for subsequent reads
                logger.success(f"Connected to GMS at {self.gms_ip}:{self.gms_port}")
                self.last_rx_time = time.time()  # Reset Watchdog on success
                self._broadcast_status(AppStatus.CONNECTED, "Connected")
                return self._sock
            except Exception as e:
                logger.error(f"Connect failed: {e}")
                self.emit_log("SYS", "ERROR", f"Connection failed: {e}")
                self._broadcast_status(AppStatus.DISCONNECTED, str(e))
                self.emit_error(AppErrorCode.SOCKET_ERROR, str(e))
                return None

    def disconnect(self):
        with self._lock:
            if self._sock:
                try:
                    self._sock.close()
                except:
                    pass
                self._sock = None
                self.pending_requests.clear()  # Clear pending on disconnect
                self._emit_pending()
                self._broadcast_status(AppStatus.DISCONNECTED, "Disconnected")

    def read_loop(self, running_flag_func):
        buffer = b""
        logger.info(f"Read Loop Started (Source: {self.gms_ip})")
        while running_flag_func() and self._sock:
            try:
                data = self._sock.recv(4096)
                if not data:
                    logger.warning("Read Loop: Connection closed by remote")
                    break

                # Low-level tracing
                try:
                    raw_str = data.decode("utf-8", errors="replace").strip()
                    logger.debug(f"📥 [RAW RX] {raw_str}")
                except:
                    logger.debug(f"📥 [RAW RX] {data}")

                buffer += data
                while b"\r\n" in buffer:
                    line, buffer = buffer.split(b"\r\n", 1)
                    if line.strip():
                        self._handle_raw_message(line)
            except OSError:
                break
            except Exception as e:
                logger.error(f"Read Loop Error: {e}")
                break
        logger.info("Read Loop Ended")

    def _handle_raw_message(self, raw_bytes):
        # Update Watchdog on any byte received
        self.last_rx_time = time.time()

        msg_type = "Unknown"
        try:
            msg_str = raw_bytes.decode("utf-8")
            data = json.loads(msg_str)
            self.stats["rx"] += 1

            if not isinstance(data, dict):
                logger.warning(f"Unexpected JSON type from GMS: {type(data)}")
                return

            # Extract msgType for specific events
            header = data.get("header", {})
            body = data.get("body", {})

            # Robust msgType extraction
            msg_type = header.get("msgType") if isinstance(header, dict) else None
            if not msg_type and isinstance(body, dict):
                msg_type = body.get("msgType")

            if not msg_type:
                # Fallback to ID suffix (e.g. req_123_HeartbeatMsg)
                id_val = None
                if isinstance(header, dict):
                    id_val = header.get("responseId") or header.get("requestId")

                if id_val and "_" in str(id_val):
                    msg_type = str(id_val).split("_")[-1]

            msg_type = msg_type or "Unknown"

            # 1. Clear from pending requests as soon as we identify the type
            if msg_type in self.pending_requests:
                self.pending_requests.remove(msg_type)
                self._emit_pending()

            # 2. Log Event (Generic)
            self.emit_log("RX", msg_type, data)

            # 📝 Debug Log: RX (with RTT and body preview ≤ 5 items)
            sent_at = self._pending_times.pop(msg_type, None)
            elapsed_ms = round((time.time() - sent_at) * 1000) if sent_at else None
            self._write_debug_log("RX", msg_type, body, elapsed_ms=elapsed_ms)

            # Update Diagnostics
            self.gms_stats["last_activity"] = datetime.datetime.now().strftime(
                "%H:%M:%S"
            )
            self.gms_stats["rx_types"][msg_type] = (
                self.gms_stats["rx_types"].get(msg_type, 0) + 1
            )

            # RTT Calculation
            if isinstance(header, dict) and "responseId" in header:
                try:
                    res_id = header["responseId"]
                    # req_123456789_MsgType
                    parts = res_id.split("_")
                    if len(parts) >= 2 and parts[0] == "req":
                        sent_time = int(parts[1][:10])
                        self.gms_stats["latency_ms"] = int(
                            (time.time() - sent_time) * 1000
                        )
                except:
                    pass

            # 3. Specific Data Event (For easier FE integration)
            event_name = f"gms:data:{msg_type}"
            logger.debug(f"📡 [EMIT] {event_name}")
            self.emit_socket(event_name, data)

            if self._on_message_callback:
                self._on_message_callback(data)

        except json.JSONDecodeError:
            self.emit_error(AppErrorCode.INVALID_JSON, "Malformed JSON from GMS")
        except Exception as e:
            logger.error(f"Error handling message ({msg_type}): {e}")
            # Ensure it's cleared even on error if we know the type
            if msg_type in self.pending_requests:
                self.pending_requests.remove(msg_type)
            self.emit_error(AppErrorCode.INTERNAL_ERROR, str(e))

    def send_request(
        self, msg_type: str, client_code: str, channel_id: str, body: Dict
    ) -> bool:
        # High-precision unique ID
        unique_id = int(time.time() * 1000) % 1000000
        req_id = f"req_{int(time.time())}{unique_id}_{msg_type}"
        if "msgType" not in body:
            body["msgType"] = msg_type

        # Safety Guard: Ensure startTime/endTime for WorkflowInstanceListMsg
        if msg_type == "WorkflowInstanceListMsg":
            if "startTime" not in body or "endTime" not in body:
                today_dt = datetime.datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                start_dt = today_dt - datetime.timedelta(days=7)
                end_dt = today_dt + datetime.timedelta(days=1)

                if "startTime" not in body:
                    body["startTime"] = start_dt.strftime("%Y-%m-%d 00:00:00")
                if "endTime" not in body:
                    body["endTime"] = end_dt.strftime("%Y-%m-%d 23:59:59")

                logger.debug(
                    f"Injected missing dates for WorkflowInstanceListMsg: {body['startTime']} to {body['endTime']}"
                )

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

        if self.send_raw(req_data):
            # Mark as pending + record send time for RTT
            self.pending_requests.add(msg_type)
            self._pending_times[msg_type] = time.time()  # บันทึกเวลาส่ง
            self._emit_pending()

            # Update Diagnostics
            self.gms_stats["tx_types"][msg_type] = (
                self.gms_stats["tx_types"].get(msg_type, 0) + 1
            )
            self.gms_stats["last_activity"] = datetime.datetime.now().strftime(
                "%H:%M:%S"
            )

            logger.debug(f"📤 [SEND] {msg_type} -> ID: {req_id}")
            self.emit_log("TX", msg_type, req_data)
            # 📝 Debug Log: TX
            self._write_debug_log("TX", msg_type, body, elapsed_ms=None)
            return True
        return False

    def send_raw(self, data_dict: Dict) -> bool:
        try:
            json_str = json.dumps(data_dict) + "\r\n"
            with self._lock:
                if self._sock:
                    self._sock.sendall(json_str.encode("utf-8"))
                    self.stats["tx"] += 1
                    return True
        except Exception as e:
            self.gms_stats["total_errors"] += 1
            logger.error(f"Send Failed: {e}")
            self.emit_error(AppErrorCode.SOCKET_ERROR, str(e))
        return False

    def _broadcast_status(self, status: str, text: str):
        self.emit_socket("status_update", {"status": status, "text": text})
        if self._on_status_callback:
            self._on_status_callback(status, text)

    def emit_log(self, direction: str, msg_type: str, payload: Dict):
        # Truncate large list payloads to avoid flooding Socket.IO
        body = payload.get("body", payload) if isinstance(payload, dict) else payload
        # Increase visibility for moderately sized lists
        if isinstance(body, list) and len(body) > 20:
            display_payload = {
                **{k: v for k, v in payload.items() if k != "body"},
                "body": f"[{len(body)} items — Use TASKS tab for details]",
            }
        else:
            display_payload = payload

        self.emit_socket(
            "log",
            {
                "direction": direction,
                "msgType": msg_type,
                "payload": display_payload,
                "stats": self.stats.copy(),
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
            },
        )

    def _write_debug_log(self, direction: str, msg_type: str, body, elapsed_ms):
        """Delegate to log_service — keeps gms_client clean."""
        _log_debug(direction, msg_type, body, elapsed_ms)

    def emit_error(self, code: str, message: str):
        self.emit_socket(
            "gms:error",
            {
                "code": code,
                "message": message,
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
            },
        )

    def emit_socket(self, event: str, data: Dict, room: str = None):
        if not self._loop:
            return
        try:
            # Route map-only events to page:map room to avoid spamming other pages
            target_room = room or (
                "page:map" if event in self._map_only_events else None
            )
            if target_room:
                logger.debug(f"📤 [SOCKET] Emitting {event} → room={target_room}")
                coro = self._sio.emit(event, data, room=target_room)
            else:
                logger.debug(f"📤 [SOCKET] Emitting {event} → all")
                coro = self._sio.emit(event, data)
            asyncio.run_coroutine_threadsafe(coro, self._loop)
        except Exception as e:
            logger.error(f"Socket Emit Failed ({event}): {e}")

    def refresh_pending_ui(self):
        """Force a refresh of the pending requests UI (used by PollingManager)"""
        self._emit_pending()

    def _emit_pending(self):
        """Broadcast in-flight requests to UI with high-resolution wait timers"""
        now = time.time()
        formatted = []
        for msg_type in list(self.pending_requests):
            sent_at = self._pending_times.get(msg_type, now)
            elapsed = now - sent_at

            # Format: RobotInfoMsg__1.2s or RobotInfoMsg__450ms
            if elapsed < 1.0:
                ms = int(elapsed * 1000)
                formatted.append(f"{msg_type}__{ms}ms")
            else:
                s = round(elapsed, 1)
                formatted.append(f"{msg_type}__{s}s")

        # Sort by duration - longest wait times first
        def get_seconds(s):
            try:
                val_str = s.split("__")[-1]
                if val_str.endswith("ms"):
                    return float(val_str[:-2]) / 1000
                if val_str.endswith("s"):
                    return float(val_str[:-1])
            except:
                pass
            return 0

        formatted.sort(key=get_seconds, reverse=True)
        self.emit_socket("gms:pending", formatted)
