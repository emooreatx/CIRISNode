import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app

@pytest.fixture
def client():
    """Create a TestClient instance with default X-DID header."""
    return TestClient(app, headers={"X-DID": "did:peer:123"})

def test_action_listen_positive(client):
    """Test TAKE ACTION with 'listen' action type."""
    response = client.post("/api/v1/wa/action", json={"action_type": "listen"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "decision_id" in data
    assert data["action"] == "listen"
    assert data["handler"] == "TAKE_ACTION"
    assert data["did"] == "did:peer:123"
    assert "timestamp" in data

def test_action_use_tool_positive(client):
    """Test TAKE ACTION with 'useTool' action type."""
    response = client.post("/api/v1/wa/action", json={"action_type": "useTool"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "decision_id" in data
    assert data["action"] == "useTool"
    assert data["handler"] == "TAKE_ACTION"
    assert data["did"] == "did:peer:123"
    assert "timestamp" in data

def test_action_speak_positive(client):
    """Test TAKE ACTION with 'speak' action type."""
    response = client.post("/api/v1/wa/action", json={"action_type": "speak"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "decision_id" in data
    assert data["action"] == "speak"
    assert data["handler"] == "TAKE_ACTION"
    assert data["did"] == "did:peer:123"
    assert "timestamp" in data

def test_action_no_did_header(client):
    """Test TAKE ACTION without X-DID header, should use mock DID."""
    client_no_did = TestClient(app)
    response = client_no_did.post("/api/v1/wa/action", json={"action_type": "listen"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "decision_id" in data
    assert data["action"] == "listen"
    assert data["did"].startswith("did:mock:")
    assert "timestamp" in data

def test_action_invalid_action_type(client):
    """Test TAKE ACTION with invalid action type."""
    response = client.post("/api/v1/wa/action", json={"action_type": "invalid"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid action type" in data["detail"]
