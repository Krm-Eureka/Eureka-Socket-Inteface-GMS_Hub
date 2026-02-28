import os
from datetime import datetime
from pathlib import Path

# Base directory for logs
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE_DIR / "logs" / "config_edits"


def log_config_change(user_ip: str, section: str, action: str, details: str = ""):
    """
    Log a configuration change to a monthly rolling file.
    Only creates the directory/file when a change actually occurs.
    """
    try:
        # 1. Ensure log directory exists
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        # 2. Generate monthly filename: config_changes_YYYY-MM.log
        now = datetime.now()
        filename = f"config_changes_{now.strftime('%Y-%m')}.log"
        log_path = LOG_DIR / filename

        # 3. Format the log entry
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] IP: {user_ip} | Section: {section} | Action: {action} | {details}\n"

        # 4. Append to file (creates if not exists)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

    except Exception as e:
        # Fallback to standard logger if this fails
        from loguru import logger

        logger.error(f"Failed to write config change log: {e}")
