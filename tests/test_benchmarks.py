from fastapi.testclient import TestClient
from cirisnode.main import app

client = TestClient(app)

def test_benchmark_workflow():
    token = client.post("/api/v1/did/issue").json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Kick off a benchmark
    response = client.post("/api/v1/benchmarks/run", headers=headers, json={"scenario": "HE-300"})
    assert response.status_code == 200
    run_id = response.json().get("run_id")
    
    # Immediately poll for status
    status = client.get(f"/api/v1/benchmarks/status/{run_id}", headers=headers)
    assert status.status_code == 200
