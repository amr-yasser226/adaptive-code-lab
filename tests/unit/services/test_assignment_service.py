import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from core.services.assignment_service import AssignmentService
from core.entities.instructor import Instructor
from core.entities.course import Course
from core.entities.assignment import Assignment
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError

@pytest.fixture
def mock_repos():
    return {
        'assignment': Mock(),
        'course': Mock(),
        'submission': Mock()
    }

@pytest.fixture
def assignment_service(mock_repos):
    return AssignmentService(
        mock_repos['assignment'],
        mock_repos['course'],
        mock_repos['submission']
    )

def test_create_assignment_success(assignment_service, mock_repos):
    instructor = Mock(spec=Instructor)
    instructor.role = "instructor"
    instructor.get_id.return_value = 99
    
    course = Mock(spec=Course)
    course.status = "active"
    course.get_instructor_id.return_value = 99
    mock_repos['course'].get_by_id.return_value = course
    
    mock_repos['assignment'].create.return_value = True
    
    result = assignment_service.create_assignment(
        instructor, 101, "Lab 1", "Desc", datetime.now(), datetime.now() + timedelta(days=7), 100
    )
    
    assert result is True
    mock_repos['assignment'].create.assert_called_once()

def test_create_assignment_not_owner(assignment_service, mock_repos):
    instructor = Mock(spec=Instructor)
    instructor.role = "instructor"
    instructor.get_id.return_value = 99
    
    course = Mock(spec=Course)
    course.get_instructor_id.return_value = 88 # Different owner
    mock_repos['course'].get_by_id.return_value = course
    
    with pytest.raises(AuthError, match="not own this course"):
        assignment_service.create_assignment(
            instructor, 101, "Lab 1", "Desc", datetime.now(), datetime.now(), 100
        )

def test_publish_assignment_success(assignment_service, mock_repos):
    instructor = Mock(spec=Instructor)
    instructor.get_id.return_value = 99
    
    assignment = Mock(spec=Assignment)
    assignment.get_course_id.return_value = 101
    mock_repos['assignment'].get_by_id.return_value = assignment
    
    course = Mock(spec=Course)
    course.get_instructor_id.return_value = 99
    mock_repos['course'].get_by_id.return_value = course
    
    mock_repos['assignment'].publish.return_value = True
    
    result = assignment_service.publish_assignment(instructor, 1)
    assert result is True
