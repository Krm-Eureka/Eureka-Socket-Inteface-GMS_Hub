import psutil
import threading
import time
import asyncio
import mysql.connector
from loguru import logger
from app.core.config import settings


class SystemMonitor:
    """[BEHAVIOR] Monitors server (CPU, RAM) and MySQL performance/health"""

    def __init__(self, sio):
        self._sio = sio
        self._loop = None
        self._running = False
        self._thread = None
        self._stop_event = threading.Event()
        self._last_queries = 0
        self._last_check_time = time.time()
        self._is_busy = False  # Guard against overlapping health checks
        self.clients = {}  # {sid: {ip: str, connected_at: str}}

    def set_loop(self, loop):
        self._loop = loop

    def start(self):
        if self._running:
            return
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Health Monitor (System + MySQL) started.")

    def add_client(self, sid, ip):
        self.clients[sid] = {
            "ip": ip,
            "connected_at": time.strftime("%H:%M:%S"),
        }

    def remove_client(self, sid):
        if sid in self.clients:
            del self.clients[sid]

    def stop(self):
        self._running = False
        self._stop_event.set()

    def _get_mysql_stats(self):
        """Fetch comprehensive MySQL metrics"""
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
            default_stats["message"] = "DB_NAME not set in .env"
            return default_stats

        if settings.DB_PASS in ("your_password_here", ""):
            default_stats["status"] = "unconfigured"
            default_stats["message"] = "DB credentials not configured in .env"
            return default_stats

        stats = default_stats.copy()
        conn = None
        try:
            start_time = time.time()
            conn = mysql.connector.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASS,
                database=settings.DB_NAME,
                connect_timeout=2,
            )
            stats["latency_ms"] = round((time.time() - start_time) * 1000, 2)
            stats["status"] = "up"

            cursor = conn.cursor(dictionary=True)

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
                stats["qps"] = round(
                    (current_queries - self._last_queries) / time_diff, 2
                )
            self._last_queries = current_queries
            self._last_check_time = now

            # 2. Global Variables
            cursor.execute("SHOW GLOBAL VARIABLES LIKE 'max_connections'")
            max_conn_row = cursor.fetchone()
            if max_conn_row:
                stats["max_connections"] = int(max_conn_row["Value"])

            cursor.execute("SHOW GLOBAL VARIABLES LIKE 'version'")
            version_row = cursor.fetchone()
            if version_row:
                stats["version"] = version_row["Value"]

            # 3. DB Size
            cursor.execute(
                f"""
                SELECT SUM(data_length + index_length) / 1024 / 1024 AS size_mb 
                FROM information_schema.TABLES 
                WHERE table_schema = '{settings.DB_NAME}'
            """
            )
            size_row = cursor.fetchone()
            if size_row and size_row["size_mb"]:
                stats["db_size_mb"] = round(float(size_row["size_mb"]), 2)

            # 4. Buffer Pool Usage
            btn = int(status_map.get("Innodb_buffer_pool_pages_total", 0))
            bfn = int(status_map.get("Innodb_buffer_pool_pages_free", 0))
            if btn > 0:
                stats["buffer_pool_usage"] = round(((btn - bfn) / btn) * 100, 2)

            cursor.close()
        except Exception as e:
            stats["status"] = "down"
            stats["error"] = str(e)
        finally:
            if conn:
                conn.close()

        return stats

    def _run(self):
        while self._running:
            try:
                # Skip if a previous check is still running
                if self._is_busy:
                    if self._stop_event.wait(3):
                        break
                    continue

                self._is_busy = True
                try:
                    # 1. System Stats
                    cpu_usage = psutil.cpu_percent(interval=None)
                    ram = psutil.virtual_memory()

                    sys_stats = {
                        "cpu": cpu_usage,
                        "ram_percent": ram.percent,
                        "ram_used_gb": round(ram.used / (1024**3), 2),
                        "ram_total_gb": round(ram.total / (1024**3), 2),
                        "ram_free_gb": round(ram.available / (1024**3), 2),
                        "client_count": len(self.clients),
                        "clients": [
                            {"sid": sid, **info} for sid, info in self.clients.items()
                        ],
                    }

                    # 2. MySQL Stats
                    mysql_stats = self._get_mysql_stats()

                    # Emit Combined Health Data
                    health_packet = {"system": sys_stats, "mysql": mysql_stats}

                    if self._loop:
                        asyncio.run_coroutine_threadsafe(
                            self._sio.emit("health_stats", health_packet), self._loop
                        )
                finally:
                    self._is_busy = False

                if self._stop_event.wait(10):  # Health check interval (10s)
                    break
            except Exception as e:
                logger.error(f"Health Monitor Error: {e}")
                self._is_busy = False
                if self._stop_event.wait(10):
                    break
