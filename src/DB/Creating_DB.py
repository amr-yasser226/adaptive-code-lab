import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "Accl_DB.db")

def create_database():
    conn = sqlite3.connect(DB_PATH)
    conn.close()

def get_tables_names():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.close()
    return tables