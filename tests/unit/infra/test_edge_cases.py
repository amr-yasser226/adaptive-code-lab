import pytest
import sqlite3
from unittest.mock import patch, Mock
from infrastructure.database.connection import DatabaseManager, connect_db
from infrastructure.ai.gemini_client import GeminiClient
from infrastructure.ai.groq_client import GroqClient

class TestDatabaseEdgeCases:
    def test_db_connection_failure(self):
        """Test handling of DB connection failure."""
        DatabaseManager._reset_instance()
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.OperationalError("Unable to open database file")
            
            # Using a custom path to avoid singleton issues if not reset properly
            db_manager = DatabaseManager(db_path="invalid_path.db")
            with pytest.raises(sqlite3.OperationalError) as excinfo:
                db_manager.get_connection()
            assert "Unable to open database file" in str(excinfo.value)

    def test_singleton_thread_safety(self):
        """Stub for thread safety test if needed, but for now just verify singleton reset works."""
        DatabaseManager._reset_instance()
        mgr1 = DatabaseManager(db_path="db1.db")
        mgr2 = DatabaseManager(db_path="db2.db")
        assert mgr1 is mgr2
        assert mgr1.db_path == "db1.db"

class TestAIProviderEdgeCases:
    @patch('google.generativeai.embed_content')
    def test_gemini_api_error(self, mock_embed):
        """Test GeminiClient handling of API errors."""
        mock_embed.side_effect = Exception("API quota exceeded")
        client = GeminiClient(api_key="fake_key")
        with pytest.raises(RuntimeError) as excinfo:
            client.generate_embedding("test text")
        assert "Gemini embedding API error" in str(excinfo.value)
        assert "API quota exceeded" in str(excinfo.value)

    @patch('infrastructure.ai.groq_client.GROQ_AVAILABLE', True)
    @patch('infrastructure.ai.groq_client.Groq')
    def test_groq_api_error(self, mock_groq_class):
        """Test GroqClient handling of API errors."""
        mock_instance = Mock()
        mock_groq_class.return_value = mock_instance
        mock_instance.chat.completions.create.side_effect = Exception("Service unavailable")
        
        client = GroqClient(api_key="fake_key")
        with pytest.raises(RuntimeError) as excinfo:
            client.chat([{"role": "user", "content": "hi"}])
        assert "Groq API error" in str(excinfo.value)
        assert "Service unavailable" in str(excinfo.value)

    def test_groq_missing_package(self):
        """Test GroqClient behavior when groq package is missing."""
        with patch('infrastructure.ai.groq_client.GROQ_AVAILABLE', False):
            with pytest.raises(ImportError) as excinfo:
                GroqClient(api_key="fake_key")
            assert "groq package not installed" in str(excinfo.value)
