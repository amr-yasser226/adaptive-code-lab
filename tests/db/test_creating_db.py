import sqlite3
import tempfile
import pytest
from infrastructure.database import create_db

@pytest.fixture
def temp_db_path():
    """Create a temporary DB file and return its path."""
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp_db:
        yield tmp_db.name

def test_create_and_list_tables(temp_db_path, monkeypatch):
    # Monkeypatch the DB_PATH in create_db
    monkeypatch.setattr("infrastructure.database.create_db.DB_PATH", temp_db_path)

    # Create DB
    create_db.create_database()

    # Connect and create a test table
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test_table(id INTEGER PRIMARY KEY);")
    conn.commit()
    conn.close()

    # Check that the table exists
    tables = create_db.get_tables_names()
    assert ("test_table",) in tables
