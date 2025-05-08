import sqlite3
from cirisnode.schema.wa_models import DeferRequest

def get_db():
    conn = sqlite3.connect('cirisnode/db/active_tasks.db')
    return conn

def store_deferral(req: DeferRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO active_tasks (thought_id, reason, timestamp, coherence, entropy)
        VALUES (?, ?, ?, ?, ?)
    """, (req.thought_id, req.reason, req.timestamp, "NA", "NA"))
    conn.commit()
    return cursor.lastrowid
