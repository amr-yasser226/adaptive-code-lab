import pytest
from datetime import datetime
from core.entities.submission import Submission


class TestSubmission:
    """Test suite for Submission entity"""

    def test_init(self):
        """Test Submission initialization"""
        now = datetime.now()
        submission = Submission(
            id=1,
            assignment_id=10,
            student_id=5,
            version=1,
            language="python",
            status="pending",
            score=None,
            is_late=False,
            created_at=now,
            updated_at=now,
            grade_at=None
        )

        assert submission.get_id() == 1
        assert submission.get_assignment_id() == 10
        assert submission.get_student_id() == 5
        assert submission.version == 1
        assert submission.language == "python"
        assert submission.status == "pending"

    def test_get_id(self):
        """Test get_id getter"""
        submission = Submission(
            id=42, assignment_id=1, student_id=1, version=1,
            language="python", status="pending", score=None,
            is_late=False, created_at=datetime.now(),
            updated_at=datetime.now(), grade_at=None
        )
        assert submission.get_id() == 42

    def test_get_assignment_id(self):
        """Test get_assignment_id getter"""
        submission = Submission(
            id=1, assignment_id=99, student_id=1, version=1,
            language="python", status="pending", score=None,
            is_late=False, created_at=datetime.now(),
            updated_at=datetime.now(), grade_at=None
        )
        assert submission.get_assignment_id() == 99

    def test_get_student_id(self):
        """Test get_student_id getter"""
        submission = Submission(
            id=1, assignment_id=1, student_id=77, version=1,
            language="python", status="pending", score=None,
            is_late=False, created_at=datetime.now(),
            updated_at=datetime.now(), grade_at=None
        )
        assert submission.get_student_id() == 77

    def test_valid_language_python(self):
        """Test python is valid language"""
        submission = Submission(
            id=1, assignment_id=1, student_id=1, version=1,
            language="python", status="pending", score=None,
            is_late=False, created_at=datetime.now(),
            updated_at=datetime.now(), grade_at=None
        )
        assert submission.language == "python"

    def test_valid_language_java(self):
        """Test java is valid language"""
        submission = Submission(
            id=1, assignment_id=1, student_id=1, version=1,
            language="java", status="pending", score=None,
            is_late=False, created_at=datetime.now(),
            updated_at=datetime.now(), grade_at=None
        )
        assert submission.language == "java"

    def test_invalid_language_raises_error(self):
        """Test invalid language raises ValueError"""
        with pytest.raises(ValueError, match="Invalid language"):
            Submission(
                id=1, assignment_id=1, student_id=1, version=1,
                language="ruby", status="pending", score=None,
                is_late=False, created_at=datetime.now(),
                updated_at=datetime.now(), grade_at=None
            )

    def test_valid_status_graded(self):
        """Test graded is valid status"""
        submission = Submission(
            id=1, assignment_id=1, student_id=1, version=1,
            language="python", status="graded", score=95.0,
            is_late=False, created_at=datetime.now(),
            updated_at=datetime.now(), grade_at=datetime.now()
        )
        assert submission.status == "graded"
        assert submission.score == 95.0

    def test_invalid_status_raises_error(self):
        """Test invalid status raises ValueError"""
        with pytest.raises(ValueError, match="Invalid status"):
            Submission(
                id=1, assignment_id=1, student_id=1, version=1,
                language="python", status="unknown", score=None,
                is_late=False, created_at=datetime.now(),
                updated_at=datetime.now(), grade_at=None
            )

    def test_is_late_converted_to_bool(self):
        """Test is_late is converted to boolean"""
        submission = Submission(
            id=1, assignment_id=1, student_id=1, version=1,
            language="python", status="pending", score=None,
            is_late=1, created_at=datetime.now(),
            updated_at=datetime.now(), grade_at=None
        )
        assert submission.is_late is True
