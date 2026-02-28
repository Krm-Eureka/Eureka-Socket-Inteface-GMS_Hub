"""
log_service.py — Centralized file logging for ESIG HUB
ใช้ร่วมกันระหว่าง gms_client, system_monitor และ services อื่นๆ

ไฟล์ที่ผลิต:
  logs/debug_YYYY-MM-DD.log   ← GMS TX/RX messages + RTT
  logs/log_daily_YYYY-MM-DD.log ← Daily health summary (1 entry/วัน)
"""

import datetime
from pathlib import Path
from loguru import logger
import os
from pathlib import Path
from loguru import logger


# กำหนด logs directory (ถ้าถูกเรียกผ่าน Launcher .exe จะใช้ ESIG_BASE_DIR)
_base_dir = os.environ.get("ESIG_BASE_DIR", ".")
_LOG_DIR = Path(_base_dir) / "logs"


def _ensure_log_dir():
    _LOG_DIR.mkdir(exist_ok=True)


def _today() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d")


def _now_ms() -> str:
    """Timestamp พร้อม milliseconds  เช่น 08:32:01.457"""
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]


# ------------------------------------------------------------------
# DEBUG LOG — GMS TX/RX per message
# ------------------------------------------------------------------


def write_debug_log(direction: str, msg_type: str, body, elapsed_ms):
    """
    เขียน 1 บรรทัดต่อ message ลง logs/debug_YYYY-MM-DD.log

    Args:
        direction : "TX" หรือ "RX"
        msg_type  : เช่น "RobotInfoMsg", "HeartbeatMsg"
        body      : payload ที่ส่ง/รับ (dict หรือ list)
        elapsed_ms: RTT เป็น ms (None ถ้าเป็น TX หรือไม่ทราบ)
    """
    try:
        _ensure_log_dir()
        log_path = _LOG_DIR / f"debug_{_today()}.log"
        now_str = _now_ms()

        if direction == "TX":
            # แสดง body โดยตัด msgType ออก (ซ้ำซ้อน)
            if isinstance(body, dict):
                body_info = {k: v for k, v in body.items() if k != "msgType"}
            else:
                body_info = body
            line = f"[{now_str}] ➡️  TX  {msg_type:<35} | BODY: {body_info}"

        else:  # RX
            rtt = f"{elapsed_ms}ms" if elapsed_ms is not None else "??ms"
            if isinstance(body, list):
                count = len(body)
                preview = body[:5]
                body_str = f"[{count} items] first 5: {preview}"
            elif isinstance(body, dict):
                body_str = str(body)[:300]
            else:
                body_str = str(body)[:200]
            line = f"[{now_str}] ⬅️  RX  {msg_type:<35} | RTT: {rtt:>8} | {body_str}"

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    except Exception as e:
        logger.warning(f"[LogService] write_debug_log failed: {e}")


# ------------------------------------------------------------------
# DAILY HEALTH LOG — snapshot จาก SystemMonitor
# ------------------------------------------------------------------


def write_daily_log(snapshot: dict, daily_summary: dict, label: str = "DAILY_SUMMARY"):
    """
    เขียนสรุปสุขภาพระบบลง logs/log_daily_YYYY-MM-DD.log
    ปกติเรียก 1 ครั้ง/วัน ตอนเที่ยงคืน (เมื่อวันเปลี่ยน)

    Args:
        snapshot     : health_packet จาก SystemMonitor._run
                       {"system": {...}, "mysql": {...}, "gms": {...}}
        daily_summary: ผลจาก SystemMonitor.get_daily_summary()
        label        : หัวข้อ entry เช่น "DAILY_SUMMARY"
    """
    try:
        _ensure_log_dir()
        today = _today()
        log_path = _LOG_DIR / f"log_daily_{today}.log"
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sys_s = snapshot.get("system", {})
        db_s = snapshot.get("mysql", {})
        gms_s = snapshot.get("gms", {})
        daily = daily_summary

        lines = [
            f"[{now_str}] === {label} ===",
            f"  CPU      : {sys_s.get('cpu', '-')}%"
            f"  (day avg={daily.get('cpu_avg', '-')}%"
            f"  min={daily.get('cpu_min', '-')}%"
            f"  max={daily.get('cpu_max', '-')}%)",
            f"  RAM      : {sys_s.get('ram_percent', '-')}%"
            f"  ({sys_s.get('ram_used_gb', '-')}/{sys_s.get('ram_total_gb', '-')} GB)"
            f"  (day min={daily.get('ram_min', '-')}%"
            f"  max={daily.get('ram_max', '-')}%)",
            f"  DISK     : {sys_s.get('disk_percent', '-')}%"
            f"  ({sys_s.get('disk_used_gb', '-')}/{sys_s.get('disk_total_gb', '-')} GB)",
            f"  DB       : {db_s.get('status', '-')}"
            f"  latency={db_s.get('latency_ms', '-')}ms"
            f"  qps={db_s.get('qps', '-')}"
            f"  errors_today={daily.get('db_errors', '-')}",
            f"  GMS      : connected={gms_s.get('connected', '-')}"
            f"  rx={gms_s.get('rx_count', '-')}"
            f"  tx={gms_s.get('tx_count', '-')}",
            f"  CLIENTS  : {sys_s.get('client_count', 0)} connected",
            f"  SAMPLES  : {daily.get('samples', '-')} since midnight",
            "",
        ]

        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.debug(f"[LogService] Written {label} to {log_path}")

    except Exception as e:
        logger.warning(f"[LogService] write_daily_log failed: {e}")
