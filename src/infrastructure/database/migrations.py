import sqlite3
import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# Adjust DB path to be in /data or relative to root, ensuring consistency
DB_PATH = os.getenv("ACCL_DB_PATH", os.path.join(PROJECT_ROOT, "Accl_DB.db"))
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.join(PROJECT_ROOT, DB_PATH)

# Correct path to schema directory (src/infrastructure/database/schema)
TABLES_DIR = os.path.join(os.path.dirname(__file__), "schema")

def run_migrations(db_path=DB_PATH, tables_dir=TABLES_DIR):
    print(f"Using DB: {db_path}")
    print(f"Loading SQL files from: {tables_dir}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sql_files = sorted([f for f in os.listdir(tables_dir) if f.endswith(".sql")])
    print(f"Found {len(sql_files)} SQL files: {sql_files}")

    for sql_file in sql_files:
        file_path = os.path.join(tables_dir, sql_file)
        print(f"Executing {sql_file}...")
        with open(file_path, "r") as f:
            sql = f.read()
            try:
                cursor.executescript(sql)
                print(f"✔ Successfully executed {sql_file}")
            except sqlite3.Error as e:
                print(f"❌ Error executing {sql_file}: {e}")

    conn.commit()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]

    conn.close()
    print("\n✅ All migrations finished!")
    return tables

if __name__ == "__main__":
    run_migrations()
