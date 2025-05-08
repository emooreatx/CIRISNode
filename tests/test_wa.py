import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app
from init_db import initialize_database

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """
    Ensure the database is initialized before each test.
    """
    initialize_database()

def test_reject_task_valid():
    """
    Test rejecting a valid task.
    """
    # Add a task to the active_tasks table
    response = client.post(
        "/wa/defer",
        json={"task_type": "example", "payload": "test payload"}
    )
    assert response.status_code == 200
    task_id = response.json()["task_id"]

    # Reject the task
    response = client.post(
        "/wa/reject",
        json={"task_id": task_id, "reason": "Not needed"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify the task is removed from active_tasks
    response = client.get("/wa/active_tasks")
    assert response.status_code == 200
    assert task_id not in [task["id"] for task in response.json()]

    # Verify the task is added to completed_actions
    response = client.get("/wa/completed_actions")
    assert response.status_code == 200
    completed_task = next(
        (action for action in response.json() if action["task_id"] == task_id), None
    )
    assert completed_task is not None
    assert completed_task["action_type"] == "reject"
    assert completed_task["reason"] == "Not needed"

def test_reject_task_invalid_id():
    """
    Test rejecting a task with an invalid ID.
    """
    response = client.post(
        "/wa/reject",
        json={"task_id": 9999, "reason": "Invalid task"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"
