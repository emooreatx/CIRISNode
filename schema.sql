-- Schema for CIRISNode database

-- Table for active tasks
CREATE TABLE IF NOT EXISTS active_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for completed actions
CREATE TABLE IF NOT EXISTS completed_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    reason TEXT,
    additional_info TEXT,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES active_tasks (id)
);

-- Table for audit logs
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    payload TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for WBD tasks
CREATE TABLE IF NOT EXISTS wbd_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_task_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decision TEXT,
    comment TEXT
);
