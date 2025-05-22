from fastapi import APIRouter, Depends
from cirisnode.config import settings

router = APIRouter(prefix="/api/v1")

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",  # Placeholder version
    }
