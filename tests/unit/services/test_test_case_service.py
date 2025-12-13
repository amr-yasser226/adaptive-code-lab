import pytest
from unittest.mock import Mock
from core.services.test_case_service import TestCaseService
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_testcase_repo():
    return Mock()


@pytest.fixture
def mock_assignment_repo():
    return Mock()


@pytest.fixture
def mock_course_repo():
    return Mock()


@pytest.fixture
def test_case_service(mock_testcase_repo, mock_assignment_repo, mock_course_repo):
    return TestCaseService(
        testcase_repo=mock_testcase_repo,
        assignment_repo=mock_assignment_repo,
        course_repo=mock_course_repo
    )


@pytest.fixture
def instructor_user():
    user = Mock()
    user.role = "instructor"
    user.get_id.return_value = 10
    return user


@pytest.fixture
def student_user():
    user = Mock()
    user.role = "student"
    user.get_id.return_value = 5
    return user


def setup_instructor_owns(mock_assignment_repo, mock_course_repo, instructor_id=10):
    """Setup mocks for instructor ownership check"""
    assignment = Mock()
    assignment.get_course_id.return_value = 1
    assignment.get_id.return_value = 1
    mock_assignment_repo.get_by_id.return_value = assignment

    course = Mock()
    course.get_instructor_id.return_value = instructor_id
    mock_course_repo.get_by_id.return_value = course

    return assignment


class TestTestCaseService:
    """Test suite for TestCaseService"""

    def test_create_test_case_success(self, test_case_service, instructor_user,
                                       mock_testcase_repo, mock_assignment_repo, mock_course_repo):
        """Test successful test case creation"""
        setup_instructor_owns(mock_assignment_repo, mock_course_repo)
        mock_testcase_repo.create.return_value = Mock()

        result = test_case_service.create_test_case(
            instructor=instructor_user,
            assignment_id=1,
            name="Basic Test",
            stdin="input",
            expected_out="output",
            points=10
        )

        mock_testcase_repo.create.assert_called_once()

    def test_create_test_case_non_instructor_denied(self, test_case_service, student_user):
        """Non-instructors cannot create test cases"""
        with pytest.raises(AuthError, match="Only instructors can create test cases"):
            test_case_service.create_test_case(student_user, 1, "Test", "", "", 10)

    def test_create_test_case_assignment_not_found(self, test_case_service, instructor_user,
                                                    mock_assignment_repo):
        """Assignment not found raises ValidationError"""
        mock_assignment_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Assignment not found"):
            test_case_service.create_test_case(instructor_user, 999, "Test", "", "", 10)

    def test_create_test_case_not_owner(self, test_case_service, instructor_user,
                                         mock_assignment_repo, mock_course_repo):
        """Instructor doesn't own the course"""
        setup_instructor_owns(mock_assignment_repo, mock_course_repo, instructor_id=999)

        with pytest.raises(AuthError, match="You do not own this course"):
            test_case_service.create_test_case(instructor_user, 1, "Test", "", "", 10)

    def test_create_test_case_invalid_points(self, test_case_service, instructor_user,
                                              mock_assignment_repo, mock_course_repo):
        """Zero or negative points raises ValidationError"""
        setup_instructor_owns(mock_assignment_repo, mock_course_repo)

        with pytest.raises(ValidationError, match="Points must be greater than zero"):
            test_case_service.create_test_case(instructor_user, 1, "Test", "", "", 0)

    def test_update_test_case_success(self, test_case_service, instructor_user,
                                       mock_testcase_repo, mock_assignment_repo, mock_course_repo):
        """Test successful test case update"""
        testcase = Mock()
        testcase.get_assignment_id.return_value = 1
        testcase.points = 10
        mock_testcase_repo.get_by_id.return_value = testcase
        setup_instructor_owns(mock_assignment_repo, mock_course_repo)
        mock_testcase_repo.update.return_value = testcase

        result = test_case_service.update_test_case(
            instructor_user, 1, name="Updated Test"
        )

        mock_testcase_repo.update.assert_called_once()

    def test_update_test_case_not_found(self, test_case_service, instructor_user, mock_testcase_repo):
        """Test case not found raises ValidationError"""
        mock_testcase_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Test case not found"):
            test_case_service.update_test_case(instructor_user, 999)

    def test_delete_test_case_success(self, test_case_service, instructor_user,
                                       mock_testcase_repo, mock_assignment_repo, mock_course_repo):
        """Test successful test case deletion"""
        testcase = Mock()
        testcase.get_assignment_id.return_value = 1
        mock_testcase_repo.get_by_id.return_value = testcase
        setup_instructor_owns(mock_assignment_repo, mock_course_repo)
        mock_testcase_repo.delete.return_value = True

        result = test_case_service.delete_test_case(instructor_user, 1)

        mock_testcase_repo.delete.assert_called_once_with(1)

    def test_list_test_cases_as_instructor(self, test_case_service, instructor_user,
                                            mock_testcase_repo, mock_assignment_repo):
        """Instructor sees all test cases"""
        mock_assignment_repo.get_by_id.return_value = Mock()
        visible = Mock()
        visible.is_visible = True
        hidden = Mock()
        hidden.is_visible = False
        mock_testcase_repo.list_by_assignment.return_value = [visible, hidden]

        result = test_case_service.list_test_cases(instructor_user, 1)

        assert len(result) == 2

    def test_list_test_cases_as_student(self, test_case_service, student_user,
                                         mock_testcase_repo, mock_assignment_repo):
        """Students only see visible test cases"""
        mock_assignment_repo.get_by_id.return_value = Mock()
        visible = Mock()
        visible.is_visible = True
        hidden = Mock()
        hidden.is_visible = False
        mock_testcase_repo.list_by_assignment.return_value = [visible, hidden]

        result = test_case_service.list_test_cases(student_user, 1)

        assert len(result) == 1
        assert result[0].is_visible is True

    def test_list_test_cases_assignment_not_found(self, test_case_service, instructor_user,
                                                   mock_assignment_repo):
        """Assignment not found raises ValidationError"""
        mock_assignment_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Assignment not found"):
            test_case_service.list_test_cases(instructor_user, 999)
