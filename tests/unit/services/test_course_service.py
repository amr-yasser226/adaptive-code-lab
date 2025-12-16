import pytest
from unittest.mock import Mock
from core.services.course_service import CourseService
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_course_repo():
    return Mock()


@pytest.fixture
def mock_assignment_repo():
    return Mock()


@pytest.fixture
def mock_enrollment_repo():
    return Mock()


@pytest.fixture
def course_service(mock_course_repo, mock_assignment_repo, mock_enrollment_repo):
    return CourseService(mock_course_repo, mock_assignment_repo, mock_enrollment_repo)


class TestCourseService:
    """Test suite for CourseService"""

    def test_get_course_success(self, course_service, mock_course_repo):
        """Test getting a course successfully"""
        course = Mock()
        mock_course_repo.get_by_id.return_value = course

        result = course_service.get_course(1)

        mock_course_repo.get_by_id.assert_called_once_with(1)
        assert result == course

    def test_get_course_not_found(self, course_service, mock_course_repo):
        """Test getting a non-existent course raises ValidationError"""
        mock_course_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Course not found"):
            course_service.get_course(999)

    def test_publish_course(self, course_service, mock_course_repo):
        """Test publishing a course"""
        mock_course_repo.publish.return_value = Mock()

        result = course_service.publish_course(1)

        mock_course_repo.publish.assert_called_once_with(1)

    def test_archive_course(self, course_service, mock_course_repo):
        """Test archiving a course"""
        mock_course_repo.archive.return_value = Mock()

        result = course_service.archive_course(1)

        mock_course_repo.archive.assert_called_once_with(1)

    def test_list_assignments(self, course_service, mock_assignment_repo):
        """Test listing assignments for a course"""
        assignments = [Mock(), Mock()]
        mock_assignment_repo.list_by_course.return_value = assignments

        result = course_service.list_assignments(1)

        mock_assignment_repo.list_by_course.assert_called_once_with(1)
        assert result == assignments

    def test_get_enrolled_students(self, course_service, mock_enrollment_repo):
        """Test getting enrolled students for a course"""
        enrolled = Mock()
        enrolled.status = "enrolled"
        dropped = Mock()
        dropped.status = "dropped"
        mock_enrollment_repo.list_by_course.return_value = [enrolled, dropped]

        result = course_service.get_enrolled_students(1)

        assert len(result) == 1
        assert result[0] == enrolled

    def test_get_enrolled_students_empty(self, course_service, mock_enrollment_repo):
        """Test getting enrolled students when none enrolled"""
        mock_enrollment_repo.list_by_course.return_value = []

        result = course_service.get_enrolled_students(1)

        assert result == []
