import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from core.services.student_service import StudentService
from core.entities.student import Student
from core.entities.course import Course
from core.entities.enrollment import Enrollment
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError

@pytest.fixture
def mock_repos():
    return {
        'student': Mock(),
        'course': Mock(),
        'enrollment': Mock(),
        'assignment': Mock(),
        'submission': Mock()
    }

@pytest.fixture
def student_service(mock_repos):
    return StudentService(
        mock_repos['student'],
        mock_repos['course'],
        mock_repos['enrollment'],
        mock_repos['assignment'],
        mock_repos['submission']
    )

def test_enroll_course_success(student_service, mock_repos):
    student = Mock(spec=Student)
    student.role = "student"
    mock_repos['student'].get_by_id.return_value = student
    
    course = Mock(spec=Course)
    course.status = "active"
    mock_repos['course'].get_by_id.return_value = course
    
    mock_repos['enrollment'].get.return_value = None # Not enrolled
    mock_repos['enrollment'].enroll.return_value = True
    
    result = student_service.enroll_course(1, 101)
    
    assert result is True
    # Verify enrollment created with correct status
    args, _ = mock_repos['enrollment'].enroll.call_args
    enrollment = args[0]
    assert enrollment.get_student_id() == 1
    assert enrollment.get_course_id() == 101
    assert enrollment.status == "enrolled"

def test_enroll_already_enrolled(student_service, mock_repos):
    mock_repos['student'].get_by_id.return_value = Mock(spec=Student)
    mock_repos['course'].get_by_id.return_value = Mock(spec=Course)
    mock_repos['enrollment'].get.return_value = Mock(spec=Enrollment) # Exists
    
    with pytest.raises(ValidationError, match="Student already enrolled"):
        student_service.enroll_course(1, 101)

def test_drop_course_success(student_service, mock_repos):
    enrollment = Mock(spec=Enrollment)
    enrollment.status = "enrolled"
    mock_repos['enrollment'].get.return_value = enrollment
    mock_repos['enrollment'].update.return_value = True
    
    result = student_service.drop_course(1, 101)
    
    assert result is True
    assert enrollment.status == "dropped"
    assert enrollment.dropped_at is not None

def test_submit_assignment_not_enrolled(student_service, mock_repos):
    assignment = Mock()
    assignment.get_course_id.return_value = 101
    assignment.due_date = datetime.now()
    mock_repos['assignment'].get_by_id.return_value = assignment
    
    mock_repos['enrollment'].get.return_value = None # Not enrolled
    
    with pytest.raises(AuthError, match="not enrolled"):
        student_service.submit_assignment(1, 5, "code")

