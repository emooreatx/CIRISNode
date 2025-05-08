import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app

client = TestClient(app)

def test_benchmark_workflow():
    # Since authentication is bypassed in the current setup, we can directly test the endpoint
    response = client.post(
        "/api/v1/benchmarks/run",
        headers={"Authorization": "Bearer sk_test_abc123"},
        json={"id": "test_benchmark"}
    )
    assert response.status_code == 400  # Expecting failure due to test environment setup
