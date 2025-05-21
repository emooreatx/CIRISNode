from fastapi.testclient import TestClient
from cirisnode.main import app

client = TestClient(app)

def test_get_token():
    response = client.post("/auth/token", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_refresh_token():
    # First, get a token
    response = client.post("/auth/token", data={"username": "testuser", "password": "testpassword"})
    token = response.json()["access_token"]
    
    # Then, refresh the token
    response = client.post("/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
