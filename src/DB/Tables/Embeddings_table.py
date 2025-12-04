from DB.connection import connect_db
conn=connect_db()
c=conn.cursor()
c.execute('''CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY,
    vector_ref TEXT NOT NULL,
    model_version TEXT,
    dimension INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
    FOREIGN KEY (id) REFERENCES submissions(id) ON DELETE CASCADE
);

''')
conn.commit()
conn.close()
