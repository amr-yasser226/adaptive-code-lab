from DB.connection import connect_db
conn=connect_db()
c=conn.cursor()
c.execute('''CREATE TABLE hints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    submission_id INTEGER NOT NULL,
    model_used TEXT,
    confidence REAL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    hint_text TEXT NOT NULL,
    is_helpful INTEGER CHECK(is_helpful IN (0,1)),
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
);



''')
conn.commit()
conn.close()
