from fastapi import APIRouter, Response, status, Request
import uuid

wa_router = APIRouter(tags=["wa"])

@wa_router.post("/authenticate")
async def authenticate():
    from cirisnode.api.did.routes import SECRET_KEY, ALGORITHM
    from datetime import datetime, timedelta
    import jwt
    
    payload = {
        "sub": "agent_user",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"status": "authenticated", "token": token}

@wa_router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    return {"user_id": user_id, "profile": "mocked profile data"}

@wa_router.post("/logout")
async def logout():
    return {"status": "logged out"}

@wa_router.post("/ticket")
async def submit_ticket(response: Response):
    ticket_id = str(uuid.uuid4())
    # Mocked ticket submission logic
    return {"ticket_id": ticket_id, "status": "submitted"}

@wa_router.get("/status/{ticket_id}")
async def check_ticket_status(ticket_id: str):
    # Mocked status check logic
    return {"ticket_id": ticket_id, "status": "processing"}

@wa_router.post("/run")
async def run_agent_request(request: Request):
    import httpx
    try:
        # Get input from agent request
        data = await request.json()
        query = data.get("text", "Test query to Ollama")
        
        # Send query to Ollama (assuming it's running on default port 11434)
        async with httpx.AsyncClient() as client:
            ollama_response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral:latest",  # Using available model
                    "prompt": query,
                    "stream": False
                },
                timeout=30.0
            )
            if ollama_response.status_code == 200:
                result = ollama_response.json()
                return {"status": "success", "decision": result.get("response", "No response from Ollama")}
            else:
                return {"status": "error", "decision": f"Ollama request failed with status {ollama_response.status_code}"}
    except Exception as e:
        return {"status": "error", "decision": f"Error connecting to Ollama: {str(e)}"}
