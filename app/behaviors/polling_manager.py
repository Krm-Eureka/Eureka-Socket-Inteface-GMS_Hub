import threading
import time
import datetime
from typing import List, Dict, Set
from loguru import logger
from app.services.gms_client import GMSClient
from app.core.config import settings


class PollingManager:
    """[BEHAVIOR] Manages polling logic, heartbeats and thread sessions"""

    def __init__(self, gms_client: GMSClient):
        self._gms = gms_client
        self._running = False
        self._stop_event = threading.Event()
        self._tier_lock = (
            threading.RLock()
        )  # RLock: reentrant — safe for nested acquire in set_client_page → set_dynamic_tier
        self.client_code = settings.GMS_CLIENT_CODE
        self.channel_id = settings.GMS_CHANNEL_ID
        self.auto_query = True
        self._task_cache = []  # Store latest WorkflowInstanceListMsg data
        self._cache_lock = threading.Lock()

        # Polling Categories
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
            # WorkflowInstanceListMsg ย้ายไป slow tier แล้ว — ลด load fast poll
        ]
        self.slow_msg_types = [
            "LocationListMsg",
            "WorkflowInstanceListMsg",
        ]

        # Per-client page tracking: { page_name: {sid1, sid2, ...} }
        self._page_watchers: Dict[str, Set[str]] = {
            "map": set(),
            "taskmonitoring": set(),
        }

        self._last_slow_query = 0
        self.workflow_refresh_interval = 10 * 60  # 10 minutes
        self._last_workflow_refresh = 0

    def start_service(self):
        if self._running:
            logger.warning("Polling Manager already running.")
            return
        self._running = True
        self._stop_event.clear()
        logger.info("Polling Manager starting session...")
        threading.Thread(
            target=self._session_worker, name="PollingManagerThread", daemon=True
        ).start()

    def stop_service(self):
        if not self._running:
            return
        logger.info("Polling Manager stopping session...")
        self._running = False
        self._stop_event.set()
        self._gms.disconnect()

    def update_behavior(self, config: Dict):
        self.client_code = config.get("client_code", self.client_code)
        self.channel_id = config.get("channel_id", self.channel_id)
        self.auto_query = config.get("auto_query", self.auto_query)
        if "interval_ms" in config:
            self.query_interval = float(config["interval_ms"]) / 1000.0

        # Allow dynamic updates to msg types if needed
        if "fast_msg_types" in config:
            self.fast_msg_types = [
                m.strip() for m in config["fast_msg_types"].split(",") if m.strip()
            ]
        if "slow_msg_types" in config:
            self.slow_msg_types = [
                m.strip() for m in config["slow_msg_types"].split(",") if m.strip()
            ]

        logger.info(
            f"Behavior Updated: Auto={self.auto_query}, FastInt={self.query_interval}s, SlowInt={self.slow_query_interval}s"
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

    def set_dynamic_tier(self, msg_type: str, tier: str):
        """Move a message type between layers (e.g. 'fast' or 'slow') - Thread Safe"""
        with self._tier_lock:
            if tier == "fast":
                if msg_type not in self.fast_msg_types:
                    self.fast_msg_types.append(msg_type)
                if msg_type in self.slow_msg_types:
                    self.slow_msg_types.remove(msg_type)
            elif tier == "slow":
                if msg_type not in self.slow_msg_types:
                    self.slow_msg_types.append(msg_type)
                if msg_type in self.fast_msg_types:
                    self.fast_msg_types.remove(msg_type)

        logger.info(f"Dynamic Tier Updated: {msg_type} -> {tier}")

    def set_client_page(self, sid: str, page: str):
        """Track which page each client is on and adjust tiers accordingly."""
        with self._tier_lock:  # Atomic: discard + add must not interleave between concurrent callers
            for watchers in self._page_watchers.values():
                watchers.discard(sid)
            if page in self._page_watchers:
                self._page_watchers[page].add(sid)
            any_on_map = bool(self._page_watchers["map"])
            any_on_task = bool(self._page_watchers["taskmonitoring"])

        # set_dynamic_tier also acquires _tier_lock — safe because RLock is reentrant
        self.set_dynamic_tier("LocationListMsg", "fast" if any_on_map else "slow")
        self.set_dynamic_tier(
            "WorkflowInstanceListMsg", "fast" if (any_on_task or any_on_map) else "slow"
        )

        logger.info(
            f"Page Watchers -> map: {self._page_watchers['map']}, "
            f"task: {self._page_watchers['taskmonitoring']}"
        )

    def remove_client(self, sid: str):
        """Remove a disconnected client from all page watchers and recalculate tiers."""
        self.set_client_page(sid, "")  # Empty page removes from all watchers

    def _session_worker(self):
        """Higher level session management"""
        backoff_seconds = settings.GMS_RECONNECT_INITIAL_DELAY
        max_backoff = settings.GMS_RECONNECT_MAX_DELAY

        while self._running:
            try:
                sock = self._gms.connect()
                if sock:
                    backoff_seconds = (
                        settings.GMS_RECONNECT_INITIAL_DELAY
                    )  # Reset on success
                    # 1. Connected: Perform Startup Query (Once per connect)
                    logger.info("Performing Startup Query (One-time)...")
                    for msg_type in self.startup_msg_types:
                        body = {}
                        if msg_type == "WorkflowInstanceListMsg":
                            # Today at 00:00:00
                            today_dt = datetime.datetime.now().replace(
                                hour=0, minute=0, second=0, microsecond=0
                            )
                            start_dt = today_dt - datetime.timedelta(days=14)
                            end_dt = today_dt + datetime.timedelta(days=1)
                            body = {
                                "msgType": "WorkflowInstanceListMsg",
                                "startTime": start_dt.strftime("%Y-%m-%d 00:00:00"),
                                "endTime": end_dt.strftime("%Y-%m-%d 00:00:00"),
                            }
                        self._gms.send_request(
                            msg_type, self.client_code, self.channel_id, body
                        )

                    # 2. Start sub-behavioral loops
                    hb_thread = threading.Thread(
                        target=self._heartbeat_loop,
                        args=(sock,),
                        name="HeartbeatThread",
                        daemon=True,
                    )
                    poll_thread = threading.Thread(
                        target=self._polling_loop,
                        args=(sock,),
                        name="PollingThread",
                        daemon=True,
                    )
                    hb_thread.start()
                    poll_thread.start()

                    # Blocking read loop (The Service part)
                    self._gms.read_loop(lambda: self._running)

                if self._running:
                    logger.warning(
                        f"GMS Session lost or failed. Retrying in {backoff_seconds}s..."
                    )
                    # Ensure it's disconnected properly
                    self._gms.disconnect()
                    if self._stop_event.wait(backoff_seconds):
                        break
                    # Exponential backoff
                    backoff_seconds = min(backoff_seconds * 2, max_backoff)
            except Exception as e:
                logger.error(f"Critical error in Session Worker: {e}")
                if self._stop_event.wait(1.0):
                    break

    def _heartbeat_loop(self, sock_ref):
        logger.info("Heartbeat Loop Started")
        while self._running and self._gms._sock == sock_ref:
            try:
                # Watchdog: Check if GMS is silent for too long (> 15s)
                silent_duration = time.time() - self._gms.last_rx_time
                if silent_duration > 15.0:
                    logger.warning(
                        f"Watchdog: GMS is silent for {silent_duration:.1f}s. Forcing reconnection..."
                    )
                    self._gms.disconnect()
                    break

                self._gms.send_request(
                    "HeartbeatMsg", self.client_code, self.channel_id, {}
                )
                if self._stop_event.wait(5):  # Every 5s
                    break
            except Exception as e:
                logger.error(f"Heartbeat Loop Error: {e}")
                if self._stop_event.wait(1):
                    break
                if not self._gms.is_connected():
                    break
        logger.info("Heartbeat Loop Ended")

    def handle_gms_message(self, data):
        """Unified message handler to support caching for pagination"""
        try:
            header = data.get("header", {})
            body = data.get("body", {})
            msg_type = header.get("msgType") or body.get("msgType")

            if msg_type == "WorkflowInstanceListMsg":
                # GMS might send a direct list or wrap it in a dict field
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
                    with self._cache_lock:
                        # 1. Create a map of existing tasks by ID
                        # Use either 'instanceId' or 'workflowInstanceId'
                        task_map = {}
                        for t in self._task_cache:
                            tid = t.get("instanceId") or t.get("workflowInstanceId")
                            if tid:
                                task_map[tid] = t

                        # 2. Merge new tasks (potentially update status)
                        for t in new_tasks:
                            if t is None: continue
                            tid = t.get("instanceId") or t.get("workflowInstanceId")
                            if tid:
                                task_map[tid] = t

                        # 3. Define robust sorting key (Latest first)
                        def get_sort_key(task):
                            if task is None: return ("0000-00-00 00:00:00", 0)
                            st = str(task.get("startTime") or "0000-00-00 00:00:00")
                            # Secondary sort by taskId (numeric)
                            tid_val = task.get("taskId")
                            try:
                                n_tid = int(tid_val) if tid_val is not None else 0
                            except:
                                n_tid = 0
                            return (st, n_tid)

                        # 4. Sort and apply limit
                        all_tasks = list(task_map.values())
                        sorted_tasks = sorted(all_tasks, key=get_sort_key, reverse=True)
                        self._task_cache = sorted_tasks[:30000]

                        logger.debug(
                            f"Merged {len(new_tasks)} new tasks. Cache size: {len(self._task_cache)} (Limit: 30000)"
                        )
                else:
                    logger.warning("WorkflowInstanceListMsg body is empty")

        except Exception as e:
            logger.error(f"Error updating task cache: {e}")

    def get_paginated_tasks(
        self, page=1, page_size=30, start_time: str = None, end_time: str = None
    ):
        """Returns a slice of the cached tasks with total count, optionally filtered by date"""
        with self._cache_lock:
            tasks = self._task_cache

        if start_time and end_time:
            # 🛡️ Pad dates to ensure full day coverage if they are YYYY-MM-DD
            f_start = start_time if len(start_time) > 10 else f"{start_time} 00:00:00"
            f_end = end_time if len(end_time) > 10 else f"{end_time} 23:59:59"

            tasks = [
                t
                for t in tasks
                if f_start <= str(t.get("startTime") or "0000-00-00 00:00:00") <= f_end
            ]

        # 🛡️ Critical: Logic below must be OUTSIDE the if-block to handle all requests
        try:
            n_page = int(page)
            n_size = int(page_size)
        except (ValueError, TypeError):
            n_page, n_size = 1, 20

        total_count = len(tasks)
        start_idx = (n_page - 1) * n_size
        end_idx = start_idx + n_size

        # Ensure indices are within bounds
        paged_data = tasks[start_idx:end_idx]

        return {
            "tasks": paged_data,
            "totalCount": total_count,
            "page": n_page,
            "pageSize": n_size,
            "totalPages": (
                (total_count + n_size - 1) // n_size if total_count > 0 else 0
            ),
        }

    def _polling_loop(self, sock_ref):
        logger.info("Polling Loop Started")
        # Reset slow timer on start
        self._last_slow_query = 0

        while self._running and self._gms._sock == sock_ref:
            if self.auto_query:
                start_time = time.time()
                try:
                    now = time.time()

                    # Today at 00:00:00 for shared use
                    today_dt = datetime.datetime.now().replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                    start_dt_7d = today_dt - datetime.timedelta(days=7)
                    end_dt_1d = today_dt + datetime.timedelta(days=1)

                    # RC-1 Fix: snapshot lists while holding the lock to prevent
                    # RuntimeError if set_dynamic_tier modifies them concurrently
                    with self._tier_lock:
                        fast_types = list(self.fast_msg_types)
                        slow_types = list(self.slow_msg_types)

                    # 1. Fast Layer (1s Interval)
                    for msg_type in fast_types:
                        # Skip if a similar request is pending to avoid flooding
                        if msg_type in self._gms.pending_requests:
                            continue
                        body = {}
                        if msg_type == "WorkflowInstanceListMsg":
                            body = {
                                "msgType": "WorkflowInstanceListMsg",
                                "startTime": start_dt_7d.strftime("%Y-%m-%d 00:00:00"),
                                "endTime": end_dt_1d.strftime("%Y-%m-%d 23:59:59"),
                            }
                        self._gms.send_request(
                            msg_type, self.client_code, self.channel_id, body
                        )

                    # 2. Slow Layer (30s Interval)
                    if now - self._last_slow_query >= self.slow_query_interval:
                        self._last_slow_query = now
                        for msg_type in slow_types:
                            if msg_type in self._gms.pending_requests:
                                continue
                            body = {}
                            if msg_type == "WorkflowInstanceListMsg":
                                # 7 วันย้อนหลัง 00:00:00 → วันนี้ 23:59:59
                                end_today = today_dt.replace(
                                    hour=23, minute=59, second=59
                                )
                                body = {
                                    "msgType": "WorkflowInstanceListMsg",
                                    "startTime": start_dt_7d.strftime(
                                        "%Y-%m-%d 00:00:00"
                                    ),
                                    "endTime": end_today.strftime("%Y-%m-%d 23:59:59"),
                                }
                            self._gms.send_request(
                                msg_type, self.client_code, self.channel_id, body
                            )

                    # 3. Very Slow Layer (10m Interval) - OPT-3
                    if (
                        now - self._last_workflow_refresh
                        >= self.workflow_refresh_interval
                    ):
                        self._last_workflow_refresh = now
                        if "WorkflowListMsg" not in self._gms.pending_requests:
                            self._gms.send_request(
                                "WorkflowListMsg", self.client_code, self.channel_id, {}
                            )

                    # Dynamic wait to keep 1s interval even with processing time
                    elapsed = time.time() - start_time
                    wait_time = max(0.2, self.query_interval - elapsed)

                    if self._stop_event.wait(wait_time):
                        break
                except Exception as e:
                    logger.error(f"Polling Loop Error: {e}")
                    if self._stop_event.wait(1):
                        break
                    if not self._gms.is_connected():
                        break
            else:
                if self._stop_event.wait(0.5):
                    break
        logger.info("Polling Loop Ended")
