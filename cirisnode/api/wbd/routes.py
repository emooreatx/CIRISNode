from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

wbd_router = APIRouter(prefix="/api/v1/wbd", tags=["wbd"])

# In-memory store for demonstration
wbd_tasks = {}

class WBDSubmitRequest(BaseModel):
    agent_task_id: str
    payload: str

class WBDResolveRequest(BaseModel):
    decision: str  # "approve" or "reject"
    comment: Optional[str] = None

@wbd_router.post("/submit")
def submit_wbd_task(request: WBDSubmitRequest):
    task_id = str(uuid.uuid4())
    wbd_tasks[task_id] = {
        "agent_task_id": request.agent_task_id,
        "payload": request.payload,
        "status": "open",
        "created_at": datetime.utcnow().isoformat(),
        "decision": None,
        "comment": None
    }
    return {
        "status": "success",
        "task_id": task_id,
        "message": "WBD task submitted successfully",
        "details": {
            "agent_task_id": request.agent_task_id,
            "payload": request.payload,
            "status": "open",
            "created_at": wbd_tasks[task_id]["created_at"],
        },
    }

@wbd_router.get("/tasks")
def get_wbd_tasks():
    return {"tasks": [
        {"id": task_id, **task}
        for task_id, task in wbd_tasks.items()
    ]}

@wbd_router.post("/tasks/{task_id}/resolve")
def resolve_wbd_task(task_id: str, request: WBDResolveRequest):
    if task_id not in wbd_tasks:
        raise HTTPException(status_code=404, detail=f"WBD task with ID {task_id} not found")
    if request.decision not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Decision must be 'approve' or 'reject'")
    wbd_tasks[task_id]["status"] = "resolved"
    wbd_tasks[task_id]["decision"] = request.decision
    wbd_tasks[task_id]["comment"] = request.comment
    return {
        "status": "success",
        "task_id": task_id,
        "message": f"WBD task resolved with decision: {request.decision}",
        "details": {
            "decision": request.decision,
            "comment": request.comment,
            "resolved_at": datetime.utcnow().isoformat(),
        },
    }
