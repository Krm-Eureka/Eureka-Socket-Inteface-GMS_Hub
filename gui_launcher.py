import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import subprocess
from subprocess import Popen
import sys
import os
import time
import signal
from typing import Any, Dict, Optional
from PIL import Image, ImageTk  # type: ignore[import]
import pystray  # type: ignore[import]
from pystray import MenuItem as item  # type: ignore[import]
import psutil  # type: ignore[import]


# ─── Single Instance Protection ──────────────────────────────────────────────
def check_single_instance():
    """Returns True if another instance of this application is already running."""
    current_pid = os.getpid()
    current_exe = os.path.basename(sys.executable).lower()
    is_frozen = getattr(sys, "frozen", False)

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if proc.info["pid"] == current_pid:
                continue

            if is_frozen and proc.info["name"].lower() == "esig_hub_launcher.exe":
                return True

            if not is_frozen and "gui_launcher.py" in str(proc.info["cmdline"]):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


# ─── CLI Flags ────────────────────────────────────────────────────────────────
AUTO_START_MODE = "--autostart" in sys.argv  # รันโดยไม่ต้องกด Start Server เอง

# Handle path for PyInstaller bundled executable
if getattr(sys, "frozen", False):
    EXE_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = sys._MEIPASS  # type: ignore[attr-defined]
    # For frozen app, the code (main.py, app/) is inside RESOURCE_DIR
    if RESOURCE_DIR not in sys.path:
        sys.path.insert(0, RESOURCE_DIR)
else:
    EXE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = EXE_DIR

# Import our diagnostic logic
try:
    import check_iis as diagnostic  # type: ignore[import]
except ImportError:
    diagnostic = None


# --- NEW: Routing for PyInstaller Executable ---
def check_routing():
    """Detect if we should run the Server (main.py) or the GUI"""
    if len(sys.argv) > 1 and sys.argv[1] == "main.py":
        # Launch the actual server logic
        try:
            import uvicorn  # type: ignore[import]
            from app.core.config import settings  # type: ignore[import]

            # We import main to ensure all routes/logic are loaded
            import main  # type: ignore[import]

            print(f"Launching Server on {settings.BFF_HOST}:{settings.BFF_PORT}")
            uvicorn.run(
                "main:socket_app",
                host=settings.BFF_HOST,
                port=settings.BFF_PORT,
                reload=False,
            )
            return True
        except Exception as e:
            print(f"Failed to load server: {e}")
            sys.exit(1)
    return False


if check_routing():
    sys.exit(0)
# -----------------------------------------------


