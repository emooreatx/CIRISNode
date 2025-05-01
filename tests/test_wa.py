from fastapi.testclient import TestClient
from cirisnode.main import app

client = TestClient(app)

def test_wa_ticket_submission():
    token = client.post("/api/v1/did/issue").json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    ticket = client.post("/api/v1/wa/ticket", headers=headers, json={"question": "Should AI be allowed to dream?"})
    assert ticket.status_code == 200
    ticket_id = ticket.json()["ticket_id"]
    
    status = client.get(f"/api/v1/wa/status/{ticket_id}", headers=headers)
    assert status.status_code == 200
