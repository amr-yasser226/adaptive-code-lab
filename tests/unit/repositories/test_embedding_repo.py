import pytest
import sqlite3
from unittest.mock import Mock
from core.entities.embedding import Embedding


@pytest.mark.repo
@pytest.mark.unit
class TestEmbeddingRepo:
    """Test suite for EmbeddingRepository"""
    
    def test_save_embedding(self, sample_submission, embedding_repo):
        """Test saving a new embedding"""
        embedding = Embedding(
            id=None,
            submission_id=sample_submission.get_id(),
            vector_ref="vectors/embedding_1.npy",
            model_version="text-embedding-004",
            dimensions=768,
            created_at=None
        )
        
        saved = embedding_repo.save_embedding(embedding)
        
        assert saved is not None
        assert saved.get_id() is not None
        assert saved.dimensions == 768
    
    def test_get_by_id_returns_embedding(self, sample_submission, embedding_repo):
        """Test retrieving embedding by ID"""
        embedding = Embedding(
            id=None,
            submission_id=sample_submission.get_id(),
            vector_ref="vectors/embedding_2.npy",
            model_version="text-embedding-004",
            dimensions=512,
            created_at=None
        )
        saved = embedding_repo.save_embedding(embedding)
        
        retrieved = embedding_repo.get_by_id(saved.get_id())
        
        assert retrieved is not None
        assert retrieved.dimensions == 512

    def test_get_by_id_not_found(self, embedding_repo):
        """Line 21: get_by_id returns None for non-existent ID"""
        assert embedding_repo.get_by_id(9999) is None
    
    def test_find_by_submission(self, sample_submission, embedding_repo):
        """Test finding embedding by submission"""
        embedding = Embedding(
            id=None,
            submission_id=sample_submission.get_id(),
            vector_ref="vectors/embedding_3.npy",
            model_version="text-embedding-004",
            dimensions=1024,
            created_at=None
        )
        embedding_repo.save_embedding(embedding)
        
        retrieved = embedding_repo.find_by_submission(sample_submission.get_id())
        
        assert retrieved is not None
        assert retrieved.get_submission_id() == sample_submission.get_id()

    def test_find_by_submission_not_found(self, embedding_repo):
        """Line 68: find_by_submission returns None for non-existent submission"""
        assert embedding_repo.find_by_submission(9999) is None

    def test_save_embedding_error(self, embedding_repo, sample_submission):
        """Line 50-53: save_embedding handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        embedding_repo.db = mock_db
        embedding = Embedding(None, sample_submission.get_id(), "ref", "v", 768, None)
        assert embedding_repo.save_embedding(embedding) is None
        mock_db.rollback.assert_called_once()
