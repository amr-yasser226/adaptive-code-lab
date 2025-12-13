import pytest
from unittest.mock import Mock
from core.services.instructor_service import InstructorService
from core.entities.instructor import Instructor
from core.exceptions.auth_error import AuthError

@pytest.fixture
def mock_repos():
    return {
        'instructor': Mock(),
        'course': Mock(),
        'assignment': Mock(),
        'enrollment': Mock(),
        'submission': Mock(),
        'flag': Mock()
    }

@pytest.fixture
def instructor_service(mock_repos):
    return InstructorService(
        mock_repos['instructor'],
        mock_repos['course'],
        mock_repos['assignment'],
        mock_repos['enrollment'],
        mock_repos['submission'],
        mock_repos['flag']
    )

def test_create_course_success(instructor_service, mock_repos):
    instructor = Mock(spec=Instructor)
    instructor.role = "instructor"
    instructor.get_id.return_value = 99
    
    mock_repos['instructor'].get_by_id.return_value = instructor
    mock_repos['course'].create.return_value = True
    
    result = instructor_service.create_course(
        99, "CS101", "Intro to CS", "Course description", 
        2024, "Fall", 30, 3
    )
    
    assert result is True
    args, _ = mock_repos['course'].create.call_args
    course = args[0]
    assert course.title == "Intro to CS"
    assert course.get_instructor_id() == 99

def test_create_course_not_instructor(instructor_service, mock_repos):
    mock_repos['instructor'].get_by_id.return_value = None
    
    from core.exceptions.validation_error import ValidationError
    with pytest.raises(ValidationError, match="Instructor not found"):
        instructor_service.create_course(99, "CS101", "Desc", "Description", 2024, "Fall", 30, 3)

