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
        self._tier_lock = threading.Lock()  # Thread-safe tier management
        self.client_code = settings.GMS_CLIENT_CODE
        self.channel_id = settings.GMS_CHANNEL_ID
        self.auto_query = True

        # Polling Categories
        self.query_interval = 1.0  # Fast Layer
        self.slow_query_interval = 60.0  # Slow Layer

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

        # Per-client page tracking: { page_name: {sid1, sid2, ...} }
        self._page_watchers: Dict[str, Set[str]] = {
            "map": set(),
            "taskmonitoring": set(),
        }

        self._last_slow_query = 0

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
        # Remove sid from all page watcher sets
        for watchers in self._page_watchers.values():
            watchers.discard(sid)

        # Add to new page watcher set (if it's a tracked page)
        if page in self._page_watchers:
            self._page_watchers[page].add(sid)

        # Recalculate tiers based on remaining watchers
        any_on_map = bool(self._page_watchers["map"])
        any_on_task = bool(self._page_watchers["taskmonitoring"])

        self.set_dynamic_tier("LocationListMsg", "fast" if any_on_map else "slow")
        self.set_dynamic_tier(
            "WorkflowInstanceListMsg", "fast" if any_on_task else "slow"
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
        while self._running:
            sock = self._gms.connect()
            if sock:
                # 1. Connected: Perform Startup Query (Once per connect)
                logger.info("Performing Startup Query (One-time)...")
                for msg_type in self.startup_msg_types:
                    self._gms.send_request(
                        msg_type, self.client_code, self.channel_id, {}
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
                logger.warning("GMS Session lost, retrying in 3s...")
                # Ensure it's disconnected properly
                self._gms.disconnect()
                if self._stop_event.wait(3):
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

    def _polling_loop(self, sock_ref):
        logger.info("Polling Loop Started")
        # Reset slow timer on start
        self._last_slow_query = 0

        while self._running and self._gms._sock == sock_ref:
            if self.auto_query:
                start_time = time.time()
                try:
                    now = time.time()

                    # 1. Fast Layer (1s Interval)
                    for msg_type in self.fast_msg_types:
                        # Skip if a similar request is pending to avoid flooding
                        if msg_type in self._gms.pending_requests:
                            continue
                        self._gms.send_request(
                            msg_type, self.client_code, self.channel_id, {}
                        )

                    # 2. Slow Layer (30s Interval)
                    if now - self._last_slow_query >= self.slow_query_interval:
                        self._last_slow_query = now
                        for msg_type in self.slow_msg_types:
                            if msg_type in self._gms.pending_requests:
                                continue
                            self._gms.send_request(
                                msg_type, self.client_code, self.channel_id, {}
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
