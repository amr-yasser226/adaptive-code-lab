import pytest
from datetime import datetime
from unittest.mock import Mock
from core.entities.instructor import Instructor


class TestInstructor:
    """Test suite for Instructor entity"""

    def test_init(self):
        """Test Instructor initialization"""
        now = datetime.now()
        instructor = Instructor(
            id=1,
            name="Dr. Smith",
            email="smith@university.edu",
            password="hashed_pwd",
            created_at=now,
            updated_at=now,
            instructor_code="INS001",
            bio="Computer Science Professor",
            office_hours="Mon-Wed 2-4pm"
        )

        assert instructor.get_id() == 1
        assert instructor.name == "Dr. Smith"
        assert instructor.email == "smith@university.edu"
        assert instructor.role == "instructor"
        assert instructor.instructor_code == "INS001"
        assert instructor.bio == "Computer Science Professor"
        assert instructor.office_hours == "Mon-Wed 2-4pm"

    def test_inherits_from_user(self):
        """Test Instructor inherits User properties"""
        from core.entities.user import User
        instructor = Instructor(
            id=1, name="Test", email="test@test.com",
            password="pwd", created_at=datetime.now(),
            updated_at=datetime.now(), instructor_code="INS",
            bio="", office_hours=""
        )
        assert isinstance(instructor, User)

    def test_create_course(self):
        """Test create_course method"""
        instructor = Instructor(
            id=1, name="Test", email="test@test.com",
            password="pwd", created_at=datetime.now(),
            updated_at=datetime.now(), instructor_code="INS",
            bio="", office_hours=""
        )

        mock_repo = Mock()
        mock_repo.create.return_value = Mock()

        result = instructor.create_course(
            course_repo=mock_repo,
            code="CS101",
            title="Intro to CS",
            description="Basic programming",
            year=2024,
            semester="Fall",
            max_students=30,
            credits=3
        )

        mock_repo.create.assert_called_once()
        args, _ = mock_repo.create.call_args
        course = args[0]
        assert course.code == "CS101"
        assert course.title == "Intro to CS"
        assert course.status == "inactive"  # New courses start inactive

    def test_export_grades(self):
        """Test export_grades method"""
        instructor = Instructor(
            id=1, name="Test", email="test@test.com",
            password="pwd", created_at=datetime.now(),
            updated_at=datetime.now(), instructor_code="INS",
            bio="", office_hours=""
        )

        mock_course_repo = Mock()
        course = Mock()
        course.get_instructor_id.return_value = 1
        mock_course_repo.get_by_id.return_value = course

        enrollment = Mock()
        enrollment.get_student_id.return_value = 10
        enrollment.status = "completed"
        enrollment.final_grade = 95.0
        enrollment.enrolled_at = datetime.now()
        enrollment.dropped_at = None

        mock_enrollment_repo = Mock()
        mock_enrollment_repo.list_by_course.return_value = [enrollment]

        result = instructor.export_grades(1, mock_course_repo, mock_enrollment_repo)

        assert len(result) == 1
        assert result[0]["student_id"] == 10
        assert result[0]["final_grade"] == 95.0

    def test_export_grades_wrong_instructor(self):
        """Test export_grades raises error for wrong instructor"""
        instructor = Instructor(
            id=1, name="Test", email="test@test.com",
            password="pwd", created_at=datetime.now(),
            updated_at=datetime.now(), instructor_code="INS",
            bio="", office_hours=""
        )

        mock_course_repo = Mock()
        course = Mock()
        course.get_instructor_id.return_value = 999  # Different instructor
        mock_course_repo.get_by_id.return_value = course

        mock_enrollment_repo = Mock()

        with pytest.raises(Exception, match="You can only export grades for your own courses"):
            instructor.export_grades(1, mock_course_repo, mock_enrollment_repo)

    def test_get_courses(self):
        """Test get_courses method"""
        instructor = Instructor(
            id=1, name="Test", email="test@test.com",
            password="pwd", created_at=datetime.now(),
            updated_at=datetime.now(), instructor_code="INS",
            bio="", office_hours=""
        )

        mock_repo = Mock()
        courses = [Mock(), Mock()]
        mock_repo.list_by_instructor.return_value = courses

        result = instructor.get_courses(mock_repo)

        mock_repo.list_by_instructor.assert_called_once_with(1)
        assert result == courses

    def test_review_similarity_confirm(self):
        """Test review_similarity with confirm action"""
        instructor = Instructor(
            id=1, name="Test", email="test@test.com",
            password="pwd", created_at=datetime.now(),
            updated_at=datetime.now(), instructor_code="INS",
            bio="", office_hours=""
        )

        mock_repo = Mock()
        mock_flag = Mock()
        mock_repo.get_by_id.return_value = mock_flag

        instructor.review_similarity(99, 'confirm', 'Cheating detected', mock_repo)

        mock_repo.get_by_id.assert_called_with(99)
        mock_flag.mark_reviewed.assert_called_once()
        args, _ = mock_flag.mark_reviewed.call_args
        assert args[0] == 1  # instructor_id
        assert args[2] == 'Cheating detected'
        mock_repo.update.assert_called_once_with(mock_flag)

    def test_review_similarity_invalid_action(self):
        """Test review_similarity raises error on invalid action"""
        instructor = Instructor(
            id=1, name="Test", email="test@test.com",
            password="pwd", created_at=datetime.now(),
            updated_at=datetime.now(), instructor_code="INS",
            bio="", office_hours=""
        )
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = Mock()

        with pytest.raises(Exception, match="Invalid action"):
            instructor.review_similarity(99, 'invalid', None, mock_repo)
