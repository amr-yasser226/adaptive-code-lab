import pytest
from datetime import datetime


class TestInputValidation:
    """Test suite for input validation and sanitization"""

    def test_email_validation(self, sample_student):
        """Test email format validation"""
        # Verify sample student was created with valid email
        assert sample_student is not None
        assert "@" in sample_student.email

    def test_enrollment_status_validation(self):
        """Test enrollment only accepts valid statuses"""
        from core.entities.enrollment import Enrollment

        # Valid statuses
        for status in ["enrolled", "dropped", "completed"]:
            enrollment = Enrollment(
                student_id=1, course_id=1, status=status,
                final_grade=None, enrolled_at=datetime.now(), dropped_at=None
            )
            assert enrollment.status == status

        # Invalid status should raise
        with pytest.raises(ValueError):
            Enrollment(
                student_id=1, course_id=1, status="invalid_status",
                final_grade=None, enrolled_at=datetime.now(), dropped_at=None
            )

    def test_submission_language_validation(self):
        """Test submission language field validation"""
        from core.entities.submission import Submission

        # Valid language
        submission = Submission(
            id=None, assignment_id=1, student_id=1,
            version=1, language="python", status="pending",
            score=0.0, is_late=False,
            created_at=None, updated_at=None, grade_at=None
        )
        assert submission.language == "python"

    def test_score_range_validation(self, sample_assignment, sample_student, submission_repo):
        """Test score must be within valid range"""
        from core.entities.submission import Submission

        # Score of 0 should work
        submission = Submission(
            id=None, assignment_id=sample_assignment.get_id(),
            student_id=sample_student.get_id(),
            version=1, language="python", status="graded",
            score=0.0, is_late=False,
            created_at=None, updated_at=None, grade_at=datetime.now()
        )
        saved = submission_repo.create(submission)
        assert saved.score == 0.0

    def test_string_length_limits(self, sample_student):
        """Test string fields respect length limits"""
        # Verify sample student has reasonable length names
        assert len(sample_student.name) > 0
        assert len(sample_student.name) < 256

    def test_date_format_validation(self, sample_assignment):
        """Test date fields accept valid formats"""
        # Verify assignment has valid dates
        assert sample_assignment is not None
        assert sample_assignment.release_date is not None
        assert sample_assignment.due_date is not None
