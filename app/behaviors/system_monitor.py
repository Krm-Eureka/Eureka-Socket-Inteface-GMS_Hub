import psutil  # type: ignore[import]
import asyncio
import time
import datetime
import socket as _socket
import os as _os
from typing import Any, Dict, List, Optional
import pymysql  # type: ignore[import]
import pymysql.cursors  # type: ignore[import]
from loguru import logger  # type: ignore[import]
from app.core.config import settings  # type: ignore[import]
from app.services.log_service import write_daily_log as _log_daily  # type: ignore[import]


class SystemMonitor:
    """[BEHAVIOR] Monitors server (CPU, RAM) and MySQL performance/health using Asyncio"""

    def __init__(self, sio: Any, gms_client: Any = None) -> None:
        self._sio = sio
        self._gms_client = gms_client
        self._running: bool = False
        self._stop_event = None
        self._task: Optional[asyncio.Task] = None

        self._last_queries: int = 0
        self._last_check_time: float = time.time()
        self._is_busy: bool = False  # Guard against overlapping health checks
        self.clients: Dict[str, Dict[str, str]] = {}  # {sid: {ip, hostname, connected_at}}
        self._daily: Dict[str, Any] = self._blank_daily()
        self._last_log_date: Optional[str] = None  # เขียน daily summary 1 ครั้งต่อวัน

    @staticmethod
    def _blank_daily() -> Dict[str, Any]:
        """Return a fresh min/max/sum/count tracking dict."""
        return {
            "cpu_min": None,
            "cpu_max": None,
            "cpu_sum": 0.0,
            "ram_min": None,
            "ram_max": None,
            "ram_sum": 0.0,
            "db_latency_min": None,
            "db_latency_max": None,
            "qps_max": None,
            "db_errors": 0,
            "samples": 0,
        }

    def get_daily_summary(self) -> dict:
        """Return a human-readable daily summary of min/max stats."""
        d = self._daily
        n = max(d["samples"], 1)
        return {
            "cpu_avg": round(d["cpu_sum"] / n, 1) if d["samples"] else 0,
            "cpu_min": d["cpu_min"] if d["cpu_min"] is not None else 0,
            "cpu_max": d["cpu_max"] if d["cpu_max"] is not None else 0,
            "ram_avg": round(d["ram_sum"] / n, 1) if d["samples"] else 0,
            "ram_min": d["ram_min"] if d["ram_min"] is not None else 0,
            "ram_max": d["ram_max"] if d["ram_max"] is not None else 0,
            "db_latency_min": d["db_latency_min"] if d["db_latency_min"] is not None else 0,
            "db_latency_max": d["db_latency_max"] if d["db_latency_max"] is not None else 0,
            "qps_max": d["qps_max"] if d["qps_max"] is not None else 0,
            "db_errors": d["db_errors"],
            "samples": d["samples"],
        }

    def reset_daily_stats(self):
        """Reset daily tracking counters (called at midnight)."""
        self._daily = self._blank_daily()

    def _write_daily_log(self, snapshot: dict, label: str = "DAILY_SUMMARY"):
        """Delegate to log_service — keeps system_monitor clean."""
        _log_daily(snapshot, self.get_daily_summary(), label=label)

    async def start(self) -> None:
        if self._running:
            return
        
        if self._stop_event is None:
            self._stop_event = asyncio.Event()

        self._running = True
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run())
        logger.info("Health Monitor (Async) started.")

    async def add_client(self, sid: str, ip: str):
        # Initialize with 'Resolving...' and then use a task to get the actual hostname
        # to avoid blocking the main Socket.IO event loop.
        self.clients[sid] = {
            "ip": ip,
            "hostname": "Resolving...",
            "connected_at": time.strftime("%H:%M:%S"),
        }
        asyncio.create_task(self._resolve_hostname_async(sid, ip))

    async def _resolve_hostname_async(self, sid: str, ip: str):
        try:
            # Use run_in_executor for DNS resolution (blocking OS call)
            loop = asyncio.get_running_loop()
            
            def _lookup(target_ip: str) -> str:
                return _socket.gethostbyaddr(target_ip)[0]

            h = await loop.run_in_executor(None, _lookup, ip)
            if sid in self.clients:
                self.clients[sid]["hostname"] = h
        except Exception:
            # If resolution fails, fallback to IP
            if sid in self.clients:
                self.clients[sid]["hostname"] = ip

    def remove_client(self, sid: str) -> None:
        self.clients.pop(sid, None)

    async def stop(self):
        self._running = False
        self._stop_event.set()
        task = self._task
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Health Monitor stopped.")

    def _get_mysql_stats_blocking(self):
        """Fetch MySQL metrics (blocking core)"""
        default_stats = {
            "status": "down",
            "uptime": 0,
            "version": "Unknown",
            "threads_connected": 0,
            "threads_running": 0,
            "max_connections": 0,
            "aborted_connects": 0,
            "slow_queries": 0,
            "qps": 0,
            "latency_ms": 0,
            "db_size_mb": 0,
            "buffer_pool_usage": 0,
            "error": None,
        }

        if not settings.DB_NAME or settings.DB_NAME in ("your_db_name_here", ""):
            default_stats["status"] = "unconfigured"
            return default_stats

        if settings.DB_PASS in ("your_password_here", ""):
            default_stats["status"] = "unconfigured"
            return default_stats

        stats = default_stats.copy()
        conn = None
        try:
            start_time = time.time()
            conn = pymysql.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASS,
                database=settings.DB_NAME,
                connect_timeout=2,
                cursorclass=pymysql.cursors.DictCursor,
            )
            duration = time.time() - start_time
            stats["latency_ms"] = round(float(duration * 1000), 2)
            stats["status"] = "up"

            cursor = conn.cursor()

            # 1. Global Status
            cursor.execute("SHOW GLOBAL STATUS")
            status_rows = cursor.fetchall()
            status_map = {row["Variable_name"]: row["Value"] for row in status_rows}

            stats["uptime"] = int(status_map.get("Uptime", 0))
            stats["threads_connected"] = int(status_map.get("Threads_connected", 0))
            stats["threads_running"] = int(status_map.get("Threads_running", 0))
            stats["aborted_connects"] = int(status_map.get("Aborted_connects", 0))
            stats["slow_queries"] = int(status_map.get("Slow_queries", 0))

            # Calculate QPS
            current_queries = int(status_map.get("Queries", 0))
            now = time.time()
            time_diff = now - self._last_check_time
            if time_diff > 0:
                stats["qps"] = round(float((current_queries - self._last_queries) / time_diff), 2)
            self._last_queries = current_queries
            self._last_check_time = now

            # 2. Global Variables
            cursor.execute("SHOW GLOBAL VARIABLES LIKE 'max_connections'")
            res = cursor.fetchone()
            if res: stats["max_connections"] = int(res["Value"])

            cursor.execute("SHOW GLOBAL VARIABLES LIKE 'version'")
            res = cursor.fetchone()
            if res: stats["version"] = res["Value"]

            # 3. DB Size
            cursor.execute(
                f"""
                SELECT SUM(data_length + index_length) / 1024 / 1024 AS size_mb 
                FROM information_schema.TABLES 
                WHERE table_schema = '{settings.DB_NAME}'
            """
            )
            res = cursor.fetchone()
            if res and res["size_mb"]: stats["db_size_mb"] = round(float(res["size_mb"]), 2)

            # 4. Buffer Pool Usage
            btn = int(status_map.get("Innodb_buffer_pool_pages_total", 0))
            bfn = int(status_map.get("Innodb_buffer_pool_pages_free", 0))
            if btn > 0: stats["buffer_pool_usage"] = round(float(((btn - bfn) / btn) * 100), 2)

            cursor.close()
        except Exception as e:
            stats["status"] = "down"
            stats["error"] = str(e)
        finally:
            if conn:
                conn.close()

        return stats

    async def _run(self):
        while self._running:
            try:
                # Skip if a previous check is still running
                if self._is_busy:
                    try:
                        await asyncio.wait_for(self._stop_event.wait(), timeout=3.0)
                        break
                    except asyncio.TimeoutError:
                        continue

                self._is_busy = True
                try:
                    # 1. System Stats
                    cpu_usage = psutil.cpu_percent(interval=None)
                    ram = psutil.virtual_memory()

                    # Windows uses C:\ not /, use abspath to get correct drive root
                    disk_path = _os.path.abspath("/")
                    disk = psutil.disk_usage(disk_path)

                    # cpu_temp: supported on Linux only (returns 0 on Windows)
                    cpu_temp = 0
                    try:
                        temps = psutil.sensors_temperatures()
                        if temps:
                            all_temps = [t.current for group in temps.values() for t in group]
                            if all_temps: cpu_temp = round(max(all_temps), 1)
                    except (AttributeError, OSError):
                        pass  # Not supported on Windows

                    sys_stats = {
                        "cpu": cpu_usage,
                        "ram_percent": ram.percent,
                        "ram_used_gb": round(ram.used / (1024**3), 2),
                        "ram_total_gb": round(ram.total / (1024**3), 2),
                        "ram_free_gb": round(ram.available / (1024**3), 2),
                        "disk_percent": disk.percent,
                        "disk_used_gb": round(disk.used / (1024**3), 2),
                        "disk_total_gb": round(disk.total / (1024**3), 2),
                        "hostname": _socket.gethostname(),
                        "cpu_temp": cpu_temp,
                        "client_count": len(self.clients),
                        "clients": [{"sid": sid, **info} for sid, info in self.clients.items()],
                    }

                    # 2. MySQL Stats (Run blocking DB call in executor)
                    loop = asyncio.get_running_loop()
                    mysql_stats = await loop.run_in_executor(None, self._get_mysql_stats_blocking)

                    # --- Track daily min/max ---
                    d = self._daily
                    d["samples"] += 1
                    # CPU
                    d["cpu_sum"] += cpu_usage
                    d["cpu_min"] = cpu_usage if d["cpu_min"] is None else min(d["cpu_min"], cpu_usage)
                    d["cpu_max"] = cpu_usage if d["cpu_max"] is None else max(d["cpu_max"], cpu_usage)
                    # RAM
                    d["ram_sum"] += ram.percent
                    d["ram_min"] = ram.percent if d["ram_min"] is None else min(d["ram_min"], ram.percent)
                    d["ram_max"] = ram.percent if d["ram_max"] is None else max(d["ram_max"], ram.percent)
                    # DB
                    if mysql_stats["status"] == "up":
                        lat = mysql_stats["latency_ms"]
                        qps = mysql_stats["qps"]
                        d["db_latency_min"] = lat if d["db_latency_min"] is None else min(d["db_latency_min"], lat)
                        d["db_latency_max"] = lat if d["db_latency_max"] is None else max(d["db_latency_max"], lat)
                        d["qps_max"] = qps if d["qps_max"] is None else max(d["qps_max"], qps)
                    elif mysql_stats["status"] == "down":
                        d["db_errors"] += 1
                    # ----------------------------

                    # Emit Combined Health Data
                    health_packet = {
                        "system": sys_stats,
                        "mysql": mysql_stats,
                        "gms": self._gms_client.gms_stats if self._gms_client else {},
                    }

                    logger.debug(f"[Health] Emitting health_stats packet: {health_packet}")
                    await self._sio.emit("health_stats", health_packet)

                    # 📋 เขียน Daily Summary 1 ครั้งต่อวัน (เมื่อวันเปลี่ยน = ตีหนึ่ง/เที่ยงคืน)
                    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
                    if self._last_log_date and self._last_log_date != today_str:
                        # วันเปลี่ยนแล้ว — เขียนสรุปของเมื่อวัน
                        try:
                            self._write_daily_log(health_packet, label="DAILY_SUMMARY")
                        except Exception as log_err:
                            logger.warning(f"[DailyLog] Write failed: {log_err}")
                    self._last_log_date = today_str

                finally:
                    self._is_busy = False

                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=10.0)  # Health check interval (10s)
                    break
                except asyncio.TimeoutError:
                    pass
            except asyncio.CancelledError:
                logger.info("Health Monitor loop cancelled.")
                break
            except Exception as e:
                logger.error(f"Health Monitor Error: {e}")
                self._is_busy = False
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=10.0)
                    break
                except asyncio.TimeoutError:
                    pass
        logger.info("Health Monitor Loop Ended")
