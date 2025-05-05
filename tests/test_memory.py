import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app

@pytest.fixture
def client():
    """Create a TestClient instance with default X-DID header."""
    return TestClient(app, headers={"X-DID": "did:peer:789"})

def test_memory_learn_positive(client):
    """Test MEMORY with 'learn' action."""
    response = client.post("/api/v1/wa/memory", json={
        "memory_action": "learn",
        "content": "New information to store"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "decision_id" in data
    assert data["action"] == "learn"
    assert data["handler"] == "MEMORY"
    assert data["content"] == "New information to store"
    assert data["did"] == "did:peer:789"
    assert "timestamp" in data

def test_memory_remember_positive(client):
    """Test MEMORY with 'remember' action."""
    response = client.post("/api/v1/wa/memory", json={
        "memory_action": "remember",
        "content": "Recall prior decision"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "decision_id" in data
    assert data["action"] == "remember"
    assert data["handler"] == "MEMORY"
    assert data["content"] == "Recall prior decision"
    assert data["did"] == "did:peer:789"
    assert "timestamp" in data

def test_memory_forget_positive(client):
    """Test MEMORY with 'forget' action."""
    response = client.post("/api/v1/wa/memory", json={
        "memory_action": "forget",
        "content": "Remove from active state"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "decision_id" in data
    assert data["action"] == "forget"
    assert data["handler"] == "MEMORY"
    assert data["content"] == "Remove from active state"
    assert data["did"] == "did:peer:789"
    assert "timestamp" in data

def test_memory_no_did_header(client):
    """Test MEMORY without X-DID header, should use mock DID."""
    client_no_did = TestClient(app)
    response = client_no_did.post("/api/v1/wa/memory", json={
        "memory_action": "learn",
        "content": "New information"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "decision_id" in data
    assert data["action"] == "learn"
    assert data["did"].startswith("did:mock:")
    assert "timestamp" in data

def test_memory_missing_memory_action(client):
    """Test MEMORY with missing memory action."""
    response = client.post("/api/v1/wa/memory", json={
        "content": "Missing action"
    })
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid memory action" in data["detail"]

def test_memory_invalid_memory_action(client):
    """Test MEMORY with invalid memory action."""
    response = client.post("/api/v1/wa/memory", json={
        "memory_action": "store",
        "content": "Invalid action"
    })
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid memory action" in data["detail"]
