from fastapi import APIRouter, Depends, Query
from cirisnode.database import get_db
from cirisnode.utils.audit import fetch_audit_logs

audit_router = APIRouter(prefix="/api/v1/audit", tags=["audit"])

@audit_router.get("/logs")
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db=Depends(get_db)
):
    """
    Get audit logs from the database.
    """
    conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
    logs = fetch_audit_logs(conn, limit=limit, offset=offset)
    return {"logs": logs}
