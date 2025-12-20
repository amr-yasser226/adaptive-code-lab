CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    content TEXT,
    language TEXT DEFAULT 'python',
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id)
);

CREATE INDEX IF NOT EXISTS idx_drafts_user_assignment ON drafts(user_id, assignment_id);
