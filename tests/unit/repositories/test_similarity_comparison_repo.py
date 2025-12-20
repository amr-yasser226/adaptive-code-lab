import pytest
import sqlite3
import json
from unittest.mock import Mock
from core.entities.similarity_comparison import SimilarityComparison
from core.entities.similarity_flag import SimilarityFlag
from core.entities.submission import Submission


@pytest.mark.repo
@pytest.mark.unit
class TestSimilarityComparisonRepo:
    """Test suite for SimilarityComparisonRepository"""
    
    def test_create_similarity_comparison(self, sample_submission, similarity_flag_repo, 
                                          similarity_comparison_repo, sample_student,
                                          sample_assignment, submission_repo):
        """Test creating a new similarity comparison"""
        # Create flag first
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
        saved_flag = similarity_flag_repo.create(flag)
        
        # Create another submission to compare
        submission2 = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=2,
            language="python",
            status="pending",
            score=0.0,
            is_late=False,
            created_at=None,
            updated_at=None,
            grade_at=None
        )
        saved_submission2 = submission_repo.create(submission2)
        
        comparison = SimilarityComparison(
            similarity_id=saved_flag.get_id(),
            compared_submission_id=saved_submission2.get_id(),
            match_score=0.88,
            note="High similarity detected",
            match_segments={"segments": [[0, 50], [100, 150]]}
        )
        
        saved = similarity_comparison_repo.create(comparison)
        
        assert saved is not None
        assert saved.match_score == 0.88
        assert saved.match_segments == {"segments": [[0, 50], [100, 150]]}
    
    def test_get_similarity_comparison(self, sample_submission, similarity_flag_repo,
                                       similarity_comparison_repo, sample_student,
                                       sample_assignment, submission_repo):
        """Test retrieving similarity comparison"""
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
        saved_flag = similarity_flag_repo.create(flag)
        
        submission2 = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=3,
            language="python",
            status="pending",
            score=0.0,
            is_late=False,
            created_at=None,
            updated_at=None,
            grade_at=None
        )
        saved_submission2 = submission_repo.create(submission2)
        
        comparison = SimilarityComparison(
            similarity_id=saved_flag.get_id(),
            compared_submission_id=saved_submission2.get_id(),
            match_score=0.85,
            note="Moderate similarity",
            match_segments=None
        )
        similarity_comparison_repo.create(comparison)
        
        retrieved = similarity_comparison_repo.get(
            saved_flag.get_id(),
            saved_submission2.get_id()
        )
        
        assert retrieved is not None
        assert retrieved.note == "Moderate similarity"

    def test_get_not_found(self, similarity_comparison_repo):
        """Line 20: get returns None for non-existent comparison"""
        assert similarity_comparison_repo.get(999, 999) is None
    
    def test_update_similarity_comparison(self, sample_submission, similarity_flag_repo,
                                          similarity_comparison_repo, sample_student,
                                          sample_assignment, submission_repo):
        """Test updating similarity comparison"""
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
        saved_flag = similarity_flag_repo.create(flag)
        
        submission2 = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=4,
            language="python",
            status="pending",
            score=0.0,
            is_late=False,
            created_at=None,
            updated_at=None,
            grade_at=None
        )
        saved_submission2 = submission_repo.create(submission2)
        
        comparison = SimilarityComparison(
            similarity_id=saved_flag.get_id(),
            compared_submission_id=saved_submission2.get_id(),
            match_score=0.80,
            note="Original note",
            match_segments=None
        )
        similarity_comparison_repo.create(comparison)
        
        comparison.note = "Updated note"
        comparison.match_score = 0.82
        updated = similarity_comparison_repo.update(comparison)
        
        assert updated.note == "Updated note"
        assert updated.match_score == 0.82
    
    def test_delete_similarity_comparison(self, sample_submission, similarity_flag_repo,
                                          similarity_comparison_repo, sample_student,
                                          sample_assignment, submission_repo):
        """Test deleting similarity comparison"""
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
        saved_flag = similarity_flag_repo.create(flag)
        
        submission2 = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=5,
            language="python",
            status="pending",
            score=0.0,
            is_late=False,
            created_at=None,
            updated_at=None,
            grade_at=None
        )
        saved_submission2 = submission_repo.create(submission2)
        
        comparison = SimilarityComparison(
            similarity_id=saved_flag.get_id(),
            compared_submission_id=saved_submission2.get_id(),
            match_score=0.75,
            note="To delete",
            match_segments=None
        )
        similarity_comparison_repo.create(comparison)
        
        result = similarity_comparison_repo.delete(
            saved_flag.get_id(),
            saved_submission2.get_id()
        )
        
        assert result is True
        assert similarity_comparison_repo.get(saved_flag.get_id(), saved_submission2.get_id()) is None

    def test_create_error(self, similarity_comparison_repo):
        """Line 51-53: create handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        similarity_comparison_repo.db = mock_db
        comp = SimilarityComparison(1, 1, 0.5, "N", None)
        assert similarity_comparison_repo.create(comp) is None
        mock_db.rollback.assert_called_once()

    def test_update_error(self, similarity_comparison_repo):
        """Line 75-77: update handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        similarity_comparison_repo.db = mock_db
        comp = SimilarityComparison(1, 1, 0.5, "N", None)
        assert similarity_comparison_repo.update(comp) is None
        mock_db.rollback.assert_called_once()

    def test_delete_error(self, similarity_comparison_repo):
        """Line 87-89: delete handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        similarity_comparison_repo.db = mock_db
        assert similarity_comparison_repo.delete(1, 1) is False
        mock_db.rollback.assert_called_once()
    
    def test_list_by_similarity(self, sample_submission, similarity_flag_repo,
                                similarity_comparison_repo, sample_student,
                                sample_assignment, submission_repo):
        """Test listing comparisons by similarity flag"""
        flag = SimilarityFlag(
            id=None,
            submission_id=sample_submission.get_id(),
            similarity_score=0.90,
            highlighted_spans=None,
            is_reviewed=False,
            reviewd_by=None,
            review_notes=None,
            reviewed_at=None,
            created_at=None
        )
        saved_flag = similarity_flag_repo.create(flag)
        
        # Create multiple comparisons
        for i in range(2):
            submission_i = Submission(
                id=None,
                assignment_id=sample_assignment.get_id(),
                student_id=sample_student.get_id(),
                version=10+i,
                language="python",
                status="pending",
                score=0.0,
                is_late=False,
                created_at=None,
                updated_at=None,
                grade_at=None
            )
            saved_sub = submission_repo.create(submission_i)
            
            comparison = SimilarityComparison(
                similarity_id=saved_flag.get_id(),
                compared_submission_id=saved_sub.get_id(),
                match_score=0.85 + i*0.02,
                note=f"Comparison {i}",
                match_segments=None
            )
            similarity_comparison_repo.create(comparison)
        
        comparisons = similarity_comparison_repo.list_by_similarity(saved_flag.get_id())
        assert len(comparisons) >= 2