import sqlite3
from dotenv import load_dotenv
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
dotenv_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(dotenv_path)

def get_db_path():
    path = os.getenv("ACCL_DB_PATH", "data/Accl_DB.db")
    if path.startswith("sqlite:///"):
        path = path.replace("sqlite:///", "")
    if not os.path.isabs(path):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        path = os.path.join(project_root, path)
    return path

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
        self.db_path = db_path if db_path else get_db_path()
        # DatabaseManager initialized

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
             # Default initialization if not already created
             cls(get_db_path())
        return cls._instance

    @classmethod
    def _reset_instance(cls):
        """Internal helper to reset singleton for testing purposes"""
        cls._instance = None

    def get_connection(self):
        """Returns a NEW connection object. SQLite connections cannot be shared across threads."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = self._custom_row_factory
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _custom_row_factory(self, cursor, row):
        return CustomRow(cursor, row)

class CustomRow:
    """Row wrapper that supports index (row[0]), key (row['id']), and attribute (row.id) access."""
    def __init__(self, cursor, row):
        self._data = row
        self._keys = {col[0]: i for i, col in enumerate(cursor.description)}
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._data[key]
        if key in self._keys:
            return self._data[self._keys[key]]
        raise IndexError(f"Key/Index '{key}' not found in row")

    def __getattr__(self, name):
        try:
            return self[name]
        except IndexError:
            raise AttributeError(f"Row has no attribute '{name}'")

# Backward compatibility helper
def connect_db(db_path=None):
    if db_path:
        # If a specific path is requested, we might need a separate instance or just use a direct connect 
        # for flexibility (e.g. testing different DBs). 
        # But for main app, we use the singleton Manager.
        return sqlite3.connect(db_path, check_same_thread=False)
    
    # Use the Singleton for the default path
    return DatabaseManager.get_instance().get_connection()