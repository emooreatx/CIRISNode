from fastapi.testclient import TestClient
from cirisnode.main import app

client = TestClient(app)

def test_did_issue_and_verify():
    issue = client.post("/api/v1/did/issue")
    assert issue.status_code == 200
    did_info = issue.json()
    
    verify = client.post("/api/v1/did/verify", json={"did": did_info["did"]})
    assert verify.status_code == 200
