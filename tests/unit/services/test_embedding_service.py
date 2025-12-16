import pytest
from unittest.mock import Mock, patch
from core.services.embedding_service import EmbeddingService
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_embedding_repo():
    return Mock()


@pytest.fixture
def mock_embedding_client():
    client = Mock()
    client.generate_embedding.return_value = [0.1, 0.2, 0.3]
    client.get_model_name.return_value = "text-embedding-004"
    return client


@pytest.fixture
def embedding_service(mock_embedding_repo, mock_embedding_client):
    return EmbeddingService(mock_embedding_repo, mock_embedding_client)


@pytest.fixture
def embedding_service_no_client(mock_embedding_repo):
    return EmbeddingService(mock_embedding_repo, None)


class TestEmbeddingService:
    """Test suite for EmbeddingService"""

    def test_get_embedding_vector_found(self, embedding_service, mock_embedding_repo):
        """Test getting embedding vector when it exists"""
        import pickle
        vector = [0.1, 0.2, 0.3]
        emb = Mock()
        emb.vector_ref = pickle.dumps(vector)
        mock_embedding_repo.find_by_submission.return_value = emb

        result = embedding_service.get_embedding_vector(1)

        assert result == vector

    def test_get_embedding_vector_not_found(self, embedding_service, mock_embedding_repo):
        """Test getting embedding vector when it doesn't exist"""
        mock_embedding_repo.find_by_submission.return_value = None

        result = embedding_service.get_embedding_vector(1)

        assert result is None

    def test_get_embedding_vector_empty_ref(self, embedding_service, mock_embedding_repo):
        """Test getting embedding vector with empty vector_ref"""
        emb = Mock()
        emb.vector_ref = None
        mock_embedding_repo.find_by_submission.return_value = emb

        result = embedding_service.get_embedding_vector(1)

        assert result is None

    def test_generate_and_store_embedding_success(self, embedding_service, mock_embedding_repo, mock_embedding_client):
        """Test generating and storing embedding successfully"""
        mock_embedding_repo.save_embedding.return_value = Mock()

        result = embedding_service.generate_and_store_embedding(1, "def foo(): pass")

        assert result == [0.1, 0.2, 0.3]
        mock_embedding_client.generate_embedding.assert_called_once_with("def foo(): pass")
        mock_embedding_repo.save_embedding.assert_called_once()

    def test_generate_and_store_embedding_no_client(self, embedding_service_no_client):
        """Test generating embedding without client raises error"""
        with pytest.raises(ValidationError, match="Embedding client not configured"):
            embedding_service_no_client.generate_and_store_embedding(1, "def foo(): pass")

    def test_generate_and_store_embedding_empty_code(self, embedding_service):
        """Test generating embedding with empty code raises error"""
        with pytest.raises(ValidationError, match="Code text cannot be empty"):
            embedding_service.generate_and_store_embedding(1, "")

    def test_generate_and_store_embedding_client_error(self, embedding_service, mock_embedding_client):
        """Test handling client error during embedding generation"""
        mock_embedding_client.generate_embedding.side_effect = Exception("API Error")

        with pytest.raises(ValidationError, match="Embedding generation failed"):
            embedding_service.generate_and_store_embedding(1, "def foo(): pass")

    def test_generate_and_store_embedding_save_fails(self, embedding_service, mock_embedding_repo):
        """Test handling save failure"""
        mock_embedding_repo.save_embedding.return_value = None

        with pytest.raises(ValidationError, match="Failed to save embedding"):
            embedding_service.generate_and_store_embedding(1, "def foo(): pass")

    def test_ensure_embedding_existing(self, embedding_service, mock_embedding_repo):
        """Test ensure_embedding returns existing embedding"""
        import pickle
        vector = [0.1, 0.2, 0.3]
        emb = Mock()
        emb.vector_ref = pickle.dumps(vector)
        mock_embedding_repo.find_by_submission.return_value = emb

        result = embedding_service.ensure_embedding(1)

        assert result == vector

    def test_ensure_embedding_generates_new(self, embedding_service, mock_embedding_repo):
        """Test ensure_embedding generates new when not found"""
        mock_embedding_repo.find_by_submission.return_value = None
        mock_embedding_repo.save_embedding.return_value = Mock()

        result = embedding_service.ensure_embedding(1, "def foo(): pass")

        assert result == [0.1, 0.2, 0.3]

    def test_ensure_embedding_no_code_no_existing(self, embedding_service, mock_embedding_repo):
        """Test ensure_embedding raises error when no code and no existing embedding"""
        mock_embedding_repo.find_by_submission.return_value = None

        with pytest.raises(ValidationError, match="Embedding not found and no code_text provided"):
            embedding_service.ensure_embedding(1)
