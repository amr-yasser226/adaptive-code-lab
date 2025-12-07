import pytest
from Backend.Model.Similarity_flag import SimilarityFlag


@pytest.mark.repo
@pytest.mark.unit
class TestSimilarityFlagRepo:
    """Test suite for SimilarityFlag_repo"""
    
    def test_create_similarity_flag(self, sample_submission, similarity_flag_repo):
        """Test creating a new similarity flag"""
        flag = SimilarityFlag(
            id=None,
            submission_id=sample_submission.get_id(),
            similarity_score=0.87,
            highlighted_spans={"spans": [[0, 10], [20, 30]]},
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=None
        )
        
        saved = similarity_flag_repo.create(flag)
        
        assert saved is not None
        assert saved.get_id() is not None
        assert saved.similarity_score == 0.87
    
    def test_get_by_id_returns_flag(self, sample_submission, similarity_flag_repo):
        """Test retrieving similarity flag by ID"""
        flag = SimilarityFlag(
            id=None,
            submission_id=sample_submission.get_id(),
            similarity_score=0.92,
            highlighted_spans=None,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=None
        )
        saved = similarity_flag_repo.create(flag)
        
        retrieved = similarity_flag_repo.get_by_id(saved.get_id())
        
        assert retrieved is not None
        assert retrieved.similarity_score == 0.92
    
    def test_get_by_submission(self, sample_submission, similarity_flag_repo):
        """Test retrieving similarity flag by submission"""
        flag = SimilarityFlag(
            id=None,
            submission_id=sample_submission.get_id(),
            similarity_score=0.85,
            highlighted_spans=None,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=None
        )
        similarity_flag_repo.create(flag)
        
        retrieved = similarity_flag_repo.get_by_submission(sample_submission.get_id())
        
        assert retrieved is not None
        assert retrieved.get_submission_id() == sample_submission.get_id()
    
    def test_update_similarity_flag(self, sample_submission, similarity_flag_repo):
        """Test updating similarity flag"""
        flag = SimilarityFlag(
            id=None,
            submission_id=sample_submission.get_id(),
            similarity_score=0.80,
            highlighted_spans=None,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=None
        )
        saved = similarity_flag_repo.create(flag)
        
        saved.similarity_score = 0.90
        updated = similarity_flag_repo.update(saved)
        
        assert updated.similarity_score == 0.90
    
    def test_delete_similarity_flag(self, sample_submission, similarity_flag_repo):
        """Test deleting similarity flag"""
        flag = SimilarityFlag(
            id=None,
            submission_id=sample_submission.get_id(),
            similarity_score=0.75,
            highlighted_spans=None,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=None
        )
        saved = similarity_flag_repo.create(flag)
        
        result = similarity_flag_repo.delete(saved.get_id())
        
        assert result is True
    
    def test_list_unreviewed(self, sample_submission, similarity_flag_repo):
        """Test listing unreviewed flags"""
        flag = SimilarityFlag(
            id=None,
            submission_id=sample_submission.get_id(),
            similarity_score=0.88,
            highlighted_spans=None,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=None
        )
        similarity_flag_repo.create(flag)
        
        unreviewed = similarity_flag_repo.list_unreviewed()
        
        assert len(unreviewed) >= 1
        assert all(not f.is_reviewed for f in unreviewed)
    
    def test_mark_reviewed(self, sample_submission, sample_instructor, similarity_flag_repo):
        """Test marking flag as reviewed"""
        flag = SimilarityFlag(
            id=None,
            submission_id=sample_submission.get_id(),
            similarity_score=0.91,
            highlighted_spans=None,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=None
        )
        saved = similarity_flag_repo.create(flag)
        
        marked = similarity_flag_repo.mark_reviewed(
            saved.get_id(),
            sample_instructor.get_id(),
            "Reviewed and confirmed",
            "2024-01-15 10:00:00"
        )
        
        assert marked.is_reviewed is True
        assert marked.reviewd_by == sample_instructor.get_id()
    
    def test_dismiss_flag(self, sample_submission, sample_instructor, similarity_flag_repo):
        """Test dismissing a flag"""
        flag = SimilarityFlag(
            id=None,
            submission_id=sample_submission.get_id(),
            similarity_score=0.76,
            highlighted_spans=None,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=None
        )
        saved = similarity_flag_repo.create(flag)
        
        dismissed = similarity_flag_repo.dismiss(
            saved.get_id(),
            sample_instructor.get_id(),
            "2024-01-15 11:00:00"
        )
        
        assert dismissed.is_reviewed is True
        assert dismissed.review_notes == "Dismissed"
    
    def test_escalate_flag(self, sample_submission, sample_instructor, similarity_flag_repo):
        """Test escalating a flag"""
        flag = SimilarityFlag(
            id=None,
            submission_id=sample_submission.get_id(),
            similarity_score=0.95,
            highlighted_spans=None,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=None
        )
        saved = similarity_flag_repo.create(flag)
        
        escalated = similarity_flag_repo.escalate(
            saved.get_id(),
            sample_instructor.get_id(),
            "2024-01-15 12:00:00"
        )
        
        assert escalated.is_reviewed is True
        assert "Escalated" in escalated.review_notes