import subprocess
import sys
import os
import shutil


def build():
    print("🚀 Starting ESIG HUB Build Process...")

    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Try to Create .ico from project image
    icon_path = None
    try:
        from PIL import Image

        png_path = os.path.join(os.getcwd(), "static", "images", "esig_hub.png")
        if os.path.exists(png_path):
            ico_path = os.path.join(os.getcwd(), "esig_hub.ico")
            img = Image.open(png_path)
            # Create icon with multiple sizes
            img.save(
                ico_path,
                format="ICO",
                sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)],
            )
            icon_path = ico_path
            print("🎨 Icon converted to .ico")
    except Exception as e:
        print(f"⚠️ Could not convert icon to .ico: {e}")

    # Define build command
    # --onefile: Create a single executable
    # --windowed: No console window when running the GUI
    # --name: Executable name
    # --add-data: Include static and templates folders

    separator = ";" if os.name == "nt" else ":"

    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--contents-directory",
        "internal",
        "--name",
        "ESIG_HUB_Launcher",
        "--uac-admin",
    ]

    if icon_path:
        cmd.extend(["--icon", icon_path])

    cmd.extend(
        [
            f"--add-data=static{separator}static",
            f"--add-data=templates{separator}templates",
            f"--add-data=app{separator}app",
            f"--add-data=static/ui_assets{separator}ui_assets",
            "--collect-all",
            "uvicorn",
            "--collect-all",
            "fastapi",
            "--collect-all",
            "pystray",
            "--collect-all",
            "PIL",
            "gui_launcher.py",
        ]
    )

    print(f"📦 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n✅ Build Successful!")
        print(
            f"📂 Your executable is in the 'dist' folder: {os.path.join(os.getcwd(), 'dist', 'ESIG_HUB_Launcher.exe')}"
        )
        print(
            "\nNote: Make sure your '.env' file is in the same folder as the .exe when running."
        )
    else:
        print("\n❌ Build Failed. Check the errors above.")


if __name__ == "__main__":
    build()
