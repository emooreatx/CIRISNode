from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Optional
import uuid
from cirisnode.db.active_tasks import get_active_wbd_tasks, submit_wbd_task, resolve_wbd_task

wbd_router = APIRouter(prefix="/api/v1/wbd", tags=["wbd"])

# Placeholder implementations for missing functions
def get_active_wbd_tasks(state=None, since=None):
    return []

def submit_wbd_task(task_id, agent_task_id, payload):
    pass

def resolve_wbd_task(task_id, decision, comment=None):
    pass

from fastapi import Depends
from cirisnode.database import get_db

@wbd_router.get("/tasks")
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
        {
            "id": str(row[0]),
            "agent_task_id": str(row[1]),
            "status": str(row[2]),
            "created_at": str(row[3]),
            "decision": str(row[4]) if row[4] is not None else None,
            "comment": str(row[5]) if row[5] is not None else None,
            "archived": bool(row[6]) if len(row) > 6 else False
        }
        for row in rows
    ]
    return {"tasks": tasks}

# ... rest of the file unchanged ...
