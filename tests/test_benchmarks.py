import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app

client = TestClient(app)

def test_benchmark_workflow():
    # Since authentication is bypassed in the current setup, we can directly test the endpoint
    response = client.post(
        "/api/v1/benchmarks/run",
        headers={"Authorization": "Bearer sk_test_abc123"},
        json={"scenario": "HE-300"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Benchmark run initiated"
    assert response.json()["scenario"] == "HE-300"
