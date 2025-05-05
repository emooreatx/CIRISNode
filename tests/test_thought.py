import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app

@pytest.fixture
def client():
    """Create a TestClient instance with default X-DID header."""
    return TestClient(app, headers={"X-DID": "did:peer:101"})

def test_thought_common_sense_positive(client):
    """Test THOUGHT with 'CommonSense' DMA type."""
    response = client.post("/api/v1/wa/thought", json={
        "content": "Simple observation about environment",
        "dma_type": "CommonSense"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "thought_id" in data
    assert data["content"] == "Simple observation about environment"
    assert data["dma_type"] == "CommonSense"
    assert data["did"] == "did:peer:101"
    assert "timestamp" in data

def test_thought_principled_positive(client):
    """Test THOUGHT with 'Principled' DMA type."""
    response = client.post("/api/v1/wa/thought", json={
        "content": "Ethical consideration",
        "dma_type": "Principled"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "thought_id" in data
    assert data["content"] == "Ethical consideration"
    assert data["dma_type"] == "Principled"
    assert data["did"] == "did:peer:101"
    assert "timestamp" in data

def test_thought_domain_specific_positive(client):
    """Test THOUGHT with 'DomainSpecific' DMA type."""
    response = client.post("/api/v1/wa/thought", json={
        "content": "Technical analysis",
        "dma_type": "DomainSpecific"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "thought_id" in data
    assert data["content"] == "Technical analysis"
    assert data["dma_type"] == "DomainSpecific"
    assert data["did"] == "did:peer:101"
    assert "timestamp" in data

def test_thought_no_did_header(client):
    """Test THOUGHT without X-DID header, should use mock DID."""
    client_no_did = TestClient(app)
    response = client_no_did.post("/api/v1/wa/thought", json={
        "content": "Observation without DID",
        "dma_type": "CommonSense"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "thought_id" in data
    assert data["content"] == "Observation without DID"
    assert data["dma_type"] == "CommonSense"
    assert data["did"].startswith("did:mock:")
    assert "timestamp" in data

def test_thought_no_dma_type(client):
    """Test THOUGHT with missing DMA type, should default to CommonSense."""
    response = client.post("/api/v1/wa/thought", json={
        "content": "Observation without DMA type"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "thought_id" in data
    assert data["content"] == "Observation without DMA type"
    assert data["dma_type"] == "CommonSense"
    assert data["did"] == "did:peer:101"
    assert "timestamp" in data

def test_thought_invalid_dma_type(client):
    """Test THOUGHT with invalid DMA type."""
    response = client.post("/api/v1/wa/thought", json={
        "content": "Observation with invalid DMA",
        "dma_type": "InvalidDMA"
    })
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid DMA type" in data["detail"]

def test_thought_malformed_request(client):
    """Test THOUGHT with malformed request body."""
    response = client.post("/api/v1/wa/thought", json={
        "invalid_field": "Malformed request"
    })
    assert response.status_code == 200  # Since content is optional, it should still pass with default values
    data = response.json()
    assert data["status"] == "success"
    assert "thought_id" in data
    assert data["content"] == "No content provided"
    assert data["dma_type"] == "CommonSense"
    assert data["did"] == "did:peer:101"
    assert "timestamp" in data
