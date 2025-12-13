import pytest
from datetime import datetime
from core.entities.embedding import Embedding


class TestEmbedding:
    """Test suite for Embedding entity"""

    def test_init(self):
        """Test Embedding initialization"""
        now = datetime.now()
        embedding = Embedding(
            id=1,
            submission_id=10,
            vector_ref=b"binary_vector_data",
            model_version="text-embedding-004",
            dimensions=768,
            created_at=now
        )

        assert embedding.get_id() == 1
        assert embedding.get_submission_id() == 10
        assert embedding.vector_ref == b"binary_vector_data"
        assert embedding.model_version == "text-embedding-004"
        assert embedding.dimensions == 768
        assert embedding.created_at == now

    def test_get_id(self):
        """Test get_id getter"""
        embedding = Embedding(
            id=42, submission_id=1, vector_ref=None,
            model_version="v1", dimensions=256,
            created_at=datetime.now()
        )
        assert embedding.get_id() == 42

    def test_get_submission_id(self):
        """Test get_submission_id getter"""
        embedding = Embedding(
            id=1, submission_id=99, vector_ref=None,
            model_version="v1", dimensions=256,
            created_at=datetime.now()
        )
        assert embedding.get_submission_id() == 99

    def test_public_attributes(self):
        """Test public attributes are accessible"""
        now = datetime.now()
        embedding = Embedding(
            id=1, submission_id=1, vector_ref=b"data",
            model_version="gpt-4", dimensions=1536,
            created_at=now
        )

        assert embedding.vector_ref == b"data"
        assert embedding.model_version == "gpt-4"
        assert embedding.dimensions == 1536
        assert embedding.created_at == now
