import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app

client = TestClient(app)

def test_wa_defer_submission():
    """Test submitting a deferral request to /wa/defer endpoint"""
    response = client.post(
        "/api/v1/wa/defer",
        json={
            "thought_id": "test123",
            "reason": "incomplete",
            "timestamp": "2025-05-08T15:00:00"
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "ok"
    assert "entry_id" in result

def test_wa_ticket_submission():
    """Test submitting a ticket to /wa/ticket endpoint"""
    response = client.post(
        "/api/v1/wa/ticket",
        json={"text": "Test ticket submission"}
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "submitted"
    assert "ticket_id" in result
