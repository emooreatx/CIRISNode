CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL, -- 'he300' or 'simplebench'
    status TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    results_url TEXT,
    results_json TEXT -- JSON string of results
);

CREATE TABLE IF NOT EXISTS wbd_tasks (
    id TEXT PRIMARY KEY,
    agent_task_id TEXT NOT NULL,
    status TEXT NOT NULL, -- 'open', 'resolved', 'sla_breached'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    decision TEXT,
    comment TEXT
);

CREATE TABLE IF NOT EXISTS agent_events (
    id TEXT PRIMARY KEY,
    node_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_uid TEXT,
    event_json TEXT
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actor VARCHAR(128),
    event_type VARCHAR(64) NOT NULL,
    payload_sha256 VARCHAR(128),
    details JSONB
);
