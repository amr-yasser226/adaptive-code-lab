from DB.connection import connect_db
conn=connect_db()
c=conn.cursor()
c.execute('''CREATE TABLE admins (
    id INTEGER PRIMARY KEY,
    privileges TEXT, 
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);
''')
conn.commit()
conn.close()

