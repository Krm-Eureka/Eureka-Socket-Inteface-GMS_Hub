import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from tkinter import messagebox
import sys
from flask import Flask, request, jsonify
import threading
import json
import datetime
from werkzeug.serving import make_server
import socket
import time


def log_json(title, data):
    """Helper to print JSON data with indentation"""
    try:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        print(f"{title}:\n{json_str}")
        print("-" * 40)
        sys.stdout.flush()
    except Exception as e:
        print(f"{title}: [Error decoding JSON] {e}")


class GMSReceiverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESIG HUB - Diagnostic Tool")
        self.root.geometry("1100x800")

        # --- Variables ---
        self.server_thread = None
        self.srv = None
        self.sock_client = None
        self.flask_app = Flask(__name__)
        self.is_running = False
        self.msg_count = 0
        self.cnt_rx = 0
        self.cnt_tx = 0
        self.active_clients = 0
        self.lock = threading.Lock()
        self.socket_lock = threading.Lock()
        self.server_mode = ttk.StringVar(value="http")

        # --- UI SETUP ---
        # Main Container with padding
        main_container = ttk.Frame(root, padding=10)
        main_container.pack(fill=BOTH, expand=YES)

        # 1. Top Control Panel (Connection Settings)
        top_frame = ttk.Labelframe(
            main_container, text="Connection Settings", padding=10, bootstyle="info"
        )
        top_frame.pack(fill=X, pady=(0, 10))

        # Mode Selection
        ttk.Label(top_frame, text="Mode:", font=("Helvetica", 10, "bold")).pack(
            side=LEFT, padx=(0, 10)
        )
        self.rb_http = ttk.Radiobutton(
            top_frame,
            text="HTTP",
            variable=self.server_mode,
            value="http",
            bootstyle="info toolbutton",
        )
        self.rb_http.pack(side=LEFT, padx=5)
        self.rb_socket = ttk.Radiobutton(
            top_frame,
            text="Socket",
            variable=self.server_mode,
            value="socket",
            bootstyle="info toolbutton",
        )
        self.rb_socket.pack(side=LEFT, padx=5)

        ttk.Separator(top_frame, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=15)

        # IP / Port Inputs (Container)
        self.input_container = ttk.Frame(top_frame)
        self.input_container.pack(side=LEFT)

        # Socket Inputs
        self.frame_socket_input = ttk.Frame(self.input_container)
        ttk.Label(self.frame_socket_input, text="GMS IP:", font=("Helvetica", 10)).pack(
            side=LEFT, padx=(0, 5)
        )
        self.entry_gms_ip = ttk.Entry(
            self.frame_socket_input, width=15, bootstyle="primary"
        )
        self.entry_gms_ip.insert(0, "10.80.227.230")
        self.entry_gms_ip.pack(side=LEFT)

        # HTTP Inputs
        self.frame_http_input = ttk.Frame(self.input_container)
        ttk.Label(
            self.frame_http_input, text="Local Port:", font=("Helvetica", 10)
        ).pack(side=LEFT, padx=(0, 5))
        self.entry_port = ttk.Entry(self.frame_http_input, width=8, bootstyle="primary")
        self.entry_port.insert(0, "5000")
        self.entry_port.pack(side=LEFT)

        # Start/Stop Button
        self.btn_start = ttk.Button(
            top_frame,
            text="Start Server",
            command=self.toggle_server,
            bootstyle="success",
            width=12,
        )
        self.btn_start.pack(side=RIGHT, padx=10)

        # Status Label
        self.lbl_status = ttk.Label(
            top_frame,
            text="Status: Stopped",
            bootstyle="danger",
            font=("Helvetica", 10, "bold"),
        )
        self.lbl_status.pack(side=RIGHT, padx=10)

        # 2. Command Panel (Client Code, Channel, Auto Query)
        cmd_frame = ttk.Labelframe(
            main_container, text="Command Center", padding=10, bootstyle="primary"
        )
        cmd_frame.pack(fill=X, pady=(0, 10))

        # Client Config Row
        row1 = ttk.Frame(cmd_frame)
        row1.pack(fill=X, pady=(0, 5))

        ttk.Label(row1, text="Client Code:").pack(side=LEFT)
        self.entry_client_code = ttk.Entry(row1, width=10)
        self.entry_client_code.insert(0, "MEKTEC")
        self.entry_client_code.pack(side=LEFT, padx=5)

        ttk.Label(row1, text="Channel ID:").pack(side=LEFT, padx=(10, 0))
        self.entry_channel_id = ttk.Entry(row1, width=10)
        self.entry_channel_id.insert(0, "11111")
        self.entry_channel_id.pack(side=LEFT, padx=5)

        # Auto Query Section
        ttk.Separator(row1, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=15)

        self.auto_query_var = ttk.BooleanVar()
        self.chk_auto = ttk.Checkbutton(
            row1,
            text="Auto Query (ms):",
            variable=self.auto_query_var,
            bootstyle="round-toggle",
        )
        self.chk_auto.pack(side=LEFT)

        self.entry_auto_interval = ttk.Entry(row1, width=8)
        self.entry_auto_interval.insert(0, "1000")
        self.entry_auto_interval.pack(side=LEFT, padx=5)

        self.lbl_countdown = ttk.Label(
            row1, text="", bootstyle="inverse-info", font=("Consolas", 10)
        )
        self.lbl_countdown.pack(side=LEFT, padx=10)

        # Manual Query Row
        row2 = ttk.Frame(cmd_frame)
        row2.pack(fill=X, pady=(5, 0))

        ttk.Label(row2, text="Msg Types:").pack(side=LEFT)
        self.entry_msg_type = ttk.Entry(row2, width=30)
        self.entry_msg_type.insert(
            0,
            "LocationListMsg,StationListMsg,ContainerListMsg,AreaListMsg,WorkflowListMsg,WorkflowInstanceListMsg",
        )
        self.entry_msg_type.pack(side=LEFT, padx=5, fill=X, expand=YES)

        ttk.Label(row2, text="Body JSON:").pack(side=LEFT, padx=(10, 0))
        self.entry_body_json = ttk.Entry(row2, width=20)
        self.entry_body_json.pack(side=LEFT, padx=5, fill=X, expand=YES)

        self.btn_query = ttk.Button(
            row2,
            text="Send Request",
            command=self.send_custom_request,
            bootstyle="primary-outline",
            width=15,
        )
        self.btn_query.pack(side=LEFT, padx=10)
        self.entry_robot_id = ttk.Entry(row2, width=1)  # hidden dummy

        # 3. Logs Area
        logs_frame = ttk.Frame(main_container)
        logs_frame.pack(fill=BOTH, expand=YES)

        # Received Log
        recv_frame = ttk.Labelframe(
            logs_frame, text="Received from GMS", padding=5, bootstyle="success"
        )
        recv_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 5))
        self.txt_received = ScrolledText(
            recv_frame, height=10, font=("Consolas", 9), bootstyle="success"
        )
        self.txt_received.pack(fill=BOTH, expand=YES)

        # Sent Log
        sent_frame = ttk.Labelframe(
            logs_frame, text="Sent to GMS", padding=5, bootstyle="warning"
        )
        sent_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(5, 0))
        self.txt_sent = ScrolledText(
            sent_frame, height=10, font=("Consolas", 9), bootstyle="warning"
        )
        self.txt_sent.pack(fill=BOTH, expand=YES)

        # Stats Bar (Bottom)
        stats_frame = ttk.Frame(main_container, padding=(0, 5, 0, 0))
        stats_frame.pack(fill=X)

        self.lbl_rx = ttk.Label(
            stats_frame,
            text="Requests (Rx): 0",
            font=("Helvetica", 9),
            bootstyle="success",
        )
        self.lbl_rx.pack(side=RIGHT, padx=10)

        self.lbl_tx = ttk.Label(
            stats_frame,
            text="Responses (Tx): 0",
            font=("Helvetica", 9),
            bootstyle="warning",
        )
        self.lbl_tx.pack(side=RIGHT, padx=10)

        # Trigger logic
        self.server_mode.trace_add("write", self.update_ui_by_mode)
        self.update_ui_by_mode()
        self.setup_routes()

    def update_stats(self, rx_inc=0, tx_inc=0):
        self.cnt_rx += rx_inc
        self.cnt_tx += tx_inc
        self.lbl_rx.config(text=f"Requests (Rx): {self.cnt_rx}")
        self.lbl_tx.config(text=f"Responses (Tx): {self.cnt_tx}")

    def update_ui_by_mode(self, *args):
        mode = self.server_mode.get()
        if mode == "socket":
            self.frame_http_input.pack_forget()
            self.frame_socket_input.pack(side=LEFT)
        else:
            self.frame_socket_input.pack_forget()
            self.frame_http_input.pack(side=LEFT)

    def setup_routes(self):
        @self.flask_app.route("/api/gms/callback", methods=["POST"])
        def geek_callback():
            try:
                req_data = request.get_json()
                if not req_data:
                    return jsonify({"code": 1, "message": "No JSON payload"}), 400

                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                client_ip = request.remote_addr
                log_json(f"[{timestamp}] [HTTP] RECV from {client_ip}", req_data)
                res_data = self.process_request_data(req_data)
                self.root.after(
                    0, self.update_logs, timestamp, req_data, res_data, "HTTP"
                )
                return jsonify(res_data), 200
            except Exception as e:
                print(f"Error handling callback: {e}")
                return (
                    jsonify({"code": 1, "message": f"Internal server error: {e}"}),
                    500,
                )

    def process_request_data(self, req_data):
        header = req_data.get("header", {})
        res_data = {
            "header": {
                "responseId": header.get("requestId", ""),
                "clientCode": header.get("clientCode", "geekplus"),
                "requestTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "msgType": header.get("msgType", ""),
                "code": "0",
                "msg": "success",
            },
            "body": {},
        }
        return res_data

    def send_custom_request(self):
        if not self.is_running or not self.sock_client:
            return

        # 1. Gather Inputs (Main Thread)
        client_code = self.entry_client_code.get().strip()
        channel_id = self.entry_channel_id.get().strip()
        msg_type_input = self.entry_msg_type.get().strip()
        body_str = self.entry_body_json.get().strip()
        is_auto = self.auto_query_var.get()

        msg_types = [m.strip() for m in msg_type_input.split(",") if m.strip()]
        if not msg_types:
            if not is_auto:
                messagebox.showwarning("Warning", "Please enter at least one Msg Type.")
            return

        # 2. Launch Background Thread for Sending
        threading.Thread(
            target=self._send_thread,
            args=(msg_types, client_code, channel_id, body_str, is_auto),
            daemon=True,
        ).start()

    def _send_thread(self, msg_types, client_code, channel_id, body_str, is_auto):
        """Thread worker for sending requests to avoid blocking UI"""
        for msg_type in msg_types:
            try:
                if not self.sock_client:
                    break

                req_id = f"req_{int(time.time())}_{msg_type}"
                body_data = {}
                if body_str:
                    try:
                        body_data = json.loads(body_str)
                    except json.JSONDecodeError:
                        if not is_auto:
                            self.root.after(
                                0,
                                lambda: messagebox.showerror(
                                    "Error", "Invalid JSON in Body field."
                                ),
                            )
                        return

                if "msgType" not in body_data:
                    body_data["msgType"] = msg_type

                req_data = {
                    "header": {
                        "requestId": req_id,
                        "channelId": channel_id,
                        "clientCode": client_code,
                        "requestTime": datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    },
                    "body": body_data,
                }

                data = json.dumps(req_data) + "\r\n"

                # Blocking Send
                with self.socket_lock:
                    if self.sock_client:
                        self.sock_client.sendall(data.encode("utf-8"))
                    else:
                        break

                # Update UI safely
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                self.root.after(0, self._log_sent, timestamp, msg_type, req_data)

            except Exception as e:
                # Suppress harmless errors
                if "WinError 10057" in str(e) or "WinError 10038" in str(e):
                    pass
                else:
                    print(f"Error sending {msg_type}: {e}")

    def _log_sent(self, timestamp, msg_type, req_data):
        self.txt_sent.insert(
            END,
            f"[{timestamp}] [SOCK] SENT: {msg_type}\n{json.dumps(req_data, indent=2)}\n{'-'*20}\n",
        )
        self.txt_sent.see(END)

    def start_heartbeat_loop(self):
        while self.is_running and self.sock_client:
            try:
                client_code = self.entry_client_code.get().strip()
                channel_id = self.entry_channel_id.get().strip()
                hb_req = {
                    "header": {
                        "requestId": f"hb_{int(time.time())}",
                        "clientCode": client_code,
                        "channelId": channel_id,
                        "requestTime": datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "msgType": "HeartbeatMsg",
                    },
                    "body": {"msgType": "HeartbeatMsg"},
                }
                data = json.dumps(hb_req) + "\r\n"
                with self.socket_lock:
                    if self.sock_client:
                        self.sock_client.sendall(data.encode("utf-8"))

                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                # Update UI safely
                self.root.after(0, lambda: self.update_stats(tx_inc=1))
                self.root.after(
                    0,
                    lambda t=timestamp: self.txt_sent.insert(
                        END, f"[{t}] [SOCK] SENT: HeartbeatRequest\n"
                    ),
                )
                time.sleep(10)
            except Exception as e:
                print(f"Heartbeat Loop Error: {e}")
                break

    def start_auto_query_loop(self):
        while self.is_running and self.server_mode.get() == "socket":
            if self.auto_query_var.get() and self.sock_client:
                try:
                    self.root.after(0, self.send_custom_request)
                    try:
                        interval_ms = int(self.entry_auto_interval.get())
                        if interval_ms < 100:
                            interval_ms = 100
                    except:
                        interval_ms = 3000

                    remaining_ms = interval_ms
                    step_ms = 100
                    while (
                        remaining_ms > 0
                        and self.is_running
                        and self.auto_query_var.get()
                    ):
                        self.root.after(
                            0,
                            lambda r=remaining_ms / 1000: self.lbl_countdown.config(
                                text=f"{r:.1f}s"
                            ),
                        )
                        time.sleep(step_ms / 1000.0)
                        remaining_ms -= step_ms

                except Exception as e:
                    print(f"Auto Query Error: {e}")
                    self.root.after(0, lambda: self.lbl_countdown.config(text="Error"))
                    time.sleep(1)
            else:
                self.root.after(0, lambda: self.lbl_countdown.config(text=""))
                time.sleep(0.5)

    def run_socket_client(self, gms_ip):
        while self.is_running:
            try:
                self.root.after(
                    0,
                    lambda: self.lbl_status.config(
                        text=f"Socket: Connecting to {gms_ip}...", bootstyle="warning"
                    ),
                )
                self.sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(f"Connecting to GMS at {gms_ip}:24245...")
                self.sock_client.connect((gms_ip, 24245))
                self.sock_client.settimeout(None)

                print(f"Connected to GMS!")
                self.root.after(
                    0,
                    lambda: self.lbl_status.config(
                        text=f"Socket: Connected to {gms_ip}", bootstyle="success"
                    ),
                )

                threading.Thread(target=self.start_heartbeat_loop, daemon=True).start()
                threading.Thread(target=self.start_auto_query_loop, daemon=True).start()

                buffer = b""
                while self.is_running:
                    try:
                        data = self.sock_client.recv(4096)
                        if not data:
                            print("Socket Closed by Server")
                            break
                        buffer += data
                        while b"\r\n" in buffer:
                            msg_bytes, buffer = buffer.split(b"\r\n", 1)
                            req_str = msg_bytes.decode("utf-8")
                            if not req_str.strip():
                                continue

                            req_data = json.loads(req_str)
                            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                            log_json(f"[{timestamp}] [SOCK] RECV", req_data)
                            res_data = self.process_request_data(req_data)
                            self.root.after(
                                0,
                                self.update_logs,
                                timestamp,
                                req_data,
                                res_data,
                                "SOCK",
                            )
                            log_json(f"[{timestamp}] [SOCK] SEND", res_data)

                            res_str = json.dumps(res_data) + "\r\n"
                            with self.socket_lock:
                                self.sock_client.sendall(res_str.encode("utf-8"))
                    except OSError:
                        break
            except Exception as e:
                print(f"Connection Failed: {e}")
                self.root.after(
                    0,
                    lambda msg=str(e): self.lbl_status.config(
                        text=f"Socket: Validating ({msg}). Retry in 5s...",
                        bootstyle="danger",
                    ),
                )

            if self.sock_client:
                try:
                    self.sock_client.close()
                except:
                    pass
                self.sock_client = None

            if self.is_running:
                print("Reconnecting in 5 seconds...")
                time.sleep(5)
        self.root.after(0, self.stop_server)

    def toggle_server(self):
        if not self.is_running:
            mode = self.server_mode.get()
            self.is_running = True

            # Disable inputs
            self.rb_http.configure(state="disabled")
            self.rb_socket.configure(state="disabled")
            self.entry_port.configure(state="disabled")
            self.entry_gms_ip.configure(state="disabled")

            if mode == "http":
                port = int(self.entry_port.get())
                self.server_thread = threading.Thread(
                    target=self.run_flask, args=(port,), daemon=True
                )
                self.lbl_status.config(
                    text=f"HTTP Server: Listening on {port}", bootstyle="success"
                )
            else:
                gms_ip = self.entry_gms_ip.get()
                self.server_thread = threading.Thread(
                    target=self.run_socket_client, args=(gms_ip,), daemon=True
                )
                self.lbl_status.config(
                    text=f"Socket: Connecting to {gms_ip}...", bootstyle="warning"
                )

            self.server_thread.start()
            self.btn_start.config(text="Stop Server", bootstyle="danger")
        else:
            self.stop_server()

    def stop_server(self):
        print("Stopping server/client...")
        self.is_running = False
        if self.srv:
            self.srv.shutdown()
            self.srv = None
        if self.sock_client:
            try:
                self.sock_client.close()
            except:
                pass
            self.sock_client = None

        self.rb_http.configure(state="normal")
        self.rb_socket.configure(state="normal")
        self.entry_port.configure(state="normal")
        self.entry_gms_ip.configure(state="normal")
        self.btn_start.config(text="Start Server", bootstyle="success")
        self.lbl_status.config(text="Status: Stopped", bootstyle="danger")
        print("Stopped.")
        sys.stdout.flush()

    def run_flask(self, port):
        try:
            print(f"HTTP Server starting on port {port}...")
            sys.stdout.flush()
            self.srv = make_server("0.0.0.0", port, self.flask_app)
            self.srv.serve_forever()
        except:
            self.root.after(0, self.stop_server)

    def update_logs(self, timestamp, req_data, res_data, mode):
        self.update_stats(rx_inc=1, tx_inc=1)  # Recv Request + Sent Response
        msg_type = req_data.get("header", {}).get("msgType", "Unknown")
        self.txt_received.insert(
            END,
            f"[{timestamp}] [{mode}] RECV: {msg_type}\n{json.dumps(req_data, indent=2, ensure_ascii=False)}\n{'-'*20}\n",
        )
        self.txt_received.see(END)
        self.txt_sent.insert(
            END,
            f"[{timestamp}] [{mode}] SENT: Success Response\n{json.dumps(res_data, indent=2, ensure_ascii=False)}\n{'-'*20}\n",
        )
        self.txt_sent.see(END)


if __name__ == "__main__":
    # Theme: cyborg, superhero, dark-ly, flatly
    root = ttk.Window(themename="superhero")
    app = GMSReceiverApp(root)
    root.mainloop()
