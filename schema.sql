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
