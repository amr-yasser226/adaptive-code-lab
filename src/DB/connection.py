import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "Accl_DB.db")

def connect_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn