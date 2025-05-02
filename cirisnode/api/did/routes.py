from fastapi import APIRouter, Request, HTTPException, status
from typing import Dict, Any
import jwt
from datetime import datetime, timedelta
import os

did_router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"

@did_router.post("/issue")
async def issue_did(request: Request):
    try:
        data = await request.json()
        if not isinstance(data, dict):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
        did = data.get("did")
        if not did:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DID is required")
        
        payload = {
            "sub": "user_id",  # Placeholder for user ID
            "did": did,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"token": token}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")

@did_router.post("/verify")
async def verify_did(request: Request):
    try:
        data = await request.json()
        if not isinstance(data, dict):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
        token = data.get("token")
        if not token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is required")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "did": payload.get("did")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
