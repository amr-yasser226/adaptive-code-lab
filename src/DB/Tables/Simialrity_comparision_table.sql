CREATE TABLE IF NOT EXISTS similarity_comparisons (
    similarity_id INTEGER NOT NULL,
    compared_submission_id INTEGER NOT NULL,
    match_score REAL NOT NULL CHECK(match_score >= 0.0 AND match_score <= 1.0),
    note TEXT,
    matched_segments TEXT,
    PRIMARY KEY (similarity_id, compared_submission_id),
    FOREIGN KEY (similarity_id) REFERENCES similarity_flags(id) ON DELETE CASCADE,
    FOREIGN KEY (compared_submission_id) REFERENCES submissions(id) ON DELETE CASCADE
);