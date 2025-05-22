from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from cirisnode.database import get_db
import uuid
import datetime
import json

agent_router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

class AgentEventRequest(BaseModel):
    agent_uid: str
    event: dict

@agent_router.post("/events")
async def post_agent_event(request: AgentEventRequest, db=Depends(get_db)):
    """
    Agents push Task / Thought / Action events for observability.
    """
    event_id = str(uuid.uuid4())
    conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
    conn.execute(
        """
        INSERT INTO agent_events (id, node_ts, agent_uid, event_json)
        VALUES (?, ?, ?, ?)
        """,
        (event_id, datetime.datetime.utcnow(), request.agent_uid, json.dumps(request.event))
    )
    conn.commit()
    # Write audit log
    try:
        from cirisnode.utils.audit import write_audit_log
        write_audit_log(
            db=conn,
            actor=request.agent_uid,
            event_type="agent_event",
            payload={"event_id": event_id},
            details=request.event
        )
    except Exception as e:
        print(f"WARNING: Failed to write audit log for agent_event: {e}")
    return {"id": event_id, "status": "ok"}
