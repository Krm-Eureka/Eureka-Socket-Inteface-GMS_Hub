import asyncio
import time
import datetime
import re
from typing import List, Dict, Set, Optional, Any
from loguru import logger
from app.services.gms_client import GMSClient
from app.core.config import settings


class PollingManager:
    """[BEHAVIOR] Manages async polling logic, heartbeats and task sessions"""

    def __init__(self, gms_client: GMSClient):
        self._gms = gms_client
        self._running = False
        self._stop_event: Optional[asyncio.Event] = None
        self._tier_lock: Optional[asyncio.Lock] = None
        self._cache_lock: Optional[asyncio.Lock] = None

        self.client_code = settings.GMS_CLIENT_CODE
        self.channel_id = settings.GMS_CHANNEL_ID
        self.auto_query = True
        self._task_cache: List[Dict] = []

        self.query_interval = settings.QUERY_INTERVAL_FAST
        self.slow_query_interval = settings.QUERY_INTERVAL_SLOW

        self.startup_msg_types = [
            "StationListMsg",
            "LocationListMsg",
            "WorkflowListMsg",
        ]
        self.fast_msg_types = [
            "RobotInfoMsg",
            "ContainerListMsg",
        ]
        self.slow_msg_types = [
            "LocationListMsg",
            "WorkflowInstanceListMsg",
        ]

        self._page_watchers: Dict[str, Set[str]] = {
            "map": set(),
            "taskmonitoring": set(),
        }

        self._last_slow_query = 0.0
        self.workflow_refresh_interval = 10 * 60
        self._last_workflow_refresh = 0.0
        self._last_task_query = 0.0
        self.task_query_interval = 10.0  # 🕒 Base Interval
        self._last_task_update_ts = 0.0  # 🛡️ Stale Data Prevention

        # ⏱️ Per-Message Cooldown Tracking
        self._last_msg_rx_times: Dict[str, float] = {}
        self.msg_cooldown = 0.3  # 300ms
        self._polling_tasks: List[asyncio.Task] = []

    async def start_service(self):
        if self._running:
            logger.warning("Polling Manager already running.")
            return

        # Always create fresh loop-bound objects
        self._stop_event = asyncio.Event()
        self._tier_lock = asyncio.Lock()
        self._cache_lock = asyncio.Lock()

        self._running = True
        self._stop_event.clear()
        logger.info("Polling Service (Horizontal Line Model)")

        # 🎯 Define the independent "Shouters" (Parallel Tiers)
        self._polling_tasks = [
            asyncio.create_task(self._session_worker()),  # GMS Connection & Monitor
            asyncio.create_task(
                self._fast_poll_loop()
            ),  # Robot, Location, Container (1s)
            asyncio.create_task(
                self._task_poll_loop()
            ),  # Workflow Instances (Context-aware)
            asyncio.create_task(self._slow_poll_loop()),  # Station List (30s)
            asyncio.create_task(self._workflow_poll_loop()),  # Workflow Names (60s)
            asyncio.create_task(self._heartbeat_loop()),  # Heartbeats
        ]

    async def stop_service(self):
        if not self._running:
            return
        logger.info("Polling Manager stopping session...")
        self._running = False
        if self._stop_event:
            self._stop_event.set()

        for t in self._polling_tasks:
            if not t.done():
                t.cancel()

        self._polling_tasks = []

        # Reset loop-bound objects
        self._stop_event = None
        self._tier_lock = None
        self._cache_lock = None

        await self._gms.disconnect()

    def update_behavior(self, config: Dict):
        self.client_code = config.get("client_code", self.client_code)
        self.channel_id = config.get("channel_id", self.channel_id)
        self.auto_query = config.get("auto_query", self.auto_query)
        if "interval_ms" in config:
            self.query_interval = float(config["interval_ms"]) / 1000.0

        if "fast_msg_types" in config:
            self.fast_msg_types = [
                m.strip() for m in config["fast_msg_types"].split(",") if m.strip()
            ]
        if "slow_msg_types" in config:
            self.slow_msg_types = [
                m.strip() for m in config["slow_msg_types"].split(",") if m.strip()
            ]

        logger.info(
            f"Behavior Updated: Auto={self.auto_query}, FastInt={self.query_interval}s"
        )

    def get_config(self) -> Dict:
        return {
            "gms_ip": settings.GMS_IP,
            "gms_port": settings.GMS_PORT,
            "client_code": self.client_code,
            "channel_id": self.channel_id,
            "auto_query": self.auto_query,
            "interval_ms": int(self.query_interval * 1000),
            "fast_msg_types": ",".join(self.fast_msg_types),
            "slow_msg_types": ",".join(self.slow_msg_types),
        }

    async def _emit_pending(self):
        """Broadcast current pending request types to UI for debugging/sync visualization."""
        try:
            p_list = []
            now = time.time()
            for msg_type in sorted(list(self._gms.pending_requests)):
                sent_at = self._gms._pending_times.get(msg_type, now)
                elapsed_str = f"{(now - sent_at):.1f}"
                p_list.append(f"{msg_type} _ {elapsed_str}s")

            # 🟢 Restored: ESIG dashboard needs this.
            await self._gms.emit_socket("gms:status:pending", {"pending": p_list}, room="room:admin")
        except Exception as e:
            logger.error(f"Error emitting pending requests: {e}")

    async def set_client_page(self, sid: str, page: str):
        """Track which page the client is on (Socket.IO Room management)"""
        async with self._tier_lock:
            for watchers in self._page_watchers.values():
                watchers.discard(sid)
            if page in self._page_watchers:
                self._page_watchers[page].add(sid)

        logger.info(f"Active Page Update -> sid:{sid} page:{page}")

    async def remove_client(self, sid: str):
        await self.set_client_page(sid, "")

    # ─────────────────────────────────────────────────────────
    # 🎯 HORTIZONAL LINE POLLING LOOPS (Independent Shouters)
    # ─────────────────────────────────────────────────────────

    async def _fast_poll_loop(self):
        """Tier 1: High-Frequency Map Data (1s) - Robot, Container, Location"""
        logger.info("(Fast Poll)")
        msg_types = ["RobotInfoMsg", "ContainerListMsg", "LocationListMsg"]

        while self._running:
            if not self._running or not self._gms.is_connected():
                await asyncio.sleep(1.0)
                continue

            if self.auto_query:
                await self._emit_pending()

                # Optimization: High-performance Parallel Fetch with Retry
                # Rule 8: If still pending, skip.
                # Cooldown: If recent RX, skip.
                now = time.time()
                to_shout = []
                for m in msg_types:
                    if m in self._gms.pending_requests:
                        continue
                    if (now - self._last_msg_rx_times.get(m, 0)) < self.msg_cooldown:
                        continue
                    to_shout.append(m)

                if to_shout:
                    tasks = [
                        self._gms.send_request(m, self.client_code, self.channel_id, {})
                        for m in to_shout
                    ]

                    # 🚦 [PARALLEL] Shout all at once
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # [RETRY] If any failed (returned False) AND we are still connected
                    retry_list = []
                    for m, res in zip(to_shout, results):
                        if res is False or isinstance(res, Exception):
                            retry_list.append(m)

                    if retry_list and self._gms.is_connected():
                        logger.warning(
                            f"⚠️ [Parallel] {retry_list} failed. Retrying one more time..."
                        )
                        await asyncio.sleep(0.1)  # Brief pause before retry
                        retry_tasks = [
                            self._gms.send_request(
                                m, self.client_code, self.channel_id, {}
                            )
                            for m in retry_list
                        ]
                        await asyncio.gather(*retry_tasks, return_exceptions=True)

            await asyncio.sleep(0.25)

    async def _task_poll_loop(self):
        """Tier 2: Workflow Instance Monitoring (Context-Aware)"""
        logger.info("ฝ่ายคุมรายการงาน (Task Poll) เริ่มเข้าเวร...")
        while self._running:
            if not self._running or not self._gms.is_connected():
                await asyncio.sleep(2.0)
                continue

            if self.auto_query:
                # Check context
                async with self._tier_lock:
                    is_map_active = bool(self._page_watchers.get("map"))
                    is_task_active = bool(self._page_watchers.get("taskmonitoring"))

                if is_map_active:
                    interval = 1.0  # 🔥 Faster for map (was 2.0)
                    days = 0
                    tag = "MAP"
                elif is_task_active:
                    interval = 3.0  # 🔥 Faster for task monitoring (was 5.0)
                    days = 3
                    tag = "FULL"
                else:
                    interval = 15.0
                    days = 3
                    tag = "FULL"

                lock_key = f"{tag}_WorkflowInstanceListMsg"
                if lock_key not in self._gms.pending_requests:
                    now_dt = datetime.datetime.now()
                    today_zero = now_dt.replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    start_dt = today_zero - datetime.timedelta(days=days)
                    end_dt = today_zero + datetime.timedelta(days=1)

                    body = {
                        "startTime": start_dt.strftime("%Y-%m-%d 00:00:00"),
                        "endTime": end_dt.strftime("%Y-%m-%d 23:59:59"),
                    }
                    # ✅ Fix 5: Map mode requests only running tasks (instanceStatus=20)
                    if tag == "MAP":
                        body["instanceStatus"] = "20"

                    logger.info(
                        f"🔄 [Poll] Requesting {days}-day Task List tag={tag} (Interval: {interval}s)"
                    )
                    await self._gms.send_request(
                        "WorkflowInstanceListMsg",
                        self.client_code,
                        self.channel_id,
                        body,
                    )

                await asyncio.sleep(interval)
            else:
                await asyncio.sleep(1.0)

    async def _slow_poll_loop(self):
        """Tier 3: Station definitions (30s)"""
        while self._running:
            if not self._running or not self._gms.is_connected():
                await asyncio.sleep(5.0)
                continue

            if self.auto_query:
                if "StationListMsg" not in self._gms.pending_requests:
                    logger.info("🔄 [Poll] Requesting Station List (Tier 3)")
                    await self._gms.send_request(
                        "StationListMsg", self.client_code, self.channel_id, {}
                    )
                await asyncio.sleep(30.0)
            else:
                await asyncio.sleep(5.0)

    async def _workflow_poll_loop(self):
        """Tier 4: Workflow Definitions (60s)"""
        while self._running:
            if not self._running or not self._gms.is_connected():
                await asyncio.sleep(10.0)
                continue

            if self.auto_query:
                if "WorkflowListMsg" not in self._gms.pending_requests:
                    await self._gms.send_request(
                        "WorkflowListMsg", self.client_code, self.channel_id, {}
                    )
                await asyncio.sleep(60.0)
            else:
                await asyncio.sleep(10.0)

    async def _heartbeat_loop(self):
        logger.info("Heartbeat Loop Started")
        while self._running:
            if not self._gms.is_connected():
                await asyncio.sleep(2.0)
                continue

            # Watchdog
            silent_duration = time.time() - self._gms.last_rx_time
            if silent_duration > 45.0:
                logger.warning(
                    f"Watchdog: GMS is silent for {silent_duration:.1f}s. Reconnecting..."
                )
                await self._gms.disconnect()
            else:
                # 🛡️ Rule 8: If waiting for a heart, don't shout again.
                if "HeartbeatMsg" not in self._gms.pending_requests:
                    await self._gms.send_request(
                        "HeartbeatMsg", self.client_code, self.channel_id, {}
                    )

                # 🕒 [WATCHDOG] Force-clear requests that GMS never answered (Rule 8 recovery)
                await self._gms.clear_stale_requests(timeout_secs=30.0)


            try:
                if self._stop_event:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=10.0)
                else:
                    await asyncio.sleep(10.0)
            except asyncio.TimeoutError:
                pass
        logger.info("Heartbeat Loop Ended")

    async def _session_worker(self):
        """Main Connection Worker & Startup logic"""
        backoff = 2.0
        while self._running:
            try:
                success = await self._gms.connect()
                if success:
                    backoff = 2.0
                    self._gms.start_background_tasks()

                    # One-time startup queries (Check if not pending)
                    for msg_type in self.startup_msg_types:
                        if msg_type not in self._gms.pending_requests:
                            await self._gms.send_request(
                                msg_type, self.client_code, self.channel_id, {}
                            )
                            await asyncio.sleep(0.1)

                    # Monitor the connection
                    await self._gms.read_loop(lambda: self._running)

                if self._running:
                    logger.warning(
                        f"Session Work interrupted. Reconnecting in {backoff}s..."
                    )
                    await self._gms.disconnect()
                    try:
                        if self._stop_event:
                            await asyncio.wait_for(
                                self._stop_event.wait(), timeout=backoff
                            )
                        else:
                            await asyncio.sleep(backoff)
                    except asyncio.TimeoutError:
                        backoff = min(backoff * 2, 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Session Worker Error: {e}")
                await asyncio.sleep(5.0)

    async def handle_gms_message(self, data: Dict):
        try:
            header = data.get("header", {})
            body = data.get("body", {})
            msg_type = header.get("msgType") or body.get("msgType")

            if msg_type:
                self._last_msg_rx_times[msg_type] = time.time()

            if msg_type == "WorkflowInstanceListMsg":
                resp_ts = 0.0
                if isinstance(header, dict) and "responseId" in header:
                    try:
                        resp_ts = float(header["responseId"].split("_")[1])
                    except:
                        pass

                if resp_ts > 0 and resp_ts < self._last_task_update_ts:
                    return  # Stale

                if resp_ts > 0:
                    self._last_task_update_ts = resp_ts

                new_tasks = (
                    body
                    if isinstance(body, list)
                    else (
                        body.get("workflowInstanceList", [])
                        if isinstance(body, dict)
                        else []
                    )
                )
                if new_tasks:
                    async with self._cache_lock:
                        # 🛠️ Deduplicate and Merge
                        task_map = {
                            (t.get("instanceId") or t.get("workflowInstanceId")): t
                            for t in self._task_cache
                            if (t.get("instanceId") or t.get("workflowInstanceId"))
                        }
                        for t in new_tasks:
                            if not t:
                                continue
                            iid = t.get("instanceId") or t.get("workflowInstanceId")
                            if iid:
                                task_map[iid] = t

                        all_tasks = list(task_map.values())

                        def fast_int_sort(v):
                            if not v:
                                return 0
                            if isinstance(v, (int, float)):
                                return int(v)
                            # re is imported at top
                            try:
                                m = re.findall(r"\d+", str(v))
                                return int(m[-1]) if m else 0
                            except:
                                return 0

                        # ✅ Fix 4: 7-day time-based eviction — ป้องกัน task เก่าสะสมนาน
                        cutoff = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime(
                            "%Y-%m-%d 00:00:00"
                        )
                        all_tasks = [
                            t for t in all_tasks
                            if str(t.get("startTime") or "") >= cutoff
                        ]

                        # 🚀 Sort by startTime then numeric ID, cap at 5000
                        self._task_cache = sorted(
                            all_tasks,
                            key=lambda x: (
                                str(x.get("startTime") or ""),
                                fast_int_sort(
                                    x.get("instanceId") or x.get("workflowInstanceId")
                                ),
                            ),
                            reverse=True,
                        )[:5000]  # Hard cap for memory safety
        except Exception as e:
            logger.error(f"Error handling GMS msg: {e}")

    async def get_task_cache(self, start_time=None, end_time=None):
        async with self._cache_lock:
            tasks = self._task_cache
        if start_time and end_time:
            tasks = [
                t
                for t in tasks
                if start_time <= str(t.get("startTime") or "") <= end_time
            ]

        total = len(tasks)
        return {
            "tasks": tasks,
            "totalCount": total,
            "page": 1,
            "pageSize": total,
            "totalPages": 1 if total > 0 else 0,
        }
