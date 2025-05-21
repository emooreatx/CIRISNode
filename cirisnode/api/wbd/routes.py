from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Optional
import uuid
from cirisnode.db.active_tasks import get_active_wbd_tasks, submit_wbd_task, resolve_wbd_task

router = APIRouter(prefix="/api/v1/wbd", tags=["wbd"])

class WBDSubmitRequest(BaseModel):
    agent_task_id: str
    payload: dict

class WBDTaskResponse(BaseModel):
    id: str
    agent_task_id: str
    status: str
    decision: Optional[str] = None
    comment: Optional[str] = None

class WBDTaskListResponse(BaseModel):
    tasks: List[WBDTaskResponse]

@router.post("/submit", response_model=WBDTaskResponse)
async def submit_wbd_task_route(request: WBDSubmitRequest):
    """
    Agents submit deferral packages from agents.
    """
    task_id = str(uuid.uuid4())
    submit_wbd_task(task_id, request.agent_task_id, request.payload)
    return WBDTaskResponse(id=task_id, agent_task_id=request.agent_task_id, status="open")

@router.get("/tasks", response_model=WBDTaskListResponse)
async def get_wbd_tasks(state: Optional[str] = None, since: Optional[str] = None):
    """
    List open WBD tasks. Filters: `state`, `since`.
    """
    tasks = get_active_wbd_tasks(state, since)
    return WBDTaskListResponse(tasks=tasks)

@router.post("/tasks/{task_id}/resolve", response_model=WBDTaskResponse)
async def resolve_wbd_task_route(task_id: str, decision: str = Body(..., embed=True), comment: Optional[str] = Body(None, embed=True)):
    """
    Resolve a WBD task with a decision (`approve` or `reject`).
    """
    if decision not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid decision. Must be 'approve' or 'reject'.")
    resolve_wbd_task(task_id, decision, comment)
    return WBDTaskResponse(id=task_id, agent_task_id="", status="resolved", decision=decision, comment=comment)
