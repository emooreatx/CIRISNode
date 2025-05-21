from fastapi.testclient import TestClient
from cirisnode.main import app
from cirisnode.api.auth.dependencies import create_access_token

client = TestClient(app)

def get_auth_header():
    token = create_access_token(data={"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}

def test_submit_wbd_task():
    headers = get_auth_header()
    response = client.post(
        "/api/v1/wbd/submit",
        json={"agent_task_id": "task_123", "payload": "Test payload"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "task_id" in data

def test_get_wbd_tasks():
    headers = get_auth_header()
    response = client.get("/api/v1/wbd/tasks", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert isinstance(data["tasks"], list)

def test_resolve_wbd_task():
    headers = get_auth_header()
    # First, submit a task to get a task_id
    submit_response = client.post(
        "/api/v1/wbd/submit",
        json={"agent_task_id": "task_456", "payload": "Test payload for resolution"},
        headers=headers
    )
    task_id = submit_response.json()["task_id"]
    
    # Then, resolve the task
    resolve_response = client.post(
        f"/api/v1/wbd/tasks/{task_id}/resolve",
        json={"decision": "approve", "comment": "Approved"},
        headers=headers
    )
    assert resolve_response.status_code == 200
    data = resolve_response.json()
    assert data["status"] == "success"
    assert data["task_id"] == task_id
