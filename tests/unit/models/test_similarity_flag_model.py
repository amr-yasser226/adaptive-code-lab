import pytest
from datetime import datetime
from core.entities.similarity_flag import SimilarityFlag


class TestSimilarityFlag:
    """Test suite for SimilarityFlag entity"""

    def test_init(self):
        """Test SimilarityFlag initialization"""
        now = datetime.now()
        flag = SimilarityFlag(
            id=1,
            submission_id=10,
            similarity_score=0.92,
            highlighted_spans=None,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=now
        )

        assert flag.get_id() == 1
        assert flag.get_submission_id() == 10
        assert flag.similarity_score == 0.92
        assert flag.is_reviewed is False

    def test_get_id(self):
        """Test get_id getter"""
        flag = SimilarityFlag(
            id=42, submission_id=1, similarity_score=0.5,
            highlighted_spans=None, is_reviewed=False,
            reviewd_by=None, review_notes=None,
            reviewed_at=None, created_at=datetime.now()
        )
        assert flag.get_id() == 42

    def test_get_submission_id(self):
        """Test get_submission_id getter"""
        flag = SimilarityFlag(
            id=1, submission_id=99, similarity_score=0.5,
            highlighted_spans=None, is_reviewed=False,
            reviewd_by=None, review_notes=None,
            reviewed_at=None, created_at=datetime.now()
        )
        assert flag.get_submission_id() == 99

    def test_is_reviewed_converted_to_bool(self):
        """Test is_reviewed is converted to boolean"""
        flag = SimilarityFlag(
            id=1, submission_id=1, similarity_score=0.5,
            highlighted_spans=None, is_reviewed=1,
            reviewd_by=None, review_notes=None,
            reviewed_at=None, created_at=datetime.now()
        )
        assert flag.is_reviewed is True

    def test_public_attributes(self):
        """Test public attributes are accessible and modifiable"""
        now = datetime.now()
        flag = SimilarityFlag(
            id=1, submission_id=1, similarity_score=0.85,
            highlighted_spans=[{"line": 10}], is_reviewed=False,
            reviewd_by=None, review_notes=None,
            reviewed_at=None, created_at=now
        )

        assert flag.similarity_score == 0.85
        assert flag.highlighted_spans == [{"line": 10}]
        assert flag.created_at == now

    def test_reviewed_flag(self):
        """Test reviewed flag has reviewer info"""
        now = datetime.now()
        flag = SimilarityFlag(
            id=1, submission_id=1, similarity_score=0.9,
            highlighted_spans=None, is_reviewed=True,
            reviewd_by=5, review_notes="False positive",
            reviewed_at=now, created_at=now
        )

        assert flag.is_reviewed is True
        assert flag.reviewd_by == 5
        assert flag.review_notes == "False positive"
        assert flag.reviewed_at == now
