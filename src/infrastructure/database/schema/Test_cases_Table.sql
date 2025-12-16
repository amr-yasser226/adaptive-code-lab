CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    stdin TEXT,
    descripion TEXT,
    expected_out TEXT NOT NULL,
    timeout_ms INTEGER DEFAULT 5000,
    memory_limit_mb INTEGER DEFAULT 256,
    points INTEGER DEFAULT 0,
    is_visible INTEGER DEFAULT 1 CHECK(is_visible IN (0,1)),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE
);