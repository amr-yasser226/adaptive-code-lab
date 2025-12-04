from ..connection import connect_db
conn=connect_db()
c=conn.cursor()
c.execute('''CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    student_number TEXT NOT NULL UNIQUE,
    program TEXT NOT NULL, 
    YearLevel INTEGER NOT NULL, 
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);
''')

conn.commit()
conn.close()

