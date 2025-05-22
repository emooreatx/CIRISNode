import sqlite3
from cirisnode.schema.wa_models import DeferRequest
from cirisnode.utils.encryption import decrypt_data

def get_db():
    conn = sqlite3.connect('cirisnode/db/cirisnode.db')
    return conn

def get_active_wbd_tasks(state=None, since=None):
    print("DEBUG: get_active_wbd_tasks called with state:", state, "since:", since)
    conn = get_db()
    query = "SELECT id, agent_task_id, payload, status, created_at FROM wbd_tasks WHERE 1=1"
    params = []
    if state:
        query += " AND status = ?"
        params.append(state)
    if since:
        query += " AND created_at >= ?"
        params.append(since)
    
    tasks = conn.execute(query, params).fetchall()
    print("DEBUG: Retrieved tasks from database:", tasks)
    conn.close()
    return [
        {
            "id": task[0],
            "agent_task_id": task[1],
            "payload": decrypt_data(task[2]),
            "status": task[3],
            "created_at": task[4]
        }
        for task in tasks
    ]

def submit_wbd_task(task):
    # Placeholder implementation
    pass

def resolve_wbd_task(task_id):
    # Placeholder implementation
    pass


def store_deferral(req: DeferRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO active_tasks (thought_id, reason, timestamp, coherence, entropy)
        VALUES (?, ?, ?, ?, ?)
    """, (req.thought_id, req.reason, req.timestamp, "NA", "NA"))
    conn.commit()
    return cursor.lastrowid
