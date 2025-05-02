import pytest
import jwt
from fastapi.testclient import TestClient
from cirisnode.main import app
import os
from datetime import datetime, timedelta

client = TestClient(app)

# Test data
TEST_DID = "did:example:12345"
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")

def test_issue_did():
    response = client.post(
        "/api/v1/did/issue",
        json={"did": TEST_DID}
    )
    assert response.status_code == 200
    assert "token" in response.json()
    
    token = response.json()["token"]
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    assert payload["did"] == TEST_DID
    assert "iat" in payload
    assert "exp" in payload

def test_issue_did_missing():
    response = client.post(
        "/api/v1/did/issue",
        json={}
    )
    assert response.status_code == 400
    assert "DID is required" in response.json()["detail"]

def test_verify_did_valid():
    # First issue a token
    response = client.post(
        "/api/v1/did/issue",
        json={"did": TEST_DID}
    )
    assert response.status_code == 200
    token = response.json()["token"]
    
    # Then verify it
    response = client.post(
        "/api/v1/did/verify",
        json={"token": token}
    )
    assert response.status_code == 200
    assert response.json()["valid"] == True
    assert response.json()["did"] == TEST_DID

def test_verify_did_invalid():
    response = client.post(
        "/api/v1/did/verify",
        json={"token": "invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]

def test_verify_did_expired():
    # Create an expired token
    payload = {
        "sub": "user_id",
        "did": TEST_DID,
        "iat": datetime.utcnow() - timedelta(hours=2),
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    
    response = client.post(
        "/api/v1/did/verify",
        json={"token": token}
    )
    assert response.status_code == 401
    assert "Token expired" in response.json()["detail"]

def test_verify_did_missing():
    response = client.post(
        "/api/v1/did/verify",
        json={}
    )
    assert response.status_code == 400
    assert "Token is required" in response.json()["detail"]
