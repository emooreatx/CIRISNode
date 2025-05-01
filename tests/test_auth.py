import pytest
from fastapi.testclient import TestClient
from cirisnode.main import app
import jwt
from datetime import datetime, timedelta
from cirisnode.api.did.routes import SECRET_KEY, ALGORITHM, TOKEN_EXPIRY_MINUTES

client = TestClient(app)

def test_unauthorized_access():
    response = client.get("/api/v1/did/did:example:123456")
    assert response.status_code == 200, "Expected 200 OK due to temporary authentication bypass"

def test_authorized_access():
    # Create a valid token
    did = "did:example:123456"
    expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    token = jwt.encode({"sub": did, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)
    
    response = client.get(
        f"/api/v1/did/{did}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, "Expected 200 OK for access with valid token"
