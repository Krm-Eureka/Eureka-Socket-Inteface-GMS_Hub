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
        # Always create fresh lock for the current event loop
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
                        limit=64
                        * 1024
                        * 1024,  # 64MB — รองรับ GMS messages ขนาดใหญ่ (LocationList, WorkflowInstanceList)
                    ),
                    timeout=15.0,
                )

                logger.success(f"Connected to GMS at {self.gms_ip}:{self.gms_port}")
                self.last_rx_time = time.time()
                await self._broadcast_status(AppStatus.CONNECTED, "Connected")
                return True
            except asyncio.TimeoutError:
                logger.error(
                    f"Connect timed out (15s) for GMS at {self.gms_ip}:{self.gms_port}"
                )
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
        if not self._lock:
            return
        async with self._lock:
            if self._writer:
                try:
                    self._writer.close()
                    await self._writer.wait_closed()
                except Exception as e:
                    logger.warning(f"[GMS] Socket close warning: {e}")
                self._reader = None
                self._writer = None
                self.pending_requests.clear()
                await self._emit_pending()
                await self._broadcast_status(AppStatus.DISCONNECTED, "Disconnected")

    async def read_loop(self, running_flag_func):
        logger.info(f"Read Loop Started (Source: {self.gms_ip})")
        buffer = bytearray()
        while running_flag_func() and self._reader:
            try:
                # 📦 Buffered Reading: Read large chunks (10MB) to prevent blocking the event loop
                raw_data = await self._reader.read(10 * 1024 * 1024)
                if not raw_data:
                    logger.warning("Read Loop: Connection closed by remote")
                    break

                self.last_rx_time = time.time()
                buffer.extend(raw_data)

                # Process all complete lines in the buffer
                while b"\n" in buffer:
                    line, rest = buffer.split(b"\n", 1)
                    buffer = rest
                    if line.strip():
                        # 📝 Step: Handle raw line
                        logger.debug(f"⚙️ [GMS] Parsing raw packet ({len(line)} bytes)")
                        await self._handle_raw_message(line)
                        await asyncio.sleep(0.001)

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
        try:
            # 🧵 Threaded Parsing for Large Messages (Prevent Event Loop Blocking)
            if byte_size > 100 * 1024:
                data = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: json.loads(raw_bytes.decode("utf-8"))
                )
            else:
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
                id_val = (
                    header.get("responseId") or header.get("requestId")
                    if isinstance(header, dict)
                    else None
                )
                if id_val and "_" in str(id_val):
                    msg_type = str(id_val).split("_")[-1]

            msg_type = msg_type or "Unknown"

            # ✅ [REFINED] Restore Pending Request Cleanup (Crucial for UI)
            # Differentiate tags for WorkflowInstanceListMsg (Rule 8 optimization)
            lock_key = msg_type
            if msg_type == "WorkflowInstanceListMsg" and header:
                id_val = header.get("responseId") or header.get("requestId")
                if id_val and "_" in str(id_val):
                    parts = str(id_val).split("_")
                    if len(parts) >= 4: # req, ts, tag, type
                        lock_key = f"{parts[2]}_{parts[3]}"
            
            if lock_key in self.pending_requests:
                self.pending_requests.remove(lock_key)
                await self._emit_pending()

            # 📊 Log RECV (Optimized format)
            size_str = (
                f"{byte_size/1024:.2f} KB"
                if byte_size < 1024 * 1024
                else f"{byte_size/(1024*1024):.2f} MB"
            )
            logger.info(f"📥 [GMS] RX Response: {msg_type} ({size_str})")

            await self.emit_log("RX", msg_type, data, size_str=size_str)

            sent_at = self._pending_times.pop(lock_key, None)
            elapsed_ms = round((time.time() - sent_at) * 1000) if sent_at else None
            _log_debug(
                "RX", msg_type, body, elapsed_ms=elapsed_ms, size_bytes=byte_size
            )

            # --- 🛡️ DEBUG: Sample RobotInfoMsg Structure ---
            if msg_type == "RobotInfoMsg":
                logger.debug(f"🔍 [DEBUG] RobotInfoMsg Sample: {str(body)[:500]}")
            
            self.gms_stats["last_activity"] = datetime.datetime.now().strftime(
                "%H:%M:%S"
            )
            self.gms_stats["rx_types"][msg_type] = (
                self.gms_stats["rx_types"].get(msg_type, 0) + 1
            )

            if isinstance(header, dict) and "responseId" in header:
                try:
                    res_id = header["responseId"]
                    parts = res_id.split("_")
                    if len(parts) >= 2 and parts[0] == "req":
                        sent_time = int(parts[1][:10])
                        self.gms_stats["latency_ms"] = int(
                            (time.time() - sent_time) * 1000
                        )
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

    async def send_request(
        self, msg_type: str, client_code: str, channel_id: str, body: Dict
    ) -> bool:
        # 🚦 Rule 8 Global: หากยังไม่ได้ข้อมูลเดิมมา ห้ามตะโกนซ้ำ (No shouts if pending)
        # 🆕 Optimized: Differentiate WorkflowInstanceListMsg by filter tag
        # This allows "Map Updates" to proceed even if "7-day History Fetch" is still in flight.
        lock_key = msg_type
        filter_tag = "GEN" # General
        if msg_type == "WorkflowInstanceListMsg":
            is_map_fetch = body.get("instanceStatus") == "20"
            filter_tag = "MAP" if is_map_fetch else "FULL"
            lock_key = f"{filter_tag}_{msg_type}"

        if lock_key in self.pending_requests:
            logger.info(f"🚦 [GMS] Rule 8: Skip {msg_type} (Previous {filter_tag} request STILL pending)")
            return False

        unique_id = int(time.time() * 1000) % 1000000
        req_id = f"req_{int(time.time())}{unique_id}_{filter_tag}_{msg_type}"
        if "msgType" not in body:
            body["msgType"] = msg_type

        # Default range for WorkflowInstanceListMsg if not provided
        if msg_type == "WorkflowInstanceListMsg":
            if "startTime" not in body or "endTime" not in body:
                today_dt = datetime.datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                body["startTime"] = (today_dt - datetime.timedelta(days=7)).strftime(
                    "%Y-%m-%d 00:00:00"
                )
                body["endTime"] = (today_dt + datetime.timedelta(days=1)).strftime(
                    "%Y-%m-%d 23:59:59"
                )

        # 🔥 Default status: 1 for WorkflowListMsg (Definitions)
        if msg_type == "WorkflowListMsg":
            if "status" not in body:
                body["status"] = 1

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
            self.pending_requests.add(lock_key)
            self._pending_times[lock_key] = time.time()
            await self._emit_pending()

            self.gms_stats["tx_types"][msg_type] = (
                self.gms_stats["tx_types"].get(msg_type, 0) + 1
            )
            self.gms_stats["last_activity"] = datetime.datetime.now().strftime(
                "%H:%M:%S"
            )

            logger.info(f"📤 [GMS] TX Request: {msg_type} (ID: {req_id})")
            await self.emit_log("TX", msg_type, req_data)
            _log_debug("TX", msg_type, body, elapsed_ms=None)
            return True
        return False

    async def send_raw(self, data_dict: Dict) -> bool:
        try:
            json_str = json.dumps(data_dict) + "\r\n"
            async with self._lock:
                if self._writer:
                    # 🛡️ Rule 9: Timeout on all GMS Writes (Prevents loop hangs)
                    self._writer.write(json_str.encode("utf-8"))
                    await asyncio.wait_for(self._writer.drain(), timeout=15.0)
                    self.stats["tx"] += 1
                    return True
        except asyncio.TimeoutError:
            self.gms_stats["total_errors"] += 1
            logger.error("Send Failed: GMS Socket Write Timeout (15s)")
            await self.emit_error(AppErrorCode.SOCKET_ERROR, "GMS Write Timeout")
            # Force disconnect if stuck
            await self.disconnect()
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

    async def emit_log(
        self,
        direction: str,
        msg_type: str,
        payload: Dict,
        size_str: Optional[str] = None,
    ):
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
                "size": size_str,
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
        """Helper to emit socket events with room routing"""
        try:
            target_room = room or (
                "page:map" if event in self._map_only_events else None
            )
            if target_room:
                await self._sio.emit(event, data, room=target_room)
            else:
                await self._sio.emit(event, data)
        except Exception as e:
            logger.error(f"Socket Emit Failed ({event}): {e}")

    async def broadcast_event(self, event_name: str, data: Any):
        """Broadcast event to all web clients with Chunking support for large lists"""
        if self._sio:
            try:
                # 📦 Chunking Logic for Lists (e.g. Locations, Robots, Tasks)
                if isinstance(data, list) and len(data) > settings.GMS_CHUNK_SIZE:
                    chunk_size = settings.GMS_CHUNK_SIZE
                    total_chunks = (len(data) + chunk_size - 1) // chunk_size

                    logger.info(
                        f"📦 [Chunking] {event_name}: Splitting {len(data)} items into {total_chunks} chunks"
                    )

                    for i in range(0, len(data), chunk_size):
                        chunk = data[i : i + chunk_size]
                        is_last = (i + chunk_size) >= len(data)

                        payload = {
                            "body": chunk,
                            "chunk_index": i // chunk_size,
                            "total_chunks": total_chunks,
                            "is_chunked": True,
                            "is_last_chunk": is_last,
                        }
                        await self._sio.emit(event_name, payload)
                        # Small sleep to prevent network congestion
                        await asyncio.sleep(0.01)
                else:
                    # Regular broadcast
                    logger.info(f"🌐 [FE] Push Data: {event_name}")
                    await self._sio.emit(event_name, {"body": data})
            except Exception as e:
                logger.error(f"Broadcast Error ({event_name}): {e}")

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
