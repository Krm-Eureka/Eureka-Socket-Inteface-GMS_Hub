import asyncio
import time
import datetime
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
        self._session_task: Optional[asyncio.Task] = None

    async def start_service(self):
        if self._running:
            logger.warning("Polling Manager already running.")
            return
        
        # Always create fresh loop-bound objects to avoid 'different event loop' errors on reload
        self._stop_event = asyncio.Event()
        self._tier_lock = asyncio.Lock()
        self._cache_lock = asyncio.Lock()
        
        self._running = True
        self._stop_event.clear()
        logger.info("Polling Manager starting session...")
        self._session_task = asyncio.create_task(self._session_worker())

    async def stop_service(self):
        if not self._running:
            return
        logger.info("Polling Manager stopping session...")
        self._running = False
        self._stop_event.set()
        if self._session_task:
            self._session_task.cancel()
            try:
                await self._session_task
            except asyncio.CancelledError:
                pass
            self._session_task = None
        
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
            self.fast_msg_types = [m.strip() for m in config["fast_msg_types"].split(",") if m.strip()]
        if "slow_msg_types" in config:
            self.slow_msg_types = [m.strip() for m in config["slow_msg_types"].split(",") if m.strip()]

        logger.info(f"Behavior Updated: Auto={self.auto_query}, FastInt={self.query_interval}s, SlowInt={self.slow_query_interval}s")

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

    async def _set_dynamic_tier_internal(self, msg_type: str, tier: str):
        """Internal helper without lock for reentrancy safety"""
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
        logger.debug(f"Dynamic Tier Updated: {msg_type} -> {tier}")

    async def set_dynamic_tier(self, msg_type: str, tier: str):
        async with self._tier_lock:
            await self._set_dynamic_tier_internal(msg_type, tier)

    async def set_client_page(self, sid: str, page: str):
        async with self._tier_lock:
            for watchers in self._page_watchers.values():
                watchers.discard(sid)
            if page in self._page_watchers:
                self._page_watchers[page].add(sid)
            any_on_map = bool(self._page_watchers["map"])
            any_on_task = bool(self._page_watchers["taskmonitoring"])

            await self._set_dynamic_tier_internal("LocationListMsg", "fast" if any_on_map else "slow")
            await self._set_dynamic_tier_internal("WorkflowInstanceListMsg", "fast" if (any_on_task or any_on_map) else "slow")

        logger.info(f"Page Watchers -> map: {self._page_watchers['map']}, task: {self._page_watchers['taskmonitoring']}")

    async def remove_client(self, sid: str):
        await self.set_client_page(sid, "")

    async def _session_worker(self):
        backoff_seconds = settings.GMS_RECONNECT_INITIAL_DELAY
        max_backoff = settings.GMS_RECONNECT_MAX_DELAY

        while self._running:
            try:
                success = await self._gms.connect()
                if success:
                    backoff_seconds = settings.GMS_RECONNECT_INITIAL_DELAY
                    logger.info("Performing Startup Query (One-time)...")
                    
                    self._gms.start_background_tasks()

                    for msg_type in self.startup_msg_types:
                        body = {}
                        if msg_type == "WorkflowInstanceListMsg":
                            today_dt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                            body = {
                                "startTime": (today_dt - datetime.timedelta(days=14)).strftime("%Y-%m-%d 00:00:00"),
                                "endTime": (today_dt + datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00:00"),
                            }
                        await self._gms.send_request(msg_type, self.client_code, self.channel_id, body)

                    hb_task = asyncio.create_task(self._heartbeat_loop())
                    poll_task = asyncio.create_task(self._polling_loop())

                    try:
                        await self._gms.read_loop(lambda: self._running)
                    finally:
                        hb_task.cancel()
                        poll_task.cancel()
                        await asyncio.gather(hb_task, poll_task, return_exceptions=True)

                if self._running:
                    logger.warning(f"GMS Session lost or failed. Retrying in {backoff_seconds}s...")
                    await self._gms.disconnect()
                    try:
                        await asyncio.wait_for(self._stop_event.wait(), timeout=backoff_seconds)
                        break
                    except asyncio.TimeoutError:
                        backoff_seconds = min(backoff_seconds * 2, max_backoff)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Critical error in Session Worker: {e}")
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=1.0)
                    break
                except asyncio.TimeoutError:
                    pass
        logger.info("Session Worker Ended")

    async def _heartbeat_loop(self):
        logger.info("Heartbeat Loop Started")
        try:
            while self._running and self._gms.is_connected():
                silent_duration = time.time() - self._gms.last_rx_time
                if silent_duration > 15.0:
                    logger.warning(f"Watchdog: GMS is silent for {silent_duration:.1f}s. Forcing reconnection...")
                    await self._gms.disconnect()
                    break

                await self._gms.send_request("HeartbeatMsg", self.client_code, self.channel_id, {})
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=5.0)
                    break
                except asyncio.TimeoutError:
                    pass
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Heartbeat Loop Error: {e}")
        logger.info("Heartbeat Loop Ended")

    async def handle_gms_message(self, data: Dict):
        try:
            header = data.get("header", {})
            body = data.get("body", {})
            msg_type = header.get("msgType") or body.get("msgType")

            if msg_type == "WorkflowInstanceListMsg":
                new_tasks = body if isinstance(body, list) else (body.get("workflowInstanceList", []) if isinstance(body, dict) else [])
                if new_tasks:
                    async with self._cache_lock:
                        task_map = {}
                        for t in self._task_cache:
                            tid = t.get("instanceId") or t.get("workflowInstanceId")
                            if tid: task_map[tid] = t

                        for t in new_tasks:
                            if t is None: continue
                            tid = t.get("instanceId") or t.get("workflowInstanceId")
                            if tid: task_map[tid] = t

                        def get_sort_key(task):
                            if task is None: return ("0000-00-00 00:00:00", 0)
                            st = str(task.get("startTime") or "0000-00-00 00:00:00")
                            tid_val = task.get("taskId")
                            try:
                                n_tid = int(tid_val) if tid_val is not None else 0
                            except:
                                n_tid = 0
                            return (st, n_tid)

                        all_tasks = list(task_map.values())
                        self._task_cache = sorted(all_tasks, key=get_sort_key, reverse=True)[:30000]
                        logger.debug(f"Merged {len(new_tasks)} tasks. Cache: {len(self._task_cache)}")
        except Exception as e:
            logger.error(f"Error updating task cache: {e}")

    async def get_paginated_tasks(self, page=1, page_size=30, start_time: str = None, end_time: str = None):
        async with self._cache_lock:
            tasks = self._task_cache

        if start_time and end_time:
            f_start = start_time if len(start_time) > 10 else f"{start_time} 00:00:00"
            f_end = end_time if len(end_time) > 10 else f"{end_time} 23:59:59"
            tasks = [t for t in tasks if f_start <= str(t.get("startTime") or "0000-00-00 00:00:00") <= f_end]

        try:
            n_page, n_size = int(page), int(page_size)
        except:
            n_page, n_size = 1, 20

        total_count = len(tasks)
        start_idx = (n_page - 1) * n_size
        paged_data = tasks[start_idx : start_idx + n_size]

        return {
            "tasks": paged_data,
            "totalCount": total_count,
            "page": n_page,
            "pageSize": n_size,
            "totalPages": (total_count + n_size - 1) // n_size if total_count > 0 else 0,
        }

    async def _polling_loop(self):
        logger.info("Polling Loop Started")
        self._last_slow_query = 0.0
        try:
            while self._running and self._gms.is_connected():
                if self.auto_query:
                    start_time = time.time()
                    await self._gms.refresh_pending_ui()

                    today_dt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    start_dt_7d = today_dt - datetime.timedelta(days=7)
                    end_dt_1d = today_dt + datetime.timedelta(days=1)

                    async with self._tier_lock:
                        fast_types = list(self.fast_msg_types)
                        slow_types = list(self.slow_msg_types)

                    for msg_type in fast_types:
                        if msg_type in self._gms.pending_requests: continue
                        body = {}
                        if msg_type == "WorkflowInstanceListMsg":
                            body = {
                                "startTime": start_dt_7d.strftime("%Y-%m-%d 00:00:00"),
                                "endTime": end_dt_1d.strftime("%Y-%m-%d 23:59:59"),
                            }
                        await self._gms.send_request(msg_type, self.client_code, self.channel_id, body)

                    now = time.time()
                    if now - self._last_slow_query >= self.slow_query_interval:
                        self._last_slow_query = now
                        for msg_type in slow_types:
                            if msg_type in self._gms.pending_requests: continue
                            body = {}
                            if msg_type == "WorkflowInstanceListMsg":
                                body = {
                                    "startTime": start_dt_7d.strftime("%Y-%m-%d 00:00:00"),
                                    "endTime": today_dt.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d 23:59:59"),
                                }
                            await self._gms.send_request(msg_type, self.client_code, self.channel_id, body)

                    if now - self._last_workflow_refresh >= self.workflow_refresh_interval:
                        self._last_workflow_refresh = now
                        if "WorkflowListMsg" not in self._gms.pending_requests:
                            await self._gms.send_request("WorkflowListMsg", self.client_code, self.channel_id, {})

                    wait_time = max(0.2, self.query_interval - (time.time() - start_time))
                    try:
                        await asyncio.wait_for(self._stop_event.wait(), timeout=wait_time)
                        break
                    except asyncio.TimeoutError:
                        pass
                else:
                    try:
                        await asyncio.wait_for(self._stop_event.wait(), timeout=0.5)
                        break
                    except asyncio.TimeoutError:
                        pass
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Polling Loop Error: {e}")
        logger.info("Polling Loop Ended")
        logger.info("Polling Loop Ended")
