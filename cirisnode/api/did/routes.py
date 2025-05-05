from fastapi import APIRouter, Request, HTTPException, status
from typing import Dict, Any
import jwt
from datetime import datetime, timedelta
import os
import logging

# Setup logging
logger = logging.getLogger(__name__)

did_router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET environment variable must be set")
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
        
        # Use a mocked user ID based on DID for demonstration
        mocked_user_id = f"user_{did.split(':')[-1]}" if ':' in did else f"user_{did}"
        payload = {
            "sub": mocked_user_id,
            "did": did,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Issued token for DID: {did}")
        return {"token": token}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error issuing DID token: {str(e)}")
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
        logger.info(f"Verified token for DID: {payload.get('did')}")
        return {"valid": True, "did": payload.get("did")}
    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: Token expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        logger.warning("Token verification failed: Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error verifying DID token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
