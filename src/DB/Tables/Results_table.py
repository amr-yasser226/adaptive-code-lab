from DB.connection import connect_db
conn=connect_db()
c=conn.cursor()
c.execute('''CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    test_case_id INTEGER NOT NULL,
    passed INTEGER NOT NULL CHECK(passed IN (0,1)),
    stdout TEXT,
    stderr TEXT,
    runtime_ms INTEGER,
    memory_kb INTEGER,
    exit_code INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE
);

    

''')
conn.commit()
conn.close()
