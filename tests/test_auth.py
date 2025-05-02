import pytest
import os
import jwt
from fastapi.testclient import TestClient
from cirisnode.main import app

client = TestClient(app)

# Test data
TEST_DID = "did:example:12345"
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")

def test_static_token_bypass():
    # Test with a static token from ALLOWED_BENCHMARK_TOKENS
    response = client.post(
        "/api/v1/benchmarks/run",
        headers={"Authorization": "Bearer sk_test_abc123"},
        json={"scenario": "HE-300"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Benchmark run initiated"

def test_ip_allowlist_bypass():
    # This test assumes the client IP is not in ALLOWED_BENCHMARK_IPS
    # Since we can't control the IP in tests, we'll just check the response
    response = client.post(
        "/api/v1/benchmarks/run",
        headers={"Authorization": "Bearer invalid_token"},
        json={"scenario": "HE-300"}
    )
    assert response.status_code == 401  # Should fail since IP bypass is unlikely in test env

def test_jwt_did_blessing():
    # Issue a JWT with a blessed DID
    response = client.post(
        "/api/v1/did/issue",
        json={"did": TEST_DID}
    )
    assert response.status_code == 200
    token = response.json()["token"]

    # Use the token to run a benchmark
    response = client.post(
        "/api/v1/benchmarks/run",
        headers={"Authorization": f"Bearer {token}"},
        json={"scenario": "HE-300"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Benchmark run initiated"

def test_jwt_did_not_blessed():
    # Issue a JWT with a non-blessed DID
    response = client.post(
        "/api/v1/did/issue",
        json={"did": "did:example:unblessed"}
    )
    assert response.status_code == 200
    token = response.json()["token"]

    # Use the token to run a benchmark - should fail
    response = client.post(
        "/api/v1/benchmarks/run",
        headers={"Authorization": f"Bearer {token}"},
        json={"scenario": "HE-300"}
    )
    assert response.status_code == 403
    assert "Forbidden: DID not blessed" in response.json()["detail"]

def test_invalid_jwt():
    # Use an invalid JWT
    response = client.post(
        "/api/v1/benchmarks/run",
        headers={"Authorization": "Bearer invalid_jwt_token"},
        json={"scenario": "HE-300"}
    )
    assert response.status_code == 401
    assert "Unauthorized" in response.json()["detail"]
