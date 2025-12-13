import sqlite3
from dotenv import load_dotenv
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
dotenv_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(dotenv_path)

DB_PATH = os.getenv("ACCL_DB_PATH", "data/Accl_DB.db")
if DB_PATH.startswith("sqlite:///"):
    DB_PATH = DB_PATH.replace("sqlite:///", "")

if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, DB_PATH)

print("Using DB:", DB_PATH)    # debug

import threading

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path=None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._init_connection(db_path)
        return cls._instance

    def _init_connection(self, db_path):
        self.db_path = db_path if db_path else DB_PATH
        print(f"DatabaseManager initialized with: {self.db_path}")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
             # Default initialization if not already created
             cls(DB_PATH)
        return cls._instance

    def get_connection(self):
        """Returns a NEW connection object. SQLite connections cannot be shared across threads."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

# Backward compatibility helper
def connect_db(db_path=None):
    if db_path:
        # If a specific path is requested, we might need a separate instance or just use a direct connect 
        # for flexibility (e.g. testing different DBs). 
        # But for main app, we use the singleton Manager.
        return sqlite3.connect(db_path, check_same_thread=False)
    
    # Use the Singleton for the default path
    return DatabaseManager.get_instance().get_connection()