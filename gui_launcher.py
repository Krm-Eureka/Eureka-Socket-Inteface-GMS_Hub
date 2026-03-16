import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import subprocess
import sys
import os
import time
import signal
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item

# ─── CLI Flags ────────────────────────────────────────────────────────────────
AUTO_START_MODE = "--autostart" in sys.argv  # รันโดยไม่ต้องกด Start Server เอง

# Handle path for PyInstaller bundled executable
if getattr(sys, "frozen", False):
    EXE_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = sys._MEIPASS
    # For frozen app, the code (main.py, app/) is inside RESOURCE_DIR
    if RESOURCE_DIR not in sys.path:
        sys.path.insert(0, RESOURCE_DIR)
else:
    EXE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = EXE_DIR

# Import our diagnostic logic
try:
    import check_iis as diagnostic
except ImportError:
    diagnostic = None


# --- NEW: Routing for PyInstaller Executable ---
def check_routing():
    """Detect if we should run the Server (main.py) or the GUI"""
    if len(sys.argv) > 1 and sys.argv[1] == "main.py":
        # Launch the actual server logic
        try:
            import uvicorn
            from app.core.config import settings

            # We import main to ensure all routes/logic are loaded
            import main

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
    def __init__(self, root):
        self.root = root
        self.root.title("ESIG HUB - Standalone Launcher")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")

        self.process = None
        self.is_running = False
        self.tray_icon = None
        self.auto_start = AUTO_START_MODE  # จาก --autostart flag

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
                lbl = self.diag_labels[key]
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
                results, _ = diagnostic.run_all_checks(
                    env_file=env_path, skip_import=skip_main
                )
                self.root.after(0, lambda r=results: self.update_diag_ui(r))

                # ─── Auto-Start: ถ้า --autostart และ ทุก check ผ่าน ────────────
                if self.auto_start:
                    all_passed = all(results.values())
                    if all_passed:
                        self.root.after(500, self._auto_start_and_minimize)
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
        self.root.after(3000, self.minimize_to_tray)

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
                    subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
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
        if not self.process:
            return

        self.log_area.insert(tk.END, "\n>>> Stopping server...\n")

        try:
            if os.name == "nt":
                # Sending CTRL_BREAK_EVENT to the process group
                os.kill(self.process.pid, signal.CTRL_BREAK_EVENT)
            else:
                self.process.terminate()

            self.process.wait(timeout=5)
        except Exception:
            self.process.kill()

        self.process = None
        self.is_running = False
        self.btn_start.config(text=" START SERVER ", bg="#27ae60")
        self.log_area.insert(tk.END, ">>> Server Stopped.\n")

    def content_reader(self):
        """Thread to read subprocess stdout and write to UI"""
        while self.process and self.process.poll() is None:
            line = self.process.stdout.readline()
            if line:
                self.root.after(0, lambda l=line: self.append_log(l))
            else:
                time.sleep(0.1)

        # Final cleanup
        if self.is_running:
            self.root.after(0, self.stop_server)

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
            self.tray_icon = pystray.Icon("ESIG HUB", img, "ESIG HUB Launcher", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        if self.tray_icon:

            self.root.after(0, self.root.deiconify)
            self.root.after(0, self.root.lift)

    def quit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        if self.is_running:
            self.stop_server()
        self.root.after(0, self.root.destroy)


if __name__ == "__main__":
    if os.name != "nt":
        print("This launcher is designed for Windows environment.")

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
