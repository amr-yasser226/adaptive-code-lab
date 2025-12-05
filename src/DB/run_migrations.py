import sqlite3
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
DB_PATH = os.path.join(PROJECT_ROOT, "DB", "Accl_DB.db")
TABLES_DIR = os.path.join(PROJECT_ROOT, "DB", "Tables")

print(f"Using DB: {DB_PATH}")
print(f"Loading SQL files from: {TABLES_DIR}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

sql_files = [f for f in os.listdir(TABLES_DIR) if f.endswith(".sql")]
print(f"Found {len(sql_files)} SQL files: {sql_files}")

for sql_file in sql_files:
    file_path = os.path.join(TABLES_DIR, sql_file)
    print(f"Executing {sql_file}...")
    with open(file_path, "r") as f:
        sql = f.read()
        try:
            cursor.executescript(sql)
            print(f"✔ Successfully executed {sql_file}")
        except sqlite3.Error as e:
            print(f"❌ Error executing {sql_file}: {e}")

conn.commit()

# List all tables in DB
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"\nTables currently in DB ({len(tables)}):")
for t in tables:
    print(f" - {t[0]}")

conn.close()
print("\n✅ All migrations finished!")