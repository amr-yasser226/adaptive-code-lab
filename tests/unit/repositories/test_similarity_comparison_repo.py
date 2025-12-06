import pytest
from Backend.Model.Similarity_Comparison_model import SimilarityComparison
from Backend.Model.Similarity_flag import SimilarityFlag
from Backend.Model.Submission_model import Submission

@pytest.mark.repo
@pytest.mark.unit
class TestSimilarityComparisonRepo:
    """Test suite for SimilarityComparison_repo"""
    
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