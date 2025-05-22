from fastapi.testclient import TestClient
from cirisnode.main import app
from cirisnode.api.auth.dependencies import create_access_token

client = TestClient(app)

def get_auth_header():
    token = create_access_token(data={"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}

def test_get_audit_logs():
    headers = get_auth_header()
    response = client.get("/api/v1/audit/logs", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)

def test_get_audit_logs_with_filters():
    headers = get_auth_header()
    response = client.get(
        "/api/v1/audit/logs?type=benchmark_run&from_date=2023-01-01&to_date=2023-12-31",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)
