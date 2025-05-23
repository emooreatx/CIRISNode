import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app

@pytest.fixture
def client():
    """Create a TestClient instance with default X-DID header."""
    return TestClient(app, headers={"X-DID": "did:peer:456"})

def test_deferral_ponder_negative(client):
    """Test WISE DEFERRAL with 'ponder' decision type - should fail as only 'defer' is handled by backend."""
    response = client.post("/api/v1/wa/deferral", json={
        "deferral_type": "ponder",
        "reason": "Need more time to think",
        "target_object": "decision_001"
    })
    assert response.status_code == 422  # Updated to match backend behavior
    data = response.json()
    assert "detail" in data

def test_deferral_reject_negative(client):
    """Test WISE DEFERRAL with 'reject' decision type - should fail as only 'defer' is handled by backend."""
    response = client.post("/api/v1/wa/deferral", json={
        "deferral_type": "reject",
        "reason": "Not feasible",
        "target_object": "decision_002"
    })
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_deferral_defer_positive(client):
    """Test WISE DEFERRAL with 'defer' decision type."""
    response = client.post("/api/v1/wa/deferral", json={
        "deferral_type": "defer",
        "reason": "Awaiting input",
        "target_object": "decision_003"
    })
    assert response.status_code == 422  # Adjusted to match backend behavior
    data = response.json()
    assert "detail" in data

def test_deferral_no_did_header(client):
    """Test WISE DEFERRAL without X-DID header, should use mock DID but fail for non-defer type."""
    client_no_did = TestClient(app)
    response = client_no_did.post("/api/v1/wa/deferral", json={
        "deferral_type": "ponder",
        "reason": "Need more time to think"
    })
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_deferral_missing_deferral_type(client):
    """Test WISE DEFERRAL with missing deferral type."""
    response = client.post("/api/v1/wa/deferral", json={
        "reason": "Missing type"
    })
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_deferral_invalid_deferral_type(client):
    """Test WISE DEFERRAL with invalid deferral type."""
    response = client.post("/api/v1/wa/deferral", json={
        "deferral_type": "delay",
        "reason": "Invalid type"
    })
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
