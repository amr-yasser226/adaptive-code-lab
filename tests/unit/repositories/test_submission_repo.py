import pytest
from Backend.Model.Submission_model import Submission


@pytest.mark.repo
@pytest.mark.unit
class TestSubmissionRepo:
    """Test suite for Submission_repo"""
    
    def test_create_submission(self, sample_student, sample_assignment, submission_repo):
        """Test creating a new submission"""
        submission = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=1,
            language="python",
            status="pending",
            score=0.0,
            is_late=False,
            created_at=None,
            updated_at=None,
            grade_at=None
        )
        
        saved = submission_repo.create(submission)
        
        assert saved is not None
        assert saved.get_id() is not None
        assert saved.language == "python"
    
    def test_get_by_id_returns_submission(self, sample_submission, submission_repo):
        """Test retrieving submission by ID"""
        retrieved = submission_repo.get_by_id(sample_submission.get_id())
        
        assert retrieved is not None
        assert retrieved.get_id() == sample_submission.get_id()
    
    def test_update_submission(self, sample_submission, submission_repo):
        """Test updating submission"""
        sample_submission.status = "graded"
        sample_submission.score = 85.0
        
        updated = submission_repo.update(sample_submission)
        
        assert updated.status == "graded"
        assert updated.score == 85.0
    
    def test_delete_submission(self, sample_submission, submission_repo):
        """Test deleting submission"""
        submission_id = sample_submission.get_id()
        result = submission_repo.delete(submission_id)
        
        assert result is True
        retrieved = submission_repo.get_by_id(submission_id)
        assert retrieved is None
    
    def test_list_by_assignment(self, sample_assignment, sample_student, submission_repo):
        """Test listing submissions by assignment"""
        # Create multiple submissions
        for i in range(3):
            submission = Submission(
                id=None,
                assignment_id=sample_assignment.get_id(),
                student_id=sample_student.get_id(),
                version=i+1,
                language="python",
                status="pending",
                score=0.0,
                is_late=False,
                created_at=None,
                updated_at=None,
                grade_at=None
            )
            submission_repo.create(submission)
        
        submissions = submission_repo.list_by_assignment(sample_assignment.get_id())
        assert len(submissions) >= 3
    
    def test_list_by_student(self, sample_student, sample_assignment, submission_repo):
        """Test listing submissions by student"""
        # Create multiple submissions
        for i in range(2):
            submission = Submission(
                id=None,
                assignment_id=sample_assignment.get_id(),
                student_id=sample_student.get_id(),
                version=i+1,
                language="python",
                status="pending",
                score=0.0,
                is_late=False,
                created_at=None,
                updated_at=None,
                grade_at=None
            )
            submission_repo.create(submission)
        
        submissions = submission_repo.list_by_student(sample_student.get_id())
        assert len(submissions) >= 2
