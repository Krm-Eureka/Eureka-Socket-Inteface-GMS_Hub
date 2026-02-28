# check_health.py — ตรวจสอบระบบก่อน Start ESIG
# รัน: python check_health.py
import os
import socket
import sys
import platform
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # ถ้า dotenv ยังไม่ได้ติดตั้ง ใช้ os.environ แทน

print("=" * 55)
print("🔍  ESIG HUB — Pre-Start Health Check")
print("=" * 55)

all_ok = True
warnings = []


# ------------------------------------------------------------------
# 1. Python Version
# ------------------------------------------------------------------
py = platform.python_version_tuple()
if int(py[0]) >= 3 and int(py[1]) >= 10:
    print(f"✅  Python {platform.python_version()} — OK")
else:
    print(f"❌  Python {platform.python_version()} — ต้องใช้ 3.10 ขึ้นไป")
    all_ok = False


# ------------------------------------------------------------------
# 2. .env file
# ------------------------------------------------------------------
if Path(".env").exists():
    print("✅  .env file — Found")
else:
    print("❌  .env file — ไม่พบ! กรุณาสร้างไฟล์ .env ก่อน (ดู SETUP.GUIDE.md)")
    all_ok = False


# ------------------------------------------------------------------
# 3. Required Python Packages
# ------------------------------------------------------------------
required_packages = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "python-socketio": "socketio",
    "loguru": "loguru",
    "python-dotenv": "dotenv",
}
for display_name, import_name in required_packages.items():
    try:
        __import__(import_name)
        print(f"✅  Package '{display_name}' — Installed")
    except ImportError:
        print(f"❌  Package '{display_name}' — Missing!")
        print(f"    แก้ไข: pip install -r requirements.txt")
        all_ok = False


# ------------------------------------------------------------------
# 4. Port Availability
# ------------------------------------------------------------------
bff_port = int(os.getenv("BFF_PORT", "9000"))
try:
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    test_sock.bind(("0.0.0.0", bff_port))
    test_sock.close()
    print(f"✅  Port {bff_port} — Available")
except OSError:
    # อาจ ESIG รันอยู่แล้ว — ไม่ใช่ Error แต่เป็น warning
    warnings.append(f"⚠️   Port {bff_port} — ถูกใช้งานอยู่ (ถ้า ESIG รันอยู่แล้ว = ปกติ)")
    print(f"⚠️   Port {bff_port} — In Use (อาจ ESIG รันอยู่แล้ว)")


# ------------------------------------------------------------------
# 5. GMS Network Connectivity
# ------------------------------------------------------------------
gms_ip = os.getenv("GMS_IP", "10.80.227.230")
gms_port = int(os.getenv("GMS_PORT", "24245"))
try:
    sock = socket.create_connection((gms_ip, gms_port), timeout=3)
    sock.close()
    print(f"✅  GMS {gms_ip}:{gms_port} — Reachable")
except (socket.timeout, ConnectionRefusedError, OSError) as e:
    warnings.append(
        f"⚠️   GMS {gms_ip}:{gms_port} ไม่ตอบสนอง ({e})\n"
        f"    ระบบยังสามารถ Start ได้ และจะ retry เชื่อมต่ออัตโนมัติ"
    )
    print(f"⚠️   GMS {gms_ip}:{gms_port} — Unreachable (จะ retry อัตโนมัติหลัง Start)")


# ------------------------------------------------------------------
# 6. Log Directory
# ------------------------------------------------------------------
log_dir = Path("logs")
if not log_dir.exists():
    log_dir.mkdir(parents=True)
    print("✅  logs/ directory — Created")
else:
    print("✅  logs/ directory — Exists")


# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
print("=" * 55)

if warnings:
    print("\n📋 WARNINGS (ระบบยังทำงานได้แต่ควรตรวจสอบ):")
    for w in warnings:
        print(f"   {w}")
    print()

if all_ok:
    print("🟢  ผ่านทุกข้อ! พร้อม Start ESIG Server")
    print(f"    รัน: python main.py   หรือ   .\\ESIG.exe")
    sys.exit(0)
else:
    print("🔴  มีข้อผิดพลาด — กรุณาแก้ไขก่อน Start")
    print("    ดูรายละเอียดใน SETUP.GUIDE.md")
    sys.exit(1)
