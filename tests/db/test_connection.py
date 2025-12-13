import sqlite3
import tempfile
import pytest
from infrastructure.database.connection import connect_db

@pytest.fixture
def temp_db_path():
    """Create a temporary DB file and return its path."""
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp_db:
        yield tmp_db.name  # yield path to use in tests

def test_connect_db(temp_db_path, monkeypatch):
    # Monkeypatch connect_db to use temporary DB
    monkeypatch.setattr("DB.connection.connect_db", lambda db_path=temp_db_path: sqlite3.connect(db_path))

    conn = connect_db()
    assert isinstance(conn, sqlite3.Connection)

    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys;")
    fk_enabled = cursor.fetchone()[0]
    assert fk_enabled == 1

    conn.close()
