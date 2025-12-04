from DB.connection import connect_db
conn=connect_db()
c=conn.cursor()
c.execute('''CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    instructor_id INTEGER NOT NULL,
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    year INTEGER NOT NULL, 
    semester TEXT NOT NULL, 
    max_students INTEGER , 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT check(status IN ('active', 'inactive','draft')) DEFAULT 'active',
    updated_at TIMESTAMP,
    credits INTEGER NOT NULL,  
    FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE SET NULL
);
''')

conn.commit()
conn.close()
