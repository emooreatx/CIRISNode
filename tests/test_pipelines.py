import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app

client = TestClient(app)

def test_pipeline_run_and_results():
    # Since authentication is bypassed, we can directly test the endpoint with a static token
    response = client.post(
        "/api/v1/benchmarks/run",
        headers={"Authorization": "Bearer sk_test_abc123"},
        json={"scenario": "HE-300"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Benchmark run initiated"
