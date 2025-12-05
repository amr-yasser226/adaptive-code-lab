# tests/db/test_db_env.py
import sys
import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from DB.connection import connect_db
from DB.Creating_DB import create_database
from DB.run_migrations import run_migrations

if __name__ == "__main__":
    # Quick test
    conn = connect_db()
    print("DB connection test successful!")

    create_database()
    print("Database created successfully!")

    tables = run_migrations()
    print(f"Migrations run successfully! Tables: {tables}")
