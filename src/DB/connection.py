import sqlite3
def connect_db(db_path='/home/omar-hazem/projects/SWE Project/src/DB/Accl_DB.db'):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    return conn
