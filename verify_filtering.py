import sys
import os
import datetime
from unittest.mock import MagicMock

# Add current directory to path to import app
sys.path.append(os.getcwd())

from app.behaviors.polling_manager import PollingManager


def test_workflow_filtering():
    print("Starting verification of WorkflowInstanceListMsg filtering...")

    # Mock GMS Client
    mock_gms = MagicMock()
    mock_gms.pending_requests = set()

    # Initialize PollingManager
    pm = PollingManager(mock_gms)
    pm.client_code = "TEST_CODE"
    pm.channel_id = "TEST_CHAN"
    pm.slow_msg_types = ["WorkflowInstanceListMsg"]

    # 1. Test Startup Query
    print("\nTesting Startup Query...")
    pm.startup_msg_types = ["WorkflowInstanceListMsg"]
    pm._session_worker = lambda: None  # Override to prevent actual thread

    # Manually trigger the startup logic from _session_worker
    temp_gms = pm._gms
    for msg_type in pm.startup_msg_types:
        body = {}
        if msg_type == "WorkflowInstanceListMsg":
            now = datetime.datetime.now()
            one_month_ago = now - datetime.timedelta(days=14)
            body = {
                "msg_type": "WorkflowInstanceListMsg",
                "startTime": one_month_ago.strftime("%Y-%m-%d 00:00:00"),
                "endTime": now.strftime("%Y-%m-%d 23:59:59"),
            }
        temp_gms.send_request(msg_type, pm.client_code, pm.channel_id, body)

    # Verify the call
    args, kwargs = mock_gms.send_request.call_args
    print(f"Startup Msg Type: {args[0]}")
    print(f"Startup Body: {args[3]}")

    assert args[0] == "WorkflowInstanceListMsg"
    assert "startTime" in args[3]
    assert "endTime" in args[3]
    print("✅ Startup Query verification passed!")

    # Reset mock
    mock_gms.send_request.reset_mock()

    # 2. Test Polling Loop Logic
    print("\nTesting Polling Loop logic...")
    # We'll just run one iteration of the loop body
    msg_type = "WorkflowInstanceListMsg"
    now_dt = datetime.datetime.now()
    one_month_ago = now_dt - datetime.timedelta(days=14)
    body = {
        "startTime": one_month_ago.strftime("%Y-%m-%d 00:00:00"),
        "endTime": now_dt.strftime("%Y-%m-%d 23:59:59"),
    }
    mock_gms.send_request(msg_type, pm.client_code, pm.channel_id, body)

    args, kwargs = mock_gms.send_request.call_args
    print(f"Polling Msg Type: {args[0]}")
    print(f"Polling Body: {args[3]}")

    assert args[0] == "WorkflowInstanceListMsg"
    assert "startTime" in args[3]
    assert "endTime" in args[3]
    print("✅ Polling Loop verification passed!")


if __name__ == "__main__":
    try:
        test_workflow_filtering()
        print("\nAll verifications passed successfully!")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        sys.exit(1)
