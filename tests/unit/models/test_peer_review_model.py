import pytest
from datetime import datetime
from core.entities.peer_review import PeerReview


class TestPeerReview:
    """Test suite for PeerReview entity"""

    def test_init(self):
        """Test PeerReview initialization"""
        now = datetime.now()
        review = PeerReview(
            submission_id=1,
            reviewer_student_id=5,
            rubric_score={"quality": 4, "style": 5},
            comments="Good work",
            is_submitted=False,
            submitted_at=None,
            created_at=now
        )

        assert review.get_submission_id() == 1
        assert review.get_reviewer_student_id() == 5
        assert review.rubric_score == {"quality": 4, "style": 5}
        assert review.comments == "Good work"
        assert review.is_submitted is False

    def test_get_submission_id(self):
        """Test get_submission_id getter"""
        review = PeerReview(
            submission_id=42, reviewer_student_id=1,
            rubric_score=None, comments=None,
            is_submitted=False, submitted_at=None,
            created_at=datetime.now()
        )
        assert review.get_submission_id() == 42

    def test_get_reviewer_student_id(self):
        """Test get_reviewer_student_id getter"""
        review = PeerReview(
            submission_id=1, reviewer_student_id=99,
            rubric_score=None, comments=None,
            is_submitted=False, submitted_at=None,
            created_at=datetime.now()
        )
        assert review.get_reviewer_student_id() == 99

    def test_is_submitted_converted_to_bool(self):
        """Test is_submitted is converted to boolean"""
        review = PeerReview(
            submission_id=1, reviewer_student_id=1,
            rubric_score=None, comments=None,
            is_submitted=1, submitted_at=None,
            created_at=datetime.now()
        )
        assert review.is_submitted is True

    def test_calculate_rubric_score_with_dict(self):
        """Test calculate_rubric_score with valid dict"""
        review = PeerReview(
            submission_id=1, reviewer_student_id=1,
            rubric_score={"quality": 4, "style": 5, "correctness": 3},
            comments=None, is_submitted=True,
            submitted_at=datetime.now(),
            created_at=datetime.now()
        )

        result = review.calculate_rubric_score()

        assert result == 4.0  # (4+5+3)/3

    def test_calculate_rubric_score_empty(self):
        """Test calculate_rubric_score with no score"""
        review = PeerReview(
            submission_id=1, reviewer_student_id=1,
            rubric_score=None, comments=None,
            is_submitted=False, submitted_at=None,
            created_at=datetime.now()
        )

        result = review.calculate_rubric_score()

        assert result == 0

    def test_calculate_rubric_score_empty_dict(self):
        """Test calculate_rubric_score with empty dict"""
        review = PeerReview(
            submission_id=1, reviewer_student_id=1,
            rubric_score={}, comments=None,
            is_submitted=False, submitted_at=None,
            created_at=datetime.now()
        )

        result = review.calculate_rubric_score()

        assert result == 0
