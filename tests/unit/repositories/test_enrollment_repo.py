import pytest
import sqlite3
from unittest.mock import Mock
from core.entities.enrollment import Enrollment


@pytest.mark.repo
@pytest.mark.unit
class TestEnrollmentRepo:
    """Test suite for Enrollment_repo"""
    
    def test_enroll_student(self, sample_student, sample_course, enrollment_repo):
        """Test enrolling a student in a course"""
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            final_grade=None,
            enrolled_at=None,
            dropped_at=None
        )
        
        saved = enrollment_repo.enroll(enrollment)
        
        assert saved is not None
        assert saved.get_student_id() == sample_student.get_id()
        assert saved.status == "enrolled"
    
    def test_get_enrollment(self, sample_student, sample_course, enrollment_repo):
        """Test retrieving enrollment"""
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            final_grade=None,
            enrolled_at=None,
            dropped_at=None
        )
        enrollment_repo.enroll(enrollment)
        
        retrieved = enrollment_repo.get(
            sample_student.get_id(),
            sample_course.get_id()
        )
        
        assert retrieved is not None
        assert retrieved.status == "enrolled"

    def test_get_not_found(self, enrollment_repo):
        """Line 18: get returns None for non-existent enrollment"""
        assert enrollment_repo.get(999, 999) is None
    
    def test_update_enrollment(self, sample_student, sample_course, enrollment_repo):
        """Test updating enrollment"""
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            final_grade=None,
            enrolled_at=None,
            dropped_at=None
        )
        enrollment_repo.enroll(enrollment)
        
        enrollment.status = "completed"
        enrollment.final_grade = 85.5
        updated = enrollment_repo.update(enrollment)
        
        assert updated.status == "completed"
        assert updated.final_grade == 85.5
    
    def test_delete_enrollment(self, sample_student, sample_course, enrollment_repo):
        """Test deleting enrollment"""
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            final_grade=None,
            enrolled_at=None,
            dropped_at=None
        )
        enrollment_repo.enroll(enrollment)
        
        result = enrollment_repo.delete(
            sample_student.get_id(),
            sample_course.get_id()
        )
        
        assert result is True
        assert enrollment_repo.get(sample_student.get_id(), sample_course.get_id()) is None

    def test_enroll_error(self, enrollment_repo, sample_student, sample_course):
        """Line 51-53: enroll handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        enrollment_repo.db = mock_db
        enrollment = Enrollment(sample_student.get_id(), sample_course.get_id(), "enrolled", None, None, None)
        assert enrollment_repo.enroll(enrollment) is None
        mock_db.rollback.assert_called_once()

    def test_update_error(self, enrollment_repo, sample_student, sample_course):
        """Line 76-78: update handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        enrollment_repo.db = mock_db
        enrollment = Enrollment(sample_student.get_id(), sample_course.get_id(), "enrolled", None, None, None)
        assert enrollment_repo.update(enrollment) is None
        mock_db.rollback.assert_called_once()

    def test_delete_error(self, enrollment_repo):
        """Line 88-90: delete handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        enrollment_repo.db = mock_db
        assert enrollment_repo.delete(1, 1) is False
        mock_db.rollback.assert_called_once()
    
    def test_list_by_student(self, sample_student, sample_course, enrollment_repo):
        """Test listing enrollments by student"""
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            final_grade=None,
            enrolled_at=None,
            dropped_at=None
        )
        enrollment_repo.enroll(enrollment)
        
        enrollments = enrollment_repo.list_by_student(sample_student.get_id())
        assert len(enrollments) >= 1
    
    def test_list_by_course(self, sample_student, sample_course, enrollment_repo):
        """Test listing enrollments by course"""
        enrollment = Enrollment(
            student_id=sample_student.get_id(),
            course_id=sample_course.get_id(),
            status="enrolled",
            final_grade=None,
            enrolled_at=None,
            dropped_at=None
        )
        enrollment_repo.enroll(enrollment)
        
        enrollments = enrollment_repo.list_by_course(sample_course.get_id())
        assert len(enrollments) >= 1