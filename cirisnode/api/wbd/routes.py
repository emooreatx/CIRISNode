from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Optional
import uuid
from cirisnode.db.active_tasks import get_active_wbd_tasks, submit_wbd_task, resolve_wbd_task

# Placeholder implementations for missing functions
def get_active_wbd_tasks(state=None, since=None):
    return []

def submit_wbd_task(task_id, agent_task_id, payload):
    pass

def resolve_wbd_task(task_id, decision, comment=None):
    pass

wbd_router = APIRouter(prefix="/api/v1/wbd", tags=["wbd"])

class WBDSubmitRequest(BaseModel):
    agent_task_id: str
    payload: dict

class WBDTaskResponse(BaseModel):
    id: str
    agent_task_id: str
    status: str
    created_at: str
    decision: Optional[str] = None
    comment: Optional[str] = None

class WBDTaskListResponse(BaseModel):
    tasks: List[WBDTaskResponse]

from fastapi import Depends
from cirisnode.database import get_db

@wbd_router.post("/submit", response_model=WBDTaskResponse)
async def submit_wbd_task_route(request: WBDSubmitRequest, db=Depends(get_db)):
    """
    Agents submit deferral packages from agents.
    """
    import datetime
    from cirisnode.utils.audit import write_audit_log
    task_id = str(uuid.uuid4())
    conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
    conn.execute(
        """
        INSERT INTO wbd_tasks (id, agent_task_id, status, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (task_id, request.agent_task_id, "open", datetime.datetime.utcnow())
    )
    conn.commit()
    # Write audit log
    try:
        write_audit_log(
            db=conn,
            actor=None,
            event_type="wbd_submit",
            payload={"task_id": task_id, "agent_task_id": request.agent_task_id},
            details={"payload": request.payload}
        )
    except Exception as e:
        print(f"WARNING: Failed to write audit log for wbd_submit: {e}")
    return WBDTaskResponse(id=task_id, agent_task_id=request.agent_task_id, status="open", created_at=str(datetime.datetime.utcnow()))

@wbd_router.get("/tasks", response_model=WBDTaskListResponse)
async def get_wbd_tasks(state: Optional[str] = None, since: Optional[str] = None, db=Depends(get_db)):
    """
    List open WBD tasks. Filters: `state`, `since`.
    """
    conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
    query = "SELECT id, agent_task_id, status, created_at, decision, comment FROM wbd_tasks WHERE 1=1"
    params = []
    if state:
        query += " AND status = ?"
        params.append(state)
    if since:
        query += " AND created_at >= ?"
        params.append(since)
    query += " ORDER BY created_at DESC"
    cur = conn.execute(query, tuple(params))
    rows = cur.fetchall()
    tasks = [
        WBDTaskResponse(
            id=str(row[0]),
            agent_task_id=str(row[1]),
            status=str(row[2]),
            created_at=str(row[3]),
            decision=str(row[4]) if row[4] is not None else None,
            comment=str(row[5]) if row[5] is not None else None
        )
        for row in rows
    ]
    return WBDTaskListResponse(tasks=tasks)

@wbd_router.post("/tasks/{task_id}/resolve", response_model=WBDTaskResponse)
async def resolve_wbd_task_route(
    task_id: str,
    decision: str = Body(..., embed=True),
    comment: Optional[str] = Body(None, embed=True),
    db=Depends(get_db)
):
    """
    Resolve a WBD task with a decision (`approve` or `reject`).
    """
    import datetime
    from cirisnode.utils.audit import write_audit_log
    if decision not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid decision. Must be 'approve' or 'reject'.")
    conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
    cur = conn.execute(
        "SELECT agent_task_id FROM wbd_tasks WHERE id = ?",
        (task_id,)
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="WBD task not found")
    agent_task_id = row[0]
    conn.execute(
        """
        UPDATE wbd_tasks
        SET status = ?, resolved_at = ?, decision = ?, comment = ?
        WHERE id = ?
        """,
        ("resolved", datetime.datetime.utcnow(), decision, comment, task_id)
    )
    conn.commit()
    # Write audit log
    try:
        write_audit_log(
            db=conn,
            actor=None,
            event_type="wbd_resolve",
            payload={"task_id": task_id, "decision": decision},
            details={"comment": comment}
        )
    except Exception as e:
        print(f"WARNING: Failed to write audit log for wbd_resolve: {e}")
    return WBDTaskResponse(
        id=task_id,
        agent_task_id=agent_task_id,
        status="resolved",
        created_at=str(datetime.datetime.utcnow()),
        decision=decision,
        comment=comment
    )
