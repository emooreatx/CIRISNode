-- Updated schema for SQLite with compatibility for Postgres migration

CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('he300', 'simplebench')),
    status TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    results_url TEXT
);

CREATE TABLE IF NOT EXISTS wbd_tasks (
    id SERIAL PRIMARY KEY,
    agent_task_id TEXT NOT NULL,
    payload TEXT NOT NULL, -- Encrypted
    status TEXT NOT NULL CHECK (status IN ('open', 'resolved', 'sla_breached')),
    decision TEXT,
    comment TEXT,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS audit (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    actor TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    raw_json TEXT NOT NULL -- Encrypted
);

CREATE TABLE IF NOT EXISTS agent_events (
    id SERIAL PRIMARY KEY,
    node_ts TIMESTAMP NOT NULL,
    agent_uid TEXT NOT NULL,
    event_json TEXT NOT NULL -- Encrypted
);
