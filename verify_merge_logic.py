import sys
import os
import datetime
from unittest.mock import MagicMock

# Add current directory to path
sys.path.append(os.getcwd())

from app.behaviors.polling_manager import PollingManager


def test_task_merging():
    print("Starting verification of task merging and sorting logic...")

    # Mock GMS Client
    mock_gms = MagicMock()
    pm = PollingManager(mock_gms)

    # 1. Initial Data (Batch A)
    batch_a = [
        {"instanceId": "INST-001", "taskId": 1, "startTime": "2026-02-24 10:00:00"},
        {"instanceId": "INST-002", "taskId": 2, "startTime": "2026-02-24 10:05:00"},
    ]

    pm.handle_gms_message(
        {"header": {"msgType": "WorkflowInstanceListMsg"}, "body": batch_a}
    )

    print(f"After Batch A: {len(pm._task_cache)} tasks")
    assert len(pm._task_cache) == 2
    assert pm._task_cache[0]["instanceId"] == "INST-002"  # Latest first

    # 2. Update existing task (Batch B)
    batch_b = [
        {
            "instanceId": "INST-002",
            "taskId": 2,
            "startTime": "2026-02-24 10:05:00",
            "instanceStatus": "40 (Updated)",
        },
        {"instanceId": "INST-003", "taskId": 3, "startTime": "2026-02-24 10:10:00"},
    ]

    pm.handle_gms_message(
        {"header": {"msgType": "WorkflowInstanceListMsg"}, "body": batch_b}
    )

    print(f"After Batch B: {len(pm._task_cache)} tasks")
    assert len(pm._task_cache) == 3
    assert pm._task_cache[0]["instanceId"] == "INST-003"  # Newest
    assert pm._task_cache[1]["instanceStatus"] == "40 (Updated)"  # Merged

    # 3. Test Limit (10,000) - Simulating large merge
    large_batch = []
    for i in range(10, 10010):
        large_batch.append(
            {
                "instanceId": f"INST-{i:05d}",
                "taskId": i,
                "startTime": f"2026-02-24 11:00:{i%60:02d}",
            }
        )

    pm.handle_gms_message(
        {"header": {"msgType": "WorkflowInstanceListMsg"}, "body": large_batch}
    )

    print(f"After Large Batch: {len(pm._task_cache)} tasks (Limit check)")
    assert len(pm._task_cache) == 10000

    # 4. Chronological Sort Verification
    # Add a late task out of order
    late_task = {
        "instanceId": "LATE-999",
        "taskId": 99999,
        "startTime": "2026-02-25 12:00:00",
    }
    pm.handle_gms_message(
        {"header": {"msgType": "WorkflowInstanceListMsg"}, "body": [late_task]}
    )

    assert pm._task_cache[0]["instanceId"] == "LATE-999"
    print("✅ Task merging and chronological sorting verified!")


if __name__ == "__main__":
    try:
        test_task_merging()
        print("\nAll verification steps passed!")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
