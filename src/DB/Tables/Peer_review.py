from DB.connection import connect_db
conn=connect_db()
c=conn.cursor()
c.execute('''CREATE TABLE peer_reviews (
    submission_id INTEGER NOT NULL,
    reviewer_student_id INTEGER NOT NULL,
    rubric_scores TEXT NOT NULL,
    comments TEXT,
    is_submitted INTEGER DEFAULT 0 CHECK(is_submitted IN (0,1)),
    submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (submission_id, reviewer_student_id),
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_student_id) REFERENCES students(id) ON DELETE CASCADE
);

''')
conn.commit()
conn.close()
