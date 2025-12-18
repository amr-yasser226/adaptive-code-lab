"""Cleanup old drafts based on DRAFT_RETENTION_DAYS config.
Run periodically (cron, systemd timer, or CI job).
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from infrastructure.database.connection import DatabaseManager

load_dotenv()
from config.settings import DRAFT_RETENTION_DAYS


def cleanup_old_drafts():
    dbm = DatabaseManager.get_instance()
    conn = dbm.get_connection()
    cutoff = datetime.utcnow() - timedelta(days=DRAFT_RETENTION_DAYS)
    cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
    cur = conn.cursor()
    cur.execute("DELETE FROM drafts WHERE updated_at < :cutoff", {'cutoff': cutoff_str})
    deleted = cur.rowcount
    conn.commit()
    print(f"Deleted {deleted} drafts older than {cutoff_str}")


if __name__ == '__main__':
    cleanup_old_drafts()
