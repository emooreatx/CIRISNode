from fastapi import APIRouter, Depends, Request
from datetime import datetime
from cirisnode.dao.config_dao import get_config
from cirisnode.schema.config_models import CIRISConfigV1

router = APIRouter(prefix="/api/v1/health", tags=["health"])

@router.get("")
def health_check(request: Request, config: CIRISConfigV1 = Depends(get_config)):
    return {
        "status": "ok",
        "version": config.version,
        "pubkey": "dummy-pubkey",
        "message": "CIRISNode is healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
