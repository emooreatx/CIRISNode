from fastapi.testclient import TestClient
from cirisnode.main import app

client = TestClient(app)

def test_jwt_issue_and_protected_access():
    # Issue a DID (mocked, should return a token)
    response = client.post("/api/v1/did/issue")
    assert response.status_code == 200
    token = response.json()["token"]

    # Access a protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    protected = client.get("/api/v1/benchmarks/status/mock_id", headers=headers)
    assert protected.status_code in [200, 404, 422]  # depends on mocked data
