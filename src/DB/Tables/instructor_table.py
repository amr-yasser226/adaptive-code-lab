from ..connection import connect_db
conn=connect_db()
c=conn.cursor()
c.execute('''CREATE TABLE instructors (
    id INTEGER PRIMARY KEY,
    instructor_code TEXT UNIQUE,
    bio TEXT,
    office_hours TEXT, 
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);
''')
conn.commit()
conn.close()