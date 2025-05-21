from fastapi import APIRouter, HTTPException, status, Depends
from cirisnode.api.auth.dependencies import verify_token
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from cirisnode.database import get_db
import sqlite3
import logging
import hashlib
import json
from cirisnode.utils.encryption import encrypt_data, decrypt_data

# Setup logging
logger = logging.getLogger(__name__)

audit_router = APIRouter(tags=["audit"])

@audit_router.get("/test")
def test_audit_router():
    return {"message": "Audit router is working"}

class AuditLogEntry(BaseModel):
    id: int
    timestamp: str
    actor: str
    event_type: str
    payload_sha256: str
    raw_json: str

@audit_router.get("/logs", response_model=dict)
def get_audit_logs(type: Optional[str] = None, from_date: Optional[str] = None, to_date: Optional[str] = None, db: sqlite3.Connection = Depends(get_db), token: Dict = Depends(verify_token)):
    """Retrieve audit logs with optional filters for event type and date range."""
    try:
        query = "SELECT id, ts, actor, event_type, payload_sha256, raw_json FROM audit WHERE 1=1"
        params = []
        if type:
            query += " AND event_type = ?"
            params.append(type)
        if from_date:
            query += " AND ts >= ?"
            params.append(from_date)
        if to_date:
            query += " AND ts <= ?"
            params.append(to_date)
        
        logs = db.execute(query, params).fetchall()
        logger.info(f"Retrieved {len(logs)} audit logs with filters type={type}, from={from_date}, to={to_date}")
        print("Audit logs endpoint was accessed")
        return {"logs": [
            AuditLogEntry(
                id=log[0],
                timestamp=log[1],
                actor=log[2],
                event_type=log[3],
                payload_sha256=log[4],
                raw_json=decrypt_data(log[5])
            )
            for log in logs
        ]}
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving audit logs: {str(e)}")

def log_audit_event(db: sqlite3.Connection, actor: str, event_type: str, payload: Dict[str, Any]):
    """Helper function to log an audit event. This can be called internally by other endpoints."""
    try:
        raw_json = encrypt_data(json.dumps(payload))
        payload_sha256 = hashlib.sha256(decrypt_data(raw_json).encode()).hexdigest()
        timestamp = datetime.utcnow().isoformat()
        
        db.execute(
            "INSERT INTO audit (ts, actor, event_type, payload_sha256, raw_json) VALUES (?, ?, ?, ?, ?)",
            (timestamp, actor, event_type, payload_sha256, raw_json)
        )
        db.commit()
        logger.info(f"Audit event logged: {event_type} by {actor}")
    except Exception as e:
        logger.error(f"Error logging audit event: {str(e)}")
        # Do not raise exception to avoid disrupting the main operation
