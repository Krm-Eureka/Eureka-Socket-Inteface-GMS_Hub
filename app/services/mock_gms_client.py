import socket
import time
import random
import threading
import datetime
from typing import Dict, Any, Callable
from loguru import logger
from app.services.gms_client import GMSClient, AppStatus


class MockGMSClient(GMSClient):
    """
    Simulates a GMS Client for testing purposes when the actual server is unreachable.
    Generates fake Rx/Tx traffic and periodical messages.
    """

    def __init__(self, sio):
        super().__init__(sio)
        self.gms_ip = "MOCK_MODE"
        self._connected = False
        self._mock_sock = object()  # Dummy object to represent a socket
        self._stop_event = threading.Event()

    def connect(self):
        """Simulate successful connection"""
        logger.info("MOCK: Attempting to connect...")
        self.emit_log("SYS", "CONNECTING", "Attempting to connect to MOCK SERVER...")
        self._stop_event.wait(1.0)
        self._connected = True
        logger.success("MOCK: Connected to Virtual GMS")
        self._broadcast_status(AppStatus.CONNECTED, "Connected (Mock)")
        self.emit_log("SYS", "CONNECTED", "Connected to MOCK SERVER")
        self._sock = self._mock_sock
        return self._mock_sock

    def disconnect(self):
        """Simulate disconnection"""
        self._connected = False
        self._stop_event.set()
        self._broadcast_status(AppStatus.DISCONNECTED, "Disconnected")
        logger.info("MOCK: Disconnected")

    def is_connected(self):
        return self._connected

    def send_request(
        self, msg_type: str, client_code: str, channel_id: str, body: Dict
    ):
        """Simulate sending a request (Tx)"""
        if not self._connected:
            return

        req_id = f"req_{int(time.time())}_{msg_type}"
        req_data = {
            "header": {
                "requestId": req_id,
                "msgType": msg_type,
                "channelId": channel_id,
                "clientCode": client_code,
                "requestTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            "body": body,
        }

        # Simulate Tx increment
        with self._lock:
            self.stats["tx"] += 1

        # Emit log to frontend for TX visibility
        self.emit_log("TX", msg_type, req_data)

        # Log to server console
        logger.debug(f"📤 [MOCK SEND] {msg_type} -> ID: {req_id}")

    def send_raw(self, data: bytes):
        """Simulate raw send"""
        if not self._connected:
            raise OSError("Mock Socket not connected")
        with self._lock:
            self.stats["tx"] += 1

    def read_loop(self, is_running: Callable[[], bool]):
        """Simulate receiving data (Rx)"""
        logger.info("MOCK: Read Loop Started")

        while is_running() and self._connected:
            if self._stop_event.wait(random.uniform(0.5, 2.0)):  # Random delay
                break

            # Simulate receiving a message
            msg_type = random.choice(
                [
                    "RobotInfoMsg",
                    "TaskStatusMsg",
                    "SystemStatusMsg",
                    "WorkflowInstanceListMsg",
                ]
            )

            # Create a fake realistic payload with Header/Body
            res_id = f"res_{random.randint(1000,9999)}_{msg_type}"

            if msg_type == "WorkflowInstanceListMsg":
                # ... (existing tasks)
                mock_tasks = []
                for i in range(1, 101):
                    mock_tasks.append(
                        {
                            "instanceId": f"INST-{1000+i}",
                            "taskId": i,
                            "workflowName": f"Mok-Work-{i%5}",
                            "workflowCode": f"WFC-00{i%5}",
                            "instanceStatus": random.choice(["10", "20", "30", "40"]),
                            "startTime": datetime.datetime.now().strftime("%H:%M:%S"),
                            "robot": f"RBT-{random.randint(1,5)}",
                        }
                    )
                mock_body = mock_tasks
            elif msg_type == "RobotInfoMsg":
                # Generate realistic robot data
                mock_robots = []
                for i in range(1, 4):
                    mock_robots.append(
                        {
                            "robot": f"RBT-0{i}",
                            "robotProduct": "M200C-SNE",
                            "status": random.choice(["10", "20", "30"]),
                            "powerPercent": random.randint(20, 95),
                            "location": {
                                "x": 20.0 + random.uniform(-5, 5),
                                "y": 20.0 + random.uniform(-5, 5),
                                "z": 1,
                            },
                            "angle": random.uniform(0, 360),
                        }
                    )
                mock_body = mock_robots
            else:
                mock_body = {
                    "status": "SUCCESS",
                    "data": {
                        "id": random.randint(1, 100),
                        "state": random.choice(["IDLE", "RUNNING", "ERROR"]),
                        "details": f"Mock data for {msg_type}",
                    },
                }

            mock_data = {
                "header": {
                    "responseId": res_id,
                    "msgType": msg_type,
                    "responseTime": datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                },
                "body": mock_body,
            }

            # Rx increment
            with self._lock:
                self.stats["rx"] += 1

            # Log to server console
            logger.debug(f"📥 [MOCK RECV] {msg_type} <- ID: {res_id}")

            # Emit log to frontend
            self.emit_log("RX", msg_type, mock_data)

            # Trigger specific data event for FE
            self.emit_socket(f"gms:data:{msg_type}", mock_data)

            if self._on_message_callback:
                self._on_message_callback(mock_data)

            # 5% chance to simulate a brief error or reconnect (optional, keeps it interesting)
            # if random.random() < 0.05:
            #     self.emit_log("SYS", "WARNING", "Mock jitter detected...")

        logger.info("MOCK: Read Loop Ended")
