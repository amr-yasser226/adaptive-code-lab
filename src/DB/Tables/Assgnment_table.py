from DB.connection import connect_db
conn=connect_db()
c=conn.cursor()
c.execute('''CREATE TABLE assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    release_date DATETIME,
    due_date DATETIME NOT NULL,
    max_points INTEGER DEFAULT 100,
    is_published INTEGER DEFAULT 0 CHECK(is_published IN (0,1)),
    allow_late_submissions INTEGER DEFAULT 0 CHECK(allow_late_submissions IN (0,1)),
    late_submission_penalty REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

''')

conn.commit()
conn.close()
