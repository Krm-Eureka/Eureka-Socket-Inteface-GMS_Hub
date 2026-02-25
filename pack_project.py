"""
pack_project.py — ESIG HUB Offline Deployment Packer
รันบนเครื่อง Dev (มีเน็ต) เพื่อ:
  1. Download Python packages สำหรับ offline install
  2. สร้าง ESIG_HUB.tar.gz พร้อม packages ทุกตัว

Usage:
    py pack_project.py
    py pack_project.py --skip-download     # ข้าม pip download (ถ้ามี packages_offline แล้ว)
    py pack_project.py --output my.tar.gz  # ระบุชื่อไฟล์ output
"""

import argparse
import os
import subprocess
import sys
import tarfile
import time

# ─── Config ───────────────────────────────────────────────────────────────────
DEFAULT_OUTPUT = "ESIG_HUB.tar.gz"
PACKAGES_DIR = "packages_offline"
REQUIREMENTS = "requirements.txt"

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "logs",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    ".gemini",
}
EXCLUDE_EXT = {".pyc", ".pyo", ".log", ".tmp"}


def banner(msg: str):
    print(f"\n{'─' * 60}")
    print(f"  {msg}")
    print(f"{'─' * 60}")


def download_packages(requirements: str, output_dir: str):
    """Download packages จาก PyPI ลงโฟลเดอร์ offline"""
    banner(f"📦 Downloading packages → {output_dir}/")
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "-r",
        requirements,
        "-d",
        output_dir,
    ]
    print(f"  Command: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(
            "\n  ❌ pip download ล้มเหลว — ตรวจสอบ internet connection และ requirements.txt"
        )
        sys.exit(1)
    print(f"\n  ✅ Download เสร็จแล้ว → {output_dir}/")


def should_exclude(path: str, packages_dir: str) -> bool:
    """ตรวจว่า path นี้ควร exclude ออกจาก archive"""
    parts = path.replace("\\", "/").split("/")
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
        # ข้าม packages_offline ที่ root (จะเพิ่มทีหลังแยก)
        if part == packages_dir and parts[0] == packages_dir:
            return True
    _, ext = os.path.splitext(path)
    if ext in EXCLUDE_EXT:
        return True
    # ข้าม .tar.gz files
    if path.endswith(".tar.gz") or path.endswith(".zip"):
        return True
    return False


def create_archive(output_file: str, packages_dir: str):
    """สร้าง .tar.gz รวมทุก file + packages_offline"""
    banner(f"🗜  Creating archive → {output_file}")
    base_dir = os.path.abspath(".")
    file_count = 0
    start = time.time()

    with tarfile.open(output_file, "w:gz") as tar:
        # เดิน directory ปัจจุบัน
        for root, dirs, files in os.walk(base_dir):
            rel_root = os.path.relpath(root, base_dir)

            # กรอง dir ที่ต้องการ exclude
            dirs[:] = [
                d
                for d in dirs
                if d not in EXCLUDE_DIRS
                and not d.startswith(".")
                and not (d == packages_dir and rel_root == ".")  # จะเพิ่มทีหลัง
            ]

            for file in files:
                abs_file = os.path.join(root, file)
                rel_file = os.path.relpath(abs_file, base_dir).replace("\\", "/")

                if should_exclude(rel_file, packages_dir):
                    continue

                tar.add(abs_file, arcname=rel_file)
                file_count += 1
                if file_count % 50 == 0:
                    print(f"  ... {file_count} files packed", end="\r")

        # เพิ่ม packages_offline แยกต่างหาก
        if os.path.isdir(packages_dir):
            print(f"\n  Adding {packages_dir}/ ...")
            pkg_count = 0
            for root, _, files in os.walk(packages_dir):
                for file in files:
                    abs_file = os.path.join(root, file)
                    rel_file = os.path.relpath(abs_file, base_dir).replace("\\", "/")
                    tar.add(abs_file, arcname=rel_file)
                    pkg_count += 1
            print(f"  ✅ Added {pkg_count} package files")

    elapsed = time.time() - start
    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"\n  ✅ Done: {output_file}")
    print(
        f"     Files: {file_count:,}  |  Size: {size_mb:.1f} MB  |  Time: {elapsed:.1f}s"
    )


def verify_archive(output_file: str):
    """แสดงรายการไฟล์สำคัญใน archive"""
    banner("🔍 Verifying archive contents")
    critical = {"main.py", "web.config", "requirements.txt", ".env.example"}
    found = set()

    with tarfile.open(output_file, "r:gz") as tar:
        members = tar.getnames()
        for name in members:
            basename = os.path.basename(name)
            if basename in critical:
                found.add(basename)
        pkg_files = [m for m in members if m.startswith(PACKAGES_DIR + "/")]
        print(f"  Packages: {len(pkg_files)} files in {PACKAGES_DIR}/")

    for f in sorted(critical):
        status = "✅" if f in found else "❌"
        print(f"  {status} {f}")


def main():
    parser = argparse.ArgumentParser(description="ESIG HUB Offline Deployment Packer")
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output filename (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="ข้าม pip download (ใช้ packages_offline ที่มีอยู่)",
    )
    parser.add_argument(
        "--packages-dir",
        default=PACKAGES_DIR,
        help=f"โฟลเดอร์เก็บ packages (default: {PACKAGES_DIR})",
    )
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  ESIG HUB — Offline Deployment Packer")
    print("=" * 60)
    print(f"  Output   : {args.output}")
    print(f"  Packages : {args.packages_dir}/")

    if not os.path.exists(REQUIREMENTS):
        print(f"\n  ❌ ไม่พบ {REQUIREMENTS} — รันจาก root ของ project")
        sys.exit(1)

    # Step 1: Download packages
    if not args.skip_download:
        download_packages(REQUIREMENTS, args.packages_dir)
    else:
        if os.path.isdir(args.packages_dir):
            pkg_count = sum(len(f) for _, _, f in os.walk(args.packages_dir))
            print(f"\n  ⏭  Skip download — ใช้ {args.packages_dir}/ ({pkg_count} files)")
        else:
            print(
                f"\n  ⚠️  --skip-download แต่ไม่พบ {args.packages_dir}/ — กำลัง download ใหม่..."
            )
            download_packages(REQUIREMENTS, args.packages_dir)

    # Step 2: Create archive
    create_archive(args.output, args.packages_dir)

    # Step 3: Verify
    verify_archive(args.output)

    # Step 4: Instructions
    print()
    print("=" * 60)
    print("  🎉 พร้อม Deploy!")
    print("=" * 60)
    print(
        f"""
  ขั้นตอนต่อไป:
  1. Copy ไฟล์เหล่านี้ไป USB/Network Share:
       {args.output}
       python-3.10.x-amd64.exe  (ถ้าเครื่อง target ยังไม่มี Python)

  2. บนเครื่อง Target (ไม่มีเน็ต):
       mkdir C:\\inetpub\\wwwroot\\ESIG_HUB
       tar -xzvf {args.output} -C C:\\inetpub\\wwwroot\\ESIG_HUB
       cd C:\\inetpub\\wwwroot\\ESIG_HUB
       pip install --no-index --find-links=.\\{args.packages_dir} -r requirements.txt
       copy .env.example .env && notepad .env

  3. ทดสอบก่อนขึ้น IIS:
       py main.py
       # เปิด browser: http://localhost:1244/health

  4. ทดสอบ environment:
       py check_iis.py

  5. ตั้งค่า IIS ตาม DEPLOYMENT_GUIDE.md
"""
    )


if __name__ == "__main__":
    main()
