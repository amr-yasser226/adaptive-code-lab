"""Helper to seed drafts for E2E tests or local debugging."""
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('ACCL_DB_PATH')
if db_url and db_url.startswith('sqlite:///'):
    path = db_url.replace('sqlite:///', '')
else:
    path = db_url

def seed(user_id, assignment_id, content='print("hello")'):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO drafts (user_id, assignment_id, content, metadata, version, created_at, updated_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)',
        (user_id, assignment_id, content, None, 1)
    )
    conn.commit()
    conn.close()

if __name__ == '__main__':
    seed(1, 1)
