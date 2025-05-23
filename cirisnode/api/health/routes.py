from fastapi import APIRouter, Depends, Request
from cirisnode.config import settings
from datetime import datetime

router = APIRouter(prefix="/api/v1/health", tags=["health"])

@router.get("")
def health_check(request: Request):
    return {
        "status": "ok",
        "version": "1.0.0",
        "pubkey": "dummy-pubkey",
        "message": "CIRISNode is healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
