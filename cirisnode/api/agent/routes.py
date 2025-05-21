from fastapi import APIRouter, HTTPException, status, Depends
from cirisnode.api.auth.dependencies import verify_token
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from cirisnode.database import get_db
import sqlite3
import logging
import json
from cirisnode.utils.encryption import encrypt_data, decrypt_data

# Setup logging
logger = logging.getLogger(__name__)

agent_router = APIRouter(tags=["agent"])

class AgentEvent(BaseModel):
    agent_uid: str
    event_json: Dict[str, Any]

@agent_router.post("/events", response_model=dict)
def push_agent_event(event: AgentEvent, db: sqlite3.Connection = Depends(get_db), token: Dict = Depends(verify_token)):
    """Endpoint for agents to push Task/Thought/Action events for observability."""
    try:
        node_ts = datetime.utcnow().isoformat()
        event_json_str = decrypt_data(event.event_json)
        
        cursor = db.execute(
            "INSERT INTO agent_events (node_ts, agent_uid, event_json) VALUES (?, ?, ?)",
            (node_ts, event.agent_uid, encrypt_data(event_json_str))
        )
        event_id = cursor.lastrowid
        db.commit()
        
        # Log the agent event to audit
        from cirisnode.api.audit.routes import log_audit_event
        event_payload = {
            "action": "push_agent_event",
            "event_id": event_id,
            "agent_uid": event.agent_uid
        }
        log_audit_event(db, event.agent_uid, "agent_event", event_payload)
        
        logger.info(f"Agent event pushed by UID: {event.agent_uid}, Event ID: {event_id}")
        return {"status": "success", "event_id": event_id, "message": "Agent event recorded successfully"}  # Ensure JSON response
    except Exception as e:
        logger.error(f"Error pushing agent event: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error pushing agent event: {str(e)}")
