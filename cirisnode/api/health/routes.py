from fastapi import APIRouter, Depends
from cirisnode.api.auth.dependencies import get_public_key
from cirisnode.config import settings

router = APIRouter()

@router.get("/health")
async def health_check(public_key: str = Depends(get_public_key)):
    return {
        "status": "ok",
        "version": VERSION,
        "pubkey": public_key
    }
