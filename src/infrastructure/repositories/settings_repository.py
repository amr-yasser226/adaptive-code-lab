import sqlite3
from datetime import datetime

class SettingsRepository:
    def __init__(self, db):
        self.db = db

    def get(self, key, default=None):
        try:
            query = "SELECT value FROM settings WHERE key = :key"
            result = self.db.execute(query, {"key": key})
            row = result.fetchone()
            return row[0] if row else default
        except sqlite3.Error:
            return default

    def set(self, key, value):
        try:
            query = """
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (:key, :value, CURRENT_TIMESTAMP)
            """
            self.db.execute(query, {"key": key, "value": value})
            self.db.commit()
            return True
        except sqlite3.Error:
            self.db.rollback()
            return False

    def list_all(self):
        try:
            query = "SELECT key, value, updated_at FROM settings"
            result = self.db.execute(query)
            return [{'key': row[0], 'value': row[1], 'updated_at': row[2]} for row in result.fetchall()]
        except sqlite3.Error:
            return []
