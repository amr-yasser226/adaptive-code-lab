import pytest
from core.entities.peer_review import PeerReview


@pytest.mark.repo
@pytest.mark.unit
class TestPeerReviewRepo:
    """Test suite for PeerReview_repo"""
    
    def test_create_peer_review(self, sample_submission, sample_student, peer_review_repo):
        """Test creating a new peer review"""
        peer_review = PeerReview(
            submission_id=sample_submission.get_id(),
            reviewer_student_id=sample_student.get_id(),
            rubric_score={"clarity": 8, "correctness": 7},
            comments="Good work overall",
            is_submitted=False,
            submitted_at=None,
            created_at=None
        )
        
        saved = peer_review_repo.create(peer_review)
        
        assert saved is not None
        assert saved.comments == "Good work overall"
    
    def test_get_peer_review(self, sample_submission, sample_student, peer_review_repo):
        """Test retrieving peer review"""
        peer_review = PeerReview(
            submission_id=sample_submission.get_id(),
            reviewer_student_id=sample_student.get_id(),
            rubric_score={"clarity": 9, "correctness": 8},
            comments="Excellent",
            is_submitted=True,
            submitted_at=None,
            created_at=None
        )
        peer_review_repo.create(peer_review)
        
        retrieved = peer_review_repo.get(
            sample_submission.get_id(),
            sample_student.get_id()
        )
        
        assert retrieved is not None
        assert retrieved.comments == "Excellent"
    
    def test_update_peer_review(self, sample_submission, sample_student, peer_review_repo):
        """Test updating peer review"""
        peer_review = PeerReview(
            submission_id=sample_submission.get_id(),
            reviewer_student_id=sample_student.get_id(),
            rubric_score={"clarity": 5, "correctness": 5},
            comments="Original",
            is_submitted=False,
            submitted_at=None,
            created_at=None
        )
        peer_review_repo.create(peer_review)
        
        peer_review.comments = "Updated review"
        peer_review.rubric_score = {"clarity": 8, "correctness": 9}
        updated = peer_review_repo.update(peer_review)
        
        assert updated.comments == "Updated review"
    
    def test_delete_peer_review(self, sample_submission, sample_student, peer_review_repo):
        """Test deleting peer review"""
        peer_review = PeerReview(
            submission_id=sample_submission.get_id(),
            reviewer_student_id=sample_student.get_id(),
            rubric_score={"clarity": 7, "correctness": 7},
            comments="To delete",
            is_submitted=False,
            submitted_at=None,
            created_at=None
        )
        peer_review_repo.create(peer_review)
        
        result = peer_review_repo.delete(
            sample_submission.get_id(),
            sample_student.get_id()
        )
        
        assert result is True
    
    def test_list_by_submission(self, sample_submission, sample_student, peer_review_repo):
        """Test listing peer reviews by submission"""
        peer_review = PeerReview(
            submission_id=sample_submission.get_id(),
            reviewer_student_id=sample_student.get_id(),
            rubric_score={"clarity": 8, "correctness": 8},
            comments="Good",
            is_submitted=True,
            submitted_at=None,
            created_at=None
        )
        peer_review_repo.create(peer_review)
        
        reviews = peer_review_repo.list_by_submission(sample_submission.get_id())
        assert len(reviews) >= 1
    
    def test_list_by_reviewer(self, sample_submission, sample_student, peer_review_repo):
        """Test listing peer reviews by reviewer"""
        peer_review = PeerReview(
            submission_id=sample_submission.get_id(),
            reviewer_student_id=sample_student.get_id(),
            rubric_score={"clarity": 7, "correctness": 8},
            comments="Nice",
            is_submitted=True,
            submitted_at=None,
            created_at=None
        )
        peer_review_repo.create(peer_review)
        
        reviews = peer_review_repo.list_by_reviewer(sample_student.get_id())
        assert len(reviews) >= 1