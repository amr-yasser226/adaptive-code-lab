import os
import sqlite3
from dotenv import load_dotenv

# Load .env
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Read DB path from .env
DB_PATH = os.getenv("ACCL_DB_PATH")
if not DB_PATH:
    DB_PATH = os.path.join(PROJECT_ROOT, "DB", "Accl_DB.db")
else:
    # make path absolute if relative
    if not os.path.isabs(DB_PATH):
        DB_PATH = os.path.join(PROJECT_ROOT, DB_PATH)

def connect_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn