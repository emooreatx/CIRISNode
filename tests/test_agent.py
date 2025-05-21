from fastapi.testclient import TestClient
from cirisnode.main import app
from cirisnode.api.auth.dependencies import create_access_token

client = TestClient(app)

def get_auth_header():
    token = create_access_token(data={"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}

def test_push_agent_event():
    headers = get_auth_header()
    response = client.post(
        "/api/v1/agent/events",
        json={"agent_uid": "agent_789", "event_json": {"type": "Task", "data": "Sample task data"}},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "event_id" in data
