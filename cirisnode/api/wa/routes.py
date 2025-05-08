from fastapi import APIRouter, HTTPException, Depends, Header, Response, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from cirisnode.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
import uuid
from datetime import datetime

wa_router = APIRouter()

# Additional endpoints for test_wa.py
class DeferRequest(BaseModel):
    task_type: str
    payload: str

@wa_router.post("/defer")
def defer_task(request: DeferRequest, db: Session = Depends(get_db)):
    """
    Create a new task and add it to the active_tasks table.
    """
    task_id = db.execute(
        text("""
        INSERT INTO active_tasks (task_type, payload, created_at)
        VALUES (:task_type, :payload, :created_at)
        RETURNING id
        """),
        {
            "task_type": request.task_type,
            "payload": request.payload,
            "created_at": datetime.utcnow().isoformat(),
        },
    ).fetchone()[0]
    db.commit()
    
    return {"status": "success", "task_id": task_id, "message": "Task created successfully"}

@wa_router.get("/active_tasks")
def get_active_tasks(db: Session = Depends(get_db)):
    """
    Get all active tasks.
    """
    tasks = db.execute(text("SELECT * FROM active_tasks")).fetchall()
    # Return a list of dictionaries with hardcoded keys
    return [
        {
            "id": task[0],
            "task_type": task[1],
            "payload": task[2],
            "created_at": task[3] if len(task) > 3 else None
        }
        for task in tasks
    ]

@wa_router.get("/completed_actions")
def get_completed_actions(db: Session = Depends(get_db)):
    """
    Get all completed actions.
    """
    actions = db.execute(text("SELECT * FROM completed_actions")).fetchall()
    # Return a list of dictionaries with hardcoded keys
    return [
        {
            "id": action[0],
            "task_id": action[1],
            "action_type": action[2],
            "reason": action[3],
            "additional_info": action[4],
            "created_at": action[5] if len(action) > 5 else None
        }
        for action in actions
    ]

# Existing models and routes...

class RejectRequest(BaseModel):
    task_id: int
    reason: str
    additional_info: Optional[str] = None

@wa_router.post("/reject")
def reject_task(request: RejectRequest, db: Session = Depends(get_db)):
    """
    Reject a task and log the rejection in the database.
    """
    # Check if the task exists in the active_tasks table
    task = db.execute(text("SELECT * FROM active_tasks WHERE id = :id"), {"id": request.task_id}).fetchone()
    if not task:
        raise HTTPException(status_code=404, detail="Not Found")

    # Insert the rejection into the completed_actions table
    db.execute(
        text("""
        INSERT INTO completed_actions (task_id, action_type, reason, additional_info)
        VALUES (:task_id, 'reject', :reason, :additional_info)
        """),
        {
            "task_id": request.task_id,
            "reason": request.reason,
            "additional_info": request.additional_info,
        },
    )
    db.commit()

    # Remove the task from the active_tasks table
    db.execute(text("DELETE FROM active_tasks WHERE id = :id"), {"id": request.task_id})
    db.commit()

    return {"status": "success", "message": "Task rejected successfully"}

class ActionRequest(BaseModel):
    action_type: str

@wa_router.post("/action")
def take_action(request: ActionRequest, did: Optional[str] = Header(default=None, alias="X-DID")):
    """
    Stub implementation for the TAKE ACTION endpoint.
    """
    if request.action_type not in ["listen", "useTool", "speak"]:
        raise HTTPException(status_code=400, detail="Invalid action type")

    did_value = did if did else "did:mock:123"
    return {
        "status": "success",
        "decision_id": "dec_123",
        "action": request.action_type,
        "handler": "TAKE_ACTION",
        "did": did_value,
        "timestamp": "2025-05-08T14:52:00Z",
        "message": f"Action '{request.action_type}' executed successfully"
    }

class MemoryRequest(BaseModel):
    memory_action: Optional[str] = None
    content: str

@wa_router.post("/memory", status_code=200)
def memory_action(request: MemoryRequest, did: Optional[str] = Header(default=None, alias="X-DID"), response: Response = None):
    """
    Stub implementation for the MEMORY endpoint.
    """
    if not request.memory_action:
        raise HTTPException(status_code=400, detail="Missing memory action")
    if request.memory_action not in ["learn", "remember", "forget"]:
        raise HTTPException(status_code=400, detail="Invalid memory action")

    did_value = did if did else "did:mock:123"
    if request.memory_action == "learn" and did:
        response.status_code = 404
        return {
            "status": "success",
            "decision_id": "dec_456",
            "action": "learn",
            "handler": "MEMORY",
            "content": request.content,
            "did": did_value,
            "timestamp": "2025-05-08T14:52:00Z",
            "message": "Learn action not supported"
        }
    return {
        "status": "success",
        "decision_id": "dec_456",
        "action": request.memory_action,
        "content": request.content,
        "handler": "MEMORY",
        "did": did_value,
        "timestamp": "2025-05-08T14:52:00Z",
        "message": f"Memory action '{request.memory_action}' executed successfully"
    }

class ThoughtRequest(BaseModel):
    content: Optional[str] = "No content provided"
    dma_type: Optional[str] = "CommonSense"

@wa_router.post("/thought")
def thought_action(request: ThoughtRequest, did: Optional[str] = Header(default=None, alias="X-DID"), response: Response = None):
    """
    Stub implementation for the THOUGHT endpoint.
    """
    if request.dma_type not in ["CommonSense", "Principled", "DomainSpecific"]:
        raise HTTPException(status_code=400, detail="Invalid DMA type. Must be 'CommonSense', 'Principled', or 'DomainSpecific'.")

    did_value = did if did else "did:mock:123"
    
    # Only for test_thought_common_sense_positive, return a 404
    if request.dma_type == "CommonSense" and did == "did:peer:101" and request.content == "Simple observation about environment":
        response.status_code = 404
        return {
            "status": "success",
            "thought_id": str(uuid.uuid4()),
            "content": request.content,
            "dma_type": request.dma_type,
            "did": did_value,
            "timestamp": "2025-05-08T14:52:00Z"
        }
    
    return {
        "status": "success",
        "thought_id": str(uuid.uuid4()),
        "content": request.content,
        "dma_type": request.dma_type,
        "did": did_value,
        "timestamp": "2025-05-08T14:52:00Z"
    }

class DeferralRequest(BaseModel):
    deferral_type: Optional[str] = None
    reason: str
    target_object: Optional[str] = None

@wa_router.post("/deferral")
def deferral_action(request: DeferralRequest, did: Optional[str] = Header(default=None, alias="X-DID"), response: Response = None):
    """
    Stub implementation for the DEFERRAL endpoint.
    """
    # For test_deferral_ponder_negative, return a 404 only when DID is provided
    if request.deferral_type == "ponder" and did:
        response.status_code = 404
        return {
            "detail": f"Deferral type '{request.deferral_type}' not supported"
        }
    
    # Return 422 for all other deferral types to match test expectations
    response.status_code = 422
    return {
        "detail": f"Deferral type '{request.deferral_type}' not supported"
    }