class EsigHubLauncher:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ESIG HUB - Standalone Launcher")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")

        self.process: Optional[Popen[str]] = None
        self.is_running: bool = False
        self.tray_icon: Optional[pystray.Icon] = None
        self.auto_start: bool = AUTO_START_MODE

        # UI attributes — initialized below by setup_ui() before any other method runs
        self.icon_image: Any = None
        self.status_frame: Any = None
        self.diag_labels: Dict[str, Any] = {}
        self.btn_run_diag: Any = None
        self.btn_start: Any = None
        self.log_area: Any = None

        # UI Components
        self.setup_ui()

        # Set Window Icon
        self.set_app_icon()

        # Initial Diagnostic
        self.run_diagnostics()

    def set_app_icon(self):
        try:
            icon_path = os.path.join(RESOURCE_DIR, "static", "images", "esig_hub.png")
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
                self.icon_image = img  # Keep reference
        except Exception as e:
            print(f"Failed to set icon: {e}")

    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="ESIG HUB v1.1.2",
            font=("Segoe UI", 16, "bold"),
            bg="#2c3e50",
            fg="white",
        ).pack(pady=15)

        # Status Panel
        self.status_frame = tk.LabelFrame(
            self.root,
            text=" System Diagnostics ",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=10,
        )
        self.status_frame.pack(fill=tk.X, padx=20, pady=10)

        self.diag_labels = {}
        lab_names = {
            "python": "Python Version",
            "packages": "Required Packages",
            "env": "Environment File (.env)",
            "network": "Network / DB Connectivity",
            "port": "Port Availability",
            "logs": "Logs Permission",
            "dirs": "Project Directories",
            "import": "main.py Syntax Check",
        }

        for key, text in lab_names.items():
            f = tk.Frame(self.status_frame)
            f.pack(fill=tk.X, pady=2)
            tk.Label(f, text=text, font=("Segoe UI", 10), width=30, anchor="w").pack(
                side=tk.LEFT
            )
            lbl = tk.Label(
                f, text="Pending...", font=("Segoe UI", 10, "italic"), fg="gray"
            )
            lbl.pack(side=tk.RIGHT)
            self.diag_labels[key] = lbl

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.btn_run_diag = tk.Button(
            btn_frame,
            text="Re-Scan Status",
            command=self.run_diagnostics,
            padx=10,
            pady=5,
            bg="#ecf0f1",
        )
        self.btn_run_diag.pack(side=tk.LEFT, padx=5)

        self.btn_start = tk.Button(
            btn_frame,
            text=" START SERVER ",
            command=self.toggle_server,
            padx=20,
            pady=5,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)

        # Log Output
        log_label = tk.Label(
            self.root,
            text="Server Logs Output:",
            font=("Consolas", 10, "bold"),
            anchor="w",
        )
        log_label.pack(fill=tk.X, padx=20)

        self.log_area = scrolledtext.ScrolledText(
            self.root, height=15, font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4"
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def update_diag_ui(self, results):
        for key, passed in results.items():
            if key in self.diag_labels:
                lbl = self.diag_labels[key]  # type: ignore[index]
                if passed:
                    lbl.config(
                        text="PASSED", fg="#27ae60", font=("Segoe UI", 10, "bold")
                    )
                else:
                    lbl.config(
                        text="FAILED", fg="#e74c3c", font=("Segoe UI", 10, "bold")
                    )

    def run_diagnostics(self):
        if not diagnostic:
            messagebox.showerror(
                "Error", "check_iis.py not found! Cannot run diagnostics."
            )
            return

        def task():
            try:
                env_path = os.path.join(EXE_DIR, ".env")
                skip_main = getattr(sys, "frozen", False)
                results, _ = diagnostic.run_all_checks(  # type: ignore[union-attr]
                    env_file=env_path, skip_import=skip_main
                )
                self.root.after(0, lambda r=results: self.update_diag_ui(r))

                # ─── Auto-Start: ถ้า --autostart และ ทุก check ผ่าน ────────────
                if self.auto_start:
                    all_passed = all(results.values())
                    if all_passed:
                        self.root.after(500, self._auto_start_and_minimize)  # type: ignore[arg-type]
                    else:
                        # มี check ล้มเหลว → แสดง window ให้ admin เห็น
                        failed = [k for k, v in results.items() if not v]
                        self.root.after(
                            0,
                            lambda f=failed: self.append_log(
                                f"[AUTO-START] Aborted — checks failed: {f}\n"
                            ),
                        )
            except Exception as e:
                err_msg = str(e)
                self.root.after(
                    0, lambda m=err_msg: messagebox.showerror("Diag Error", m)
                )

        threading.Thread(target=task, daemon=True).start()

    def _auto_start_and_minimize(self):
        """เรียกโดยอัตโนมัติเมื่อ --autostart และ diagnostics ผ่านทั้งหมด"""
        self.append_log("[AUTO-START] All diagnostics passed — starting server...\n")
        self.start_server()
        # หลัง 3 วินาที minimize ลง system tray
        self.root.after(3000, self.minimize_to_tray)  # type: ignore[arg-type]

    def toggle_server(self):
        if self.is_running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        if self.process:
            return

        self.log_area.delete(1.0, tk.END)
        self.log_area.insert(tk.END, ">>> Launching ESIG HUB STANDALONE...\n")

        # We use 'py' to launch main.py
        cmd = [sys.executable, "main.py"]

        try:
            # Set environment variable to ensure unbuffered output
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            # Provide base path so main.py resolves logs/ relative to EXE_DIR
            env["ESIG_BASE_DIR"] = EXE_DIR

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=EXE_DIR,  # <-- logs/ and .env are written beside the .exe
                creationflags=(
                    subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0  # type: ignore[attr-defined]
                ),
                env=env,
            )

            self.is_running = True
            self.btn_start.config(text=" STOP SERVER ", bg="#e74c3c")

            # Start Log Reader Thread
            threading.Thread(target=self.content_reader, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Process Error", f"Failed to launch: {e}")

    def stop_server(self):
        proc = self.process
        if not proc:
            return

        self.log_area.insert(tk.END, "\n>>> Stopping server...\n")

        try:
            if os.name == "nt":
                # Sending CTRL_BREAK_EVENT to the process group
                os.kill(proc.pid, signal.CTRL_BREAK_EVENT)  # type: ignore[attr-defined]
            else:
                proc.terminate()

            proc.wait(timeout=5)
        except Exception:
            proc.kill()

        self.process = None
        self.is_running = False
        self.btn_start.config(text=" START SERVER ", bg="#27ae60")
        self.log_area.insert(tk.END, ">>> Server Stopped.\n")

    def content_reader(self):
        """Thread to read subprocess stdout and write to UI"""
        while self.process and self.process.poll() is None:  # type: ignore[union-attr]
            line = self.process.stdout.readline()  # type: ignore[union-attr]
            if line:
                self.root.after(0, lambda l=line: self.append_log(l))
            else:
                time.sleep(0.1)

        # Final cleanup
        if self.is_running:
            self.root.after(0, self.stop_server)  # type: ignore[arg-type]

    def append_log(self, msg):
        self.log_area.insert(tk.END, msg)
        self.log_area.see(tk.END)

    def minimize_to_tray(self):
        self.root.withdraw()

        if not self.tray_icon:
            icon_path = os.path.join(RESOURCE_DIR, "static", "images", "esig_hub.png")
            img = Image.open(icon_path)

            menu = (
                item("Show Window", lambda: self.show_window()),
                item("Exit", lambda: self.quit_app()),
            )
            icon = pystray.Icon("ESIG HUB", img, "ESIG HUB Launcher", menu)
            self.tray_icon = icon
            threading.Thread(target=icon.run, daemon=True).start()

    def show_window(self):
        if self.tray_icon:

            self.root.after(0, self.root.deiconify)  # type: ignore[arg-type]
            self.root.after(0, self.root.lift)

    def quit_app(self):
        icon = self.tray_icon
        if icon:
            icon.stop()
        if self.is_running:
            self.stop_server()
        self.root.after(0, self.root.destroy)  # type: ignore[arg-type]


if __name__ == "__main__":
    if os.name != "nt":
        print("This launcher is designed for Windows environment.")

    # 🛑 Check for single instance
    if check_single_instance():
        # Using a temporary TK root to show message box before main loop starts
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showwarning(
            "ESIG HUB Already Running",
            "Another instance of ESIG HUB Launcher is already running.\n\n"
            "Please check your system tray (hidden icons) or Task Manager.",
        )
        temp_root.destroy()
        sys.exit(0)

    root = tk.Tk()
    app = EsigHubLauncher(root)

    # Handle window close
    def on_closing():
        if app.is_running:
            # If server is running, we offer to minimize to tray or quit
            msg = "Server is still running.\n\n'Yes' - Exit everything\n'No' - Minimize to System Tray\n'Cancel' - Back to App"
            choice = messagebox.askyesnocancel("Exit ESIG HUB", msg)
            if choice is True:
                app.quit_app()
            elif choice is False:
                app.minimize_to_tray()
        else:
            if messagebox.askokcancel("Quit", "Are you sure you want to exit?"):
                app.quit_app()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
