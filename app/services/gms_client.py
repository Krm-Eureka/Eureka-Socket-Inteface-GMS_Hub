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
        self.last_rx_time = time.time()
        self.pending_requests = set()  # Track in-flight request types

    def set_loop(self, loop):
        self._loop = loop

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

        req_data = {
            "header": {
                "requestId": req_id,
                "channelId": channel_id,
                "clientCode": client_code,
                "requestTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            "body": body,
        }

        if self.send_raw(req_data):
            # Mark as pending
            self.pending_requests.add(msg_type)
            self._emit_pending()

            logger.debug(f"📤 [SEND] {msg_type} -> ID: {req_id}")
            self.emit_log("TX", msg_type, req_data)
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
        if isinstance(body, list) and len(body) > 3:
            display_payload = {
                **{k: v for k, v in payload.items() if k != "body"},
                "body": f"[{len(body)} items — truncated for display]",
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

    def emit_error(self, code: str, message: str):
        self.emit_socket(
            "gms:error",
            {
                "code": code,
                "message": message,
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
            },
        )

    def emit_socket(self, event: str, data: Dict):
        if not self._loop:
            return
        try:
            logger.debug(f"📤 [SOCKET] Emitting {event}")
            asyncio.run_coroutine_threadsafe(self._sio.emit(event, data), self._loop)
        except Exception as e:
            logger.error(f"Socket Emit Failed ({event}): {e}")

    def _emit_pending(self):
        """Broadcast in-flight requests to UI"""
        self.emit_socket("gms:pending", list(self.pending_requests))
