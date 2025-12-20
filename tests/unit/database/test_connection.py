import pytest
import sqlite3
import os
from infrastructure.database.connection import DatabaseManager, connect_db, CustomRow, get_db_path

@pytest.mark.unit
class TestConnection:
    """Test suite for database connection and manager"""

    def test_get_db_path_uri(self, monkeypatch):
        """Test get_db_path with sqlite:/// prefix"""
        monkeypatch.setenv("ACCL_DB_PATH", "sqlite:///test.db")
        path = get_db_path()
        assert "test.db" in path
        assert "sqlite:///" not in path

    def test_database_manager_singleton(self):
        """Test that DatabaseManager is a singleton"""
        DatabaseManager._reset_instance()
        m1 = DatabaseManager("db1.db")
        m2 = DatabaseManager("db2.db")
        assert m1 is m2
        assert m1.db_path == "db1.db"

    def test_get_instance(self, monkeypatch):
         """Test get_instance creates instance if not exists"""
         DatabaseManager._reset_instance()
         monkeypatch.setenv("ACCL_DB_PATH", "test_path.db")
         inst = DatabaseManager.get_instance()
         assert inst.db_path.endswith("test_path.db")

    def test_get_connection_hit_row_factory(self, test_db_path):
        """Line 56: Test that get_connection uses custom_row_factory"""
        DatabaseManager._reset_instance()
        manager = DatabaseManager(test_db_path)
        conn = manager.get_connection()
        
        conn.execute("CREATE TABLE test_factory (val INTEGER)")
        conn.execute("INSERT INTO test_factory VALUES (1)")
        row = conn.execute("SELECT * FROM test_factory").fetchone()
        
        assert isinstance(row, CustomRow)
        assert row.val == 1
        conn.close()

    def test_custom_row_access(self, test_db_path):
        """Test CustomRow index, key, and attribute access"""
        conn = sqlite3.connect(test_db_path)
        conn.execute("CREATE TABLE test_row (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO test_row VALUES (1, 'Test')")
        
        cursor = conn.execute("SELECT id, name FROM test_row")
        row_data = cursor.fetchone()
        
        row = CustomRow(cursor, row_data)
        
        # Index access
        assert row[0] == 1
        assert row[1] == 'Test'
        
        # Key access
        assert row['id'] == 1
        assert row['name'] == 'Test'
        
        # Attribute access
        assert row.id == 1
        assert row.name == 'Test'
        
        # Non-existent
        with pytest.raises(IndexError):
            _ = row[99]
        with pytest.raises(IndexError):
            _ = row['missing']
        with pytest.raises(AttributeError):
            _ = row.missing
            
        conn.close()

    def test_connect_db_helper(self, test_db_path):
        """Test connect_db helper with and without path"""
        # With path
        conn = connect_db(test_db_path)
        assert isinstance(conn, sqlite3.Connection)
        conn.close()
        
        # Without path (uses singleton)
        DatabaseManager._reset_instance()
        DatabaseManager(test_db_path)
        conn2 = connect_db()
        assert isinstance(conn2, sqlite3.Connection)
        conn2.close()
