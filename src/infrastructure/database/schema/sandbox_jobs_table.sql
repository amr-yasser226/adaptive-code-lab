CREATE TABLE IF NOT EXISTS sandbox_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    status TEXT DEFAULT 'queued' CHECK(status IN ('queued', 'running', 'completed', 'failed', 'timeout')),
    started_at TEXT,
    completed_at TEXT,
    timeout_seconds INTEGER DEFAULT 5,
    memory_limit_mb INTEGER DEFAULT 256,
    exit_code INTEGER,
    error_message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id)
);

CREATE INDEX IF NOT EXISTS idx_sandbox_jobs_submission ON sandbox_jobs(submission_id);
CREATE INDEX IF NOT EXISTS idx_sandbox_jobs_status ON sandbox_jobs(status);
