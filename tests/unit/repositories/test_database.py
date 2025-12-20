import pytest
import sqlite3
import os
from unittest.mock import patch, Mock
from sqlalchemy.exc import SQLAlchemyError
from infrastructure.repositories.database import Database

@pytest.mark.repo
@pytest.mark.unit
class TestDatabase:
    """Test suite for the Database base class in repositories"""

    def test_database_init_error(self, monkeypatch):
        """Line 14: Database raises ValueError if ACCL_DB_PATH is missing"""
        # Mock load_dotenv to do nothing so it doesn't reload from .env
        with patch('infrastructure.repositories.database.load_dotenv'):
            monkeypatch.delenv("ACCL_DB_PATH", raising=False)
            with pytest.raises(ValueError, match="ACCL_DB_PATH not found in .env"):
                Database()

    def test_connect_error(self):
        """Line 24-25: connect handles SQLAlchemyError"""
        db = Database()
        with patch('infrastructure.repositories.database.create_engine') as mock_engine:
            mock_engine.side_effect = SQLAlchemyError("Mock SQLAlchemy Error")
            with pytest.raises(SQLAlchemyError):
                db.connect()

    def test_disconnect_error(self):
        """Line 33-34: disconnect handles SQLAlchemyError"""
        db = Database()
        db.session = Mock()
        db.session.close.side_effect = SQLAlchemyError("Mock close error")
        with pytest.raises(SQLAlchemyError):
            db.disconnect()

    def test_begin_transaction_error(self):
        """Line 40-41: begin_transaction handles SQLAlchemyError"""
        db = Database()
        db.session = Mock()
        db.session.begin.side_effect = SQLAlchemyError("Mock begin error")
        with pytest.raises(SQLAlchemyError):
            db.begin_transaction()

    def test_commit_error(self):
        """Line 46-48: commit handles SQLAlchemyError and rolls back"""
        db = Database()
        db.session = Mock()
        db.session.commit.side_effect = SQLAlchemyError("Mock commit error")
        with pytest.raises(SQLAlchemyError):
            db.commit()
        db.session.rollback.assert_called_once()

    def test_rollback_error(self):
        """Line 53-54: rollback handles SQLAlchemyError"""
        db = Database()
        db.session = Mock()
        db.session.rollback.side_effect = SQLAlchemyError("Mock rollback error")
        with pytest.raises(SQLAlchemyError):
            db.rollback()

    def test_execute_with_params(self, clean_db):
        """Test execute with parameters"""
        result = clean_db.execute("SELECT 1 as val WHERE 1 = :one", {"one": 1})
        row = result.fetchone()
        assert row[0] == 1

    def test_execute_error(self):
        """Line 63-64: execute handles SQLAlchemyError"""
        db = Database()
        db.session = Mock()
        db.session.execute.side_effect = SQLAlchemyError("Mock execute error")
        with pytest.raises(SQLAlchemyError):
            db.execute("SELECT 1")

    def test_handle_error_sqlite(self):
        """Line 68-69: _handle_error unwraps sqlite3.Error"""
        db = Database()
        mock_error = SQLAlchemyError("Wrapper")
        mock_error.orig = sqlite3.Error("Original SQLite Error")
        with pytest.raises(sqlite3.Error, match="Original SQLite Error"):
            db._handle_error(mock_error)

    def test_handle_error_other(self):
        """Line 70: _handle_error re-raises other SQLAlchemyErrors"""
        db = Database()
        mock_error = SQLAlchemyError("Generic SQLAlchemy Error")
        with pytest.raises(SQLAlchemyError, match="Generic SQLAlchemy Error"):
            db._handle_error(mock_error)
