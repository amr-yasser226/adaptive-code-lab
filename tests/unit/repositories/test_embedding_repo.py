import pytest
from core.entities.embedding import Embedding


@pytest.mark.repo
@pytest.mark.unit
class TestEmbeddingRepo:
    """Test suite for Embedding_repo"""
    
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
