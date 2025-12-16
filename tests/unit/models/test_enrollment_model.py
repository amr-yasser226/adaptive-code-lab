import pytest
from datetime import datetime
from core.entities.enrollment import Enrollment


class TestEnrollment:
    """Test suite for Enrollment entity"""

    def test_init(self):
        """Test Enrollment initialization"""
        now = datetime.now()
        enrollment = Enrollment(
            student_id=1,
            course_id=10,
            status="enrolled",
            enrolled_at=now,
            dropped_at=None,
            final_grade=None
        )

        assert enrollment.get_student_id() == 1
        assert enrollment.get_course_id() == 10
        assert enrollment.status == "enrolled"
        assert enrollment.enrolled_at == now
        assert enrollment.dropped_at is None
        assert enrollment.final_grade is None

    def test_get_student_id(self):
        """Test get_student_id getter"""
        enrollment = Enrollment(
            student_id=42, course_id=1, status="enrolled",
            enrolled_at=datetime.now(), dropped_at=None, final_grade=None
        )
        assert enrollment.get_student_id() == 42

    def test_get_course_id(self):
        """Test get_course_id getter"""
        enrollment = Enrollment(
            student_id=1, course_id=99, status="enrolled",
            enrolled_at=datetime.now(), dropped_at=None, final_grade=None
        )
        assert enrollment.get_course_id() == 99

    def test_valid_status_enrolled(self):
        """Test enrolled status is valid"""
        enrollment = Enrollment(
            student_id=1, course_id=1, status="enrolled",
            enrolled_at=datetime.now(), dropped_at=None, final_grade=None
        )
        assert enrollment.status == "enrolled"

    def test_valid_status_dropped(self):
        """Test dropped status is valid"""
        enrollment = Enrollment(
            student_id=1, course_id=1, status="dropped",
            enrolled_at=datetime.now(), dropped_at=datetime.now(), final_grade=None
        )
        assert enrollment.status == "dropped"

    def test_valid_status_completed(self):
        """Test completed status is valid"""
        enrollment = Enrollment(
            student_id=1, course_id=1, status="completed",
            enrolled_at=datetime.now(), dropped_at=None, final_grade=95.0
        )
        assert enrollment.status == "completed"
        assert enrollment.final_grade == 95.0

    def test_invalid_status_raises_error(self):
        """Test invalid status raises ValueError"""
        with pytest.raises(ValueError, match="Invalid enrollment status"):
            Enrollment(
                student_id=1, course_id=1, status="invalid_status",
                enrolled_at=datetime.now(), dropped_at=None, final_grade=None
            )
