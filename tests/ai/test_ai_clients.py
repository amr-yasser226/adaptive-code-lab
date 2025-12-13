import pytest
import os
from unittest.mock import Mock, patch, MagicMock


class TestGeminiClient:
    """Tests for GeminiClient embedding generation."""

    def test_init_with_api_key(self):
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            with patch("infrastructure.ai.gemini_client.genai") as mock_genai:
                from infrastructure.ai.gemini_client import GeminiClient
                client = GeminiClient(api_key="test-key")
                assert client.api_key == "test-key"
                mock_genai.configure.assert_called_once_with(api_key="test-key")
    
    def test_init_from_env(self):
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "env-key"}):
            with patch("infrastructure.ai.gemini_client.genai") as mock_genai:
                from infrastructure.ai.gemini_client import GeminiClient
                client = GeminiClient()
                assert client.api_key == "env-key"
    
    def test_init_raises_without_key(self):
        with patch.dict(os.environ, {"GOOGLE_API_KEY": ""}, clear=True):
            with patch("infrastructure.ai.gemini_client.genai"):
                from infrastructure.ai.gemini_client import GeminiClient
                with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
                    GeminiClient(api_key=None)
    
    def test_generate_embedding_success(self):
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            with patch("infrastructure.ai.gemini_client.genai") as mock_genai:
                mock_genai.embed_content.return_value = {
                    'embedding': [0.1, 0.2, 0.3, 0.4, 0.5]
                }
                
                from infrastructure.ai.gemini_client import GeminiClient
                client = GeminiClient(api_key="test-key")
                
                result = client.generate_embedding("def hello(): pass")
                
                assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
                mock_genai.embed_content.assert_called_once()
    
    def test_generate_embedding_api_error(self):
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            with patch("infrastructure.ai.gemini_client.genai") as mock_genai:
                mock_genai.embed_content.side_effect = Exception("API Error")
                
                from infrastructure.ai.gemini_client import GeminiClient
                client = GeminiClient(api_key="test-key")
                
                with pytest.raises(RuntimeError, match="Gemini embedding API error"):
                    client.generate_embedding("test code")
    
    def test_get_model_name(self):
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            with patch("infrastructure.ai.gemini_client.genai"):
                from infrastructure.ai.gemini_client import GeminiClient
                client = GeminiClient(api_key="test-key", model="custom-model")
                assert client.get_model_name() == "custom-model"


class TestGroqClient:
    """Tests for GroqClient LLM operations."""
    
    def test_init_with_api_key(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-groq-key"}):
            with patch("infrastructure.ai.groq_client.Groq") as mock_groq:
                with patch("infrastructure.ai.groq_client.GROQ_AVAILABLE", True):
                    from infrastructure.ai.groq_client import GroqClient
                    client = GroqClient(api_key="test-groq-key")
                    assert client.api_key == "test-groq-key"
    
    def test_init_raises_without_key(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}, clear=True):
            with patch("infrastructure.ai.groq_client.Groq"):
                with patch("infrastructure.ai.groq_client.GROQ_AVAILABLE", True):
                    from infrastructure.ai.groq_client import GroqClient
                    with pytest.raises(ValueError, match="GROQ_API_KEY"):
                        GroqClient(api_key=None)
    
    def test_chat_success(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch("infrastructure.ai.groq_client.Groq") as mock_groq_class:
                with patch("infrastructure.ai.groq_client.GROQ_AVAILABLE", True):
                    # Setup mock response
                    mock_client = MagicMock()
                    mock_response = MagicMock()
                    mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
                    mock_client.chat.completions.create.return_value = mock_response
                    mock_groq_class.return_value = mock_client
                    
                    from infrastructure.ai.groq_client import GroqClient
                    client = GroqClient(api_key="test-key")
                    
                    result = client.chat([{"role": "user", "content": "Hi"}])
                    
                    assert result == "Hello!"
    
    def test_generate_hint(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch("infrastructure.ai.groq_client.Groq") as mock_groq_class:
                with patch("infrastructure.ai.groq_client.GROQ_AVAILABLE", True):
                    mock_client = MagicMock()
                    mock_response = MagicMock()
                    mock_response.choices = [MagicMock(message=MagicMock(content="Try checking your loop"))]
                    mock_client.chat.completions.create.return_value = mock_response
                    mock_groq_class.return_value = mock_client
                    
                    from infrastructure.ai.groq_client import GroqClient
                    client = GroqClient(api_key="test-key")
                    
                    hint = client.generate_hint("for i in range(10):", "IndexError")
                    
                    assert "loop" in hint


class TestEmbeddingServiceIntegration:
    """Integration tests for EmbeddingService with mocked client."""
    
    def test_service_with_mocked_client(self):
        from core.services.embedding_service import EmbeddingService
        from core.entities.embedding import Embedding
        
        # Mock client
        mock_client = Mock()
        mock_client.generate_embedding.return_value = [0.1, 0.2, 0.3]
        mock_client.get_model_name.return_value = "test-model"
        
        # Mock repo
        mock_repo = Mock()
        mock_repo.find_by_submission.return_value = None
        mock_repo.save_embedding.return_value = Embedding(
            id=1, submission_id=1, vector_ref=b"", 
            model_version="test", dimensions=3, created_at=None
        )
        
        service = EmbeddingService(embedding_repo=mock_repo, embedding_client=mock_client)
        
        # Call generate
        result = service.generate_and_store_embedding(1, "def test(): pass")
        
        assert result == [0.1, 0.2, 0.3]
        mock_client.generate_embedding.assert_called_once_with("def test(): pass")
        mock_repo.save_embedding.assert_called_once()
