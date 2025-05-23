from fastapi.testclient import TestClient
from cirisnode.main import app
import jwt

client = TestClient(app)

# Helper for generating a static JWT for test purposes
TEST_SECRET = "testsecret"
def get_auth_header():
    token = jwt.encode({"sub": "testuser"}, TEST_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

def test_push_agent_event():
    headers = get_auth_header()
    response = client.post(
        "/api/v1/agent/events",
        json={"agent_uid": "agent_789", "event": {"type": "Task", "data": "Sample task data"}},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "id" in data
