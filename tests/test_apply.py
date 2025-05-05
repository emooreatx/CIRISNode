import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app

@pytest.fixture
def client():
    """Create a TestClient instance with default X-DID header."""
    return TestClient(app, headers={"X-DID": "did:peer:202"})

def test_apply_env_graph_positive(client):
    """Test APPLY with 'ENV_GRAPH' type."""
    response = client.post("/api/v1/graph/apply", json={
        "graph_type": "ENV_GRAPH",
        "intent": "update"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "update_id" in data
    assert data["graph_type"] == "ENV_GRAPH"
    assert data["intent"] == "update"
    assert data["did"] == "did:peer:202"
    assert "timestamp" in data
    assert "update applied to" in data["message"].lower()

def test_apply_id_graph_positive(client):
    """Test APPLY with 'ID_GRAPH' type."""
    response = client.post("/api/v1/graph/apply", json={
        "graph_type": "ID_GRAPH",
        "intent": "link"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "update_id" in data
    assert data["graph_type"] == "ID_GRAPH"
    assert data["intent"] == "link"
    assert data["did"] == "did:peer:202"
    assert "timestamp" in data
    assert "update applied to" in data["message"].lower()

def test_apply_job_graph_positive(client):
    """Test APPLY with 'JOB_GRAPH' type."""
    response = client.post("/api/v1/graph/apply", json={
        "graph_type": "JOB_GRAPH",
        "intent": "assign"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "update_id" in data
    assert data["graph_type"] == "JOB_GRAPH"
    assert data["intent"] == "assign"
    assert data["did"] == "did:peer:202"
    assert "timestamp" in data
    assert "update applied to" in data["message"].lower()

def test_job_assign_positive(client):
    """Test JOB ASSIGN with specific job and target DID."""
    response = client.post("/api/v1/graph/job/assign", json={
        "job_id": "job_123",
        "target_did": "did:peer:target_456",
        "intent": "assign"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "assignment_id" in data
    assert data["job_id"] == "job_123"
    assert data["target_did"] == "did:peer:target_456"
    assert data["intent"] == "assign"
    assert data["did"] == "did:peer:202"
    assert "timestamp" in data
    assert "job" in data["message"].lower() and "assigned to" in data["message"].lower()

def test_apply_no_did_header(client):
    """Test APPLY without X-DID header, should use mock DID."""
    client_no_did = TestClient(app)
    response = client_no_did.post("/api/v1/graph/apply", json={
        "graph_type": "ENV_GRAPH",
        "intent": "update"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "update_id" in data
    assert data["graph_type"] == "ENV_GRAPH"
    assert data["did"].startswith("did:mock:")
    assert "timestamp" in data

def test_job_assign_no_did_header(client):
    """Test JOB ASSIGN without X-DID header, should use mock DID."""
    client_no_did = TestClient(app)
    response = client_no_did.post("/api/v1/graph/job/assign", json={
        "job_id": "job_456",
        "target_did": "did:peer:target_789"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "assignment_id" in data
    assert data["job_id"] == "job_456"
    assert data["did"].startswith("did:mock:")
    assert "timestamp" in data

def test_apply_invalid_graph_type(client):
    """Test APPLY with invalid graph type."""
    response = client.post("/api/v1/graph/apply", json={
        "graph_type": "INVALID_GRAPH",
        "intent": "update"
    })
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid graph type" in data["detail"]
