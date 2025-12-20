import pytest
from core.entities.submission import Submission


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

    def test_get_last_submission(self, sample_student, sample_assignment, submission_repo):
        """Test getting the last submission for a student and assignment"""
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
        
        last = submission_repo.get_last_submission(sample_student.get_id(), sample_assignment.get_id())
        assert last is not None
        assert last.version == 3

    def test_get_grade_for_assignment(self, sample_student, sample_assignment, submission_repo):
        """Test getting the best grade for an assignment"""
        # Create submissions with different scores
        scores = [50.0, 85.0, 70.0]
        for i, score in enumerate(scores):
            submission = Submission(
                id=None,
                assignment_id=sample_assignment.get_id(),
                student_id=sample_student.get_id(),
                version=i+1,
                language="python",
                status="graded",
                score=score,
                is_late=False,
                created_at=None,
                updated_at=None,
                grade_at=None
            )
            submission_repo.create(submission)
        
        grade = submission_repo.get_grade_for_assignment(sample_student.get_id(), sample_assignment.get_id())
        assert grade == 85.0

    def test_create_error(self, submission_repo, sample_student, sample_assignment):
        """Line 66-68: create handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        submission_repo.db = mock_db
        
        sub = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=1,
            language="python",
            status="pending",
            score=0.0
        )
        assert submission_repo.create(sub) is None
        mock_db.rollback.assert_called_once()

    def test_update_error(self, submission_repo, sample_submission):
        """Line 99-101: update handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        submission_repo.db = mock_db
        
        assert submission_repo.update(sample_submission) is None
        mock_db.rollback.assert_called_once()

    def test_delete_error(self, submission_repo):
        """Line 108-110: delete handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        submission_repo.db = mock_db
        
        assert submission_repo.delete(1) is False
        mock_db.rollback.assert_called_once()

    def test_get_all_success(self, submission_repo, sample_submission):
        """Lines 114-140: get_all retrieval"""
        all_subs = submission_repo.get_all()
        assert len(all_subs) >= 1

    def test_get_all_exception_handling(self, submission_repo):
        """Line 141-142: get_all skips invalid rows"""
        from unittest.mock import Mock
        mock_db = Mock()
        # Row with too few columns to trigger IndexError in constructor or logic
        invalid_row = (1, 2) 
        mock_db.execute.return_value.fetchall.return_value = [invalid_row]
        submission_repo.db = mock_db
        
        subs = submission_repo.get_all()
        assert len(subs) == 0

    def test_get_grades(self, submission_repo, sample_student, sample_assignment):
        """Lines 201-226: get_grades retrieval"""
        sub = Submission(
            id=None,
            assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=1,
            language="python",
            score=95.0,
            status="graded"
        )
        submission_repo.create(sub)
        
        grades = submission_repo.get_grades(sample_student.get_id())
        assert len(grades) >= 1
        assert any(g.score == 95.0 for g in grades)

    def test_get_last_submission_not_found(self, submission_repo):
        """Line 240: get_last_submission returns None if none exist"""
        assert submission_repo.get_last_submission(999, 999) is None

    def test_get_grade_for_assignment_none(self, submission_repo):
        """Line 267: get_grade_for_assignment returns None if no scores"""
        assert submission_repo.get_grade_for_assignment(999, 999) is None
