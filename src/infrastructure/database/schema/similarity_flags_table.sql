CREATE TABLE IF NOT EXISTS similarity_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL UNIQUE,
    similarity_score REAL NOT NULL CHECK(similarity_score >= 0.0 AND similarity_score <= 1.0),
    highlighted_spans TEXT,
    is_reviewed INTEGER DEFAULT 0 CHECK(is_reviewed IN (0,1)),
    reviewed_by INTEGER,
    review_notes TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);