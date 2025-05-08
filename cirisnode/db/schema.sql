CREATE TABLE IF NOT EXISTS active_tasks (
    id INTEGER PRIMARY KEY,
    thought_id TEXT,
    reason TEXT,
    timestamp TEXT,
    coherence TEXT,
    entropy TEXT
);
