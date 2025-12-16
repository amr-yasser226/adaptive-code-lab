import pytest
from unittest.mock import Mock
from core.services.enrollment_service import EnrollmentService
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_enrollment_repo():
    return Mock()


@pytest.fixture
def mock_course_repo():
    return Mock()


@pytest.fixture
def enrollment_service(mock_enrollment_repo, mock_course_repo):
    return EnrollmentService(mock_enrollment_repo, mock_course_repo)


@pytest.fixture
def student_user():
    user = Mock()
    user.role = "student"
    user.get_id.return_value = 1
    return user


@pytest.fixture
def non_student_user():
    user = Mock()
    user.role = "instructor"
    user.get_id.return_value = 2
    return user


class TestEnrollmentService:
    """Test suite for EnrollmentService"""

    def test_enroll_student_success(self, enrollment_service, student_user, 
                                     mock_enrollment_repo, mock_course_repo):
        """Test successful enrollment"""
        course = Mock()
        course.status = "active"
        mock_course_repo.get_by_id.return_value = course
        mock_enrollment_repo.get.return_value = None
        mock_enrollment_repo.enroll.return_value = Mock()

        result = enrollment_service.enroll_student(student_user, 1)

        mock_enrollment_repo.enroll.assert_called_once()

    def test_enroll_student_non_student_role(self, enrollment_service, non_student_user):
        """Non-students cannot enroll"""
        with pytest.raises(AuthError, match="Only students can enroll"):
            enrollment_service.enroll_student(non_student_user, 1)

    def test_enroll_student_course_not_found(self, enrollment_service, student_user, mock_course_repo):
        """Course not found raises ValidationError"""
        mock_course_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Course not found"):
            enrollment_service.enroll_student(student_user, 999)

    def test_enroll_student_course_not_active(self, enrollment_service, student_user, mock_course_repo):
        """Inactive course raises ValidationError"""
        course = Mock()
        course.status = "archived"
        mock_course_repo.get_by_id.return_value = course

        with pytest.raises(ValidationError, match="Course is not active"):
            enrollment_service.enroll_student(student_user, 1)

    def test_enroll_student_already_enrolled(self, enrollment_service, student_user, 
                                              mock_course_repo, mock_enrollment_repo):
        """Already enrolled raises ValidationError"""
        course = Mock()
        course.status = "active"
        mock_course_repo.get_by_id.return_value = course
        existing = Mock()
        existing.status = "enrolled"
        mock_enrollment_repo.get.return_value = existing

        with pytest.raises(ValidationError, match="Already enrolled"):
            enrollment_service.enroll_student(student_user, 1)

    def test_drop_course_success(self, enrollment_service, student_user, mock_enrollment_repo):
        """Test successful course drop"""
        enrollment = Mock()
        enrollment.status = "enrolled"
        mock_enrollment_repo.get.return_value = enrollment
        mock_enrollment_repo.update.return_value = enrollment

        result = enrollment_service.drop_course(student_user, 1)

        assert enrollment.status == "dropped"
        mock_enrollment_repo.update.assert_called_once()

    def test_drop_course_not_found(self, enrollment_service, student_user, mock_enrollment_repo):
        """Enrollment not found raises ValidationError"""
        mock_enrollment_repo.get.return_value = None

        with pytest.raises(ValidationError, match="Enrollment not found"):
            enrollment_service.drop_course(student_user, 1)

    def test_drop_course_not_enrolled(self, enrollment_service, student_user, mock_enrollment_repo):
        """Cannot drop if not enrolled"""
        enrollment = Mock()
        enrollment.status = "dropped"
        mock_enrollment_repo.get.return_value = enrollment

        with pytest.raises(ValidationError, match="Cannot drop this enrollment"):
            enrollment_service.drop_course(student_user, 1)

    def test_complete_course(self, enrollment_service, mock_enrollment_repo):
        """Test completing a course"""
        enrollment = Mock()
        mock_enrollment_repo.update.return_value = enrollment

        result = enrollment_service.complete_course(enrollment, 95.0)

        assert enrollment.status == "completed"
        assert enrollment.final_grade == 95.0

    def test_list_by_student(self, enrollment_service, mock_enrollment_repo):
        """Test listing enrollments by student"""
        enrollments = [Mock(), Mock()]
        mock_enrollment_repo.list_by_student.return_value = enrollments

        result = enrollment_service.list_by_student(1)

        mock_enrollment_repo.list_by_student.assert_called_once_with(1)
        assert result == enrollments

    def test_list_by_course(self, enrollment_service, mock_enrollment_repo):
        """Test listing enrollments by course"""
        enrollments = [Mock(), Mock()]
        mock_enrollment_repo.list_by_course.return_value = enrollments

        result = enrollment_service.list_by_course(1)

        mock_enrollment_repo.list_by_course.assert_called_once_with(1)
        assert result == enrollments
