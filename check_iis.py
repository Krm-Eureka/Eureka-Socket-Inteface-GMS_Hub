"""
check_iis.py — ESIG HUB IIS Deployment Diagnostic
รันสคริปต์นี้บนเครื่อง Target ก่อน deploy เพื่อตรวจสอบว่า environment พร้อมหรือไม่

Usage:
    py check_iis.py
    py check_iis.py --port 1244          # ระบุ port ที่ต้องการตรวจ
    py check_iis.py --env-file .env.prod # ระบุ .env file อื่น
    py check_iis.py --skip-import        # ข้ามการ import main.py (เร็วกว่า)
"""

import argparse
import importlib.util
import os
import socket
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS = os.path.join(BASE_DIR, "requirements.txt")

# ─── Color Helpers ─────────────────────────────────────────────────────────────
USE_COLOR = sys.platform != "win32" or os.environ.get("TERM")


def colored(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def ok(msg, detail=""):
    d = f"  -> {detail}" if detail else ""
    print(f"  [OK]   {msg}{d}")


def fail(msg, detail=""):
    d = f"  -> {detail}" if detail else ""
    print(f"  [FAIL] {msg}{d}")


def warn(msg, detail=""):
    d = f"  -> {detail}" if detail else ""
    print(f"  [WARN] {msg}{d}")


def info(msg):
    print(f"  [INFO] {msg}")


def sep():
    print("  " + "-" * 56)


# ─── Checks ────────────────────────────────────────────────────────────────────
def check_python_version():
    v = sys.version_info
    v_str = sys.version.split()[0]
    info(f"Python {v_str}  -> {sys.executable}")
    if v.major == 3 and v.minor >= 10:
        ok(f"Python {v_str}")
        return True, v_str
    else:
        fail(f"Python {v_str}", "Requires Python 3.10+")
        return False, v_str


def check_packages(req_file=None):
    """Check if packages in requirements.txt are installed"""
    if not req_file:
        req_file = os.path.join(BASE_DIR, "requirements.txt")

    if not os.path.exists(req_file):
        warn("requirements.txt NOT FOUND - skipping packages check")
        return True

    # Mapping package name -> import name
    import_map = {
        "python-socketio": "socketio",
        "python-dotenv": "dotenv",
        "pymysql": "pymysql",
        "gunicorn": "gunicorn",
    }

    all_ok = True
    with open(req_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Extract package name from specifier
            pkg_raw = (
                line.split("==")[0].split(">=")[0].split("<=")[0].split("[")[0].strip()
            )
            import_name = import_map.get(pkg_raw, pkg_raw.replace("-", "_"))

            try:
                top_mod = import_name.split(".")[0]
                spec = importlib.util.find_spec(top_mod)
                if spec is None:
                    raise ImportError(f"{top_mod} not found")
                ok(pkg_raw)
            except (ImportError, ModuleNotFoundError, ValueError):
                fail(pkg_raw, "Not installed - run: pip install -r requirements.txt")
                all_ok = False
    return all_ok


def check_env_file(env_file):
    """Check if .env exists and critical keys are configured"""
    if not os.path.exists(env_file):
        fail(f"{env_file} NOT FOUND", "Run: copy .env.example .env and edit it")
        return False, {}

    env_vals = {}
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env_vals[k.strip()] = v.strip()

    ok(f"{env_file} found")
    required = {
        "GMS_IP": "GMS IP Address",
        "GMS_PORT": "GMS Port",
        "DB_HOST": "MySQL Host",
        "DB_USER": "MySQL User",
        "DB_NAME": "MySQL Database Name",
    }
    placeholder_vals = {"your_password_here", "change_me", "your_db_name_here", ""}

    all_ok = True
    for key, label in required.items():
        val = env_vals.get(key, "")
        if not val or val in placeholder_vals:
            warn(f"  {key}", f"NOT CONFIGURED ({label})")
            all_ok = False
        else:
            info(
                f"  {key} = {'****' if 'PASS' in key or 'pass' in key.lower() else val}"
            )

    return all_ok, env_vals


def check_network(env_vals):
    """Test GMS TCP and MySQL connectivity"""
    all_ok = True

    gms_ip = env_vals.get("GMS_IP", "")
    gms_port = int(env_vals.get("GMS_PORT", "24245"))
    if gms_ip:
        try:
            s = socket.create_connection((gms_ip, gms_port), timeout=2)
            s.close()
            ok(f"GMS TCP {gms_ip}:{gms_port}", "reachable")
        except Exception as e:
            warn(f"GMS TCP {gms_ip}:{gms_port}", f"{e}")
            info(
                "    (Standard behavior if GMS is offline - will retry on START SERVICE)"
            )
            # Not counted as FAIL because GMS might not be started yet
    else:
        warn("GMS_IP not set in .env")

    db_name = env_vals.get("DB_NAME", "")
    db_pass = env_vals.get("DB_PASS", "")
    if db_name and db_pass and db_pass not in {"your_password_here", ""}:
        try:
            import pymysql

            db_host = env_vals.get("DB_HOST", "127.0.0.1")
            db_port = int(env_vals.get("DB_PORT", "3306"))
            db_user = env_vals.get("DB_USER", "root")
            conn = pymysql.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_pass,
                database=db_name,
                connect_timeout=3,
            )
            conn.close()
            ok(f"MySQL {db_host}:{db_port}/{db_name}", "connected")
        except Exception as e:
            fail(f"MySQL {db_host}:{db_port}/{db_name}", str(e))
            all_ok = False
    else:
        warn("MySQL", "Skipped (DB_NAME or DB_PASS not set)")

    return all_ok


def check_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(("127.0.0.1", port))
    if result == 0:
        warn(f"Port {port}", "Already in use - Stop existing process or check IIS site")
        return False
    else:
        ok(f"Port {port}", "Available")
        return True


def check_logs_writable():
    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    test_file = os.path.join(logs_dir, "._write_test.tmp")
    try:
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        ok("logs/ write permission")
        return True
    except PermissionError as e:
        fail("logs/ write permission", str(e))
        info('    Fix: icacls "<path>" /grant "IIS_IUSRS:(OI)(CI)M" /T')
        return False


def check_dirs():
    all_ok = True
    for d in ["static", "templates", "app"]:
        path = os.path.join(BASE_DIR, d)
        if os.path.isdir(path):
            ok(f"Folder '{d}/'")
        else:
            fail(f"Folder '{d}/' NOT FOUND", "Incomplete deployment")
            all_ok = False
    return all_ok


def check_webconfig():
    wc = os.path.join(BASE_DIR, "web.config")
    if not os.path.exists(wc):
        warn("web.config NOT FOUND", "Only required for IIS deployment")
        return True  # standalone run does not need it

    with open(wc, encoding="utf-8") as f:
        content = f.read()

    all_ok = True
    checks = [
        ("py.exe" in content or "python.exe" in content, "processPath -> Python"),
        ("PYTHONUNBUFFERED" in content, "PYTHONUNBUFFERED=1 (realtime logs)"),
        ("startupTimeLimit" in content, "startupTimeLimit configured"),
        ("startupRetryCount" in content, "startupRetryCount configured"),
        ("websockets" in content, "--ws websockets argument found"),
    ]
    for passed, label in checks:
        if passed:
            ok(label)
        else:
            warn(label, "Missing in web.config")
    return all_ok


def check_main_importable():
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    os.environ.setdefault("BFF_RELOAD", "false")
    try:
        spec = importlib.util.spec_from_file_location(
            "main_check", os.path.join(BASE_DIR, "main.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ok("main.py import successful - No syntax errors")
        return True
    except Exception as e:
        fail("main.py import failed", str(e))
        return False


# ─── Main ──────────────────────────────────────────────────────────────────────
def run_all_checks(env_file=".env", target_port=1244, skip_import=False):
    """Run all checks and return results dictionary + env_vals"""
    results = {}

    # 1. Python Version
    v_passed, v_info = check_python_version()
    results["python"] = v_passed

    # 2. Packages
    results["packages"] = check_packages(REQUIREMENTS)

    # 3. .env
    env_ok, env_vals = check_env_file(env_file)
    results["env"] = env_ok

    # 4. Network
    results["network"] = check_network(env_vals)

    # 5. Port
    results["port"] = check_port_available(target_port)

    # 6. Logs
    results["logs"] = check_logs_writable()

    # 7. Dirs
    results["dirs"] = check_dirs()

    # 8. WebConfig (Optional for GUI run, but good to check)
    results["webconfig"] = check_webconfig()

    # 9. Import
    if skip_import:
        results["import"] = True
    else:
        results["import"] = check_main_importable()

    return results, env_vals


def main():
    parser = argparse.ArgumentParser(description="ESIG HUB Standalone Diagnostic")
    parser.add_argument(
        "--port", type=int, default=1244, help="Port to check (default: 1244)"
    )
    parser.add_argument(
        "--env-file", default=".env", help="Path to .env file (default: .env)"
    )
    parser.add_argument(
        "--skip-import", action="store_true", help="Skip main.py import check"
    )
    args = parser.parse_args()

    banner("ESIG HUB - Environment Diagnostic")

    results, _ = run_all_checks(args.env_file, args.port, args.skip_import)

    sep()
    banner("SUMMARY")

    label_map = {
        "python": "Python Version",
        "packages": "Required Packages",
        "env": "Environment File (.env)",
        "network": "Network / DB Connectivity",
        "port": "Port Availability",
        "logs": "Logs Directory Permission",
        "dirs": "Project Directories",
        "webconfig": "web.config (IIS Optional)",
        "import": "main.py Import Test",
    }

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for key, val in results.items():
        status = "PASSED" if val else "FAILED"
        print(f"  {status:6}  {label_map.get(key, key)}")

    print()
    if passed == total:
        print(f"  ALL PASSED ({passed}/{total}) - Ready for IIS deployment!")
    else:
        print(
            f"  FAILED {total - passed}/{total} - Fix the FAILED items before deployment"
        )
    print("=" * 60)
    print()

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
