from DB.connection import connect_db
conn=connect_db()
c=conn.cursor()
c.execute('''CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('info', 'warning', 'alert')),
    is_read INTEGER DEFAULT 0 CHECK(is_read IN (0,1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    link TEXT, 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
''')

conn.commit()
conn.close()
