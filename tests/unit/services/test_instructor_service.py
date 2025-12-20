import pytest
from datetime import datetime
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
    mock_repos['user'] = Mock()
    return InstructorService(
        mock_repos['instructor'],
        mock_repos['course'],
        mock_repos['assignment'],
        mock_repos['enrollment'],
        mock_repos['submission'],
        mock_repos['flag'],
        user_repo=mock_repos['user']
    )

def test_get_instructor_via_user_repo(instructor_service, mock_repos):
    """Line 22-24: Get instructor via user_repo"""
    user = Mock()
    user.role = 'instructor'
    mock_repos['user'].get_by_id.return_value = user
    result = instructor_service.get_instructor(1)
    assert result == user

def test_create_assignment_success(instructor_service, mock_repos):
    """Lines 66-93: Successfully create an assignment"""
    instructor = Mock()
    instructor.role = 'instructor'
    instructor.get_id.return_value = 10
    mock_repos['user'].get_by_id.return_value = instructor
    
    course = Mock()
    course.get_instructor_id.return_value = 10
    mock_repos['course'].get_by_id.return_value = course
    
    mock_repos['assignment'].create.return_value = True
    
    result = instructor_service.create_assignment(
        10, 1, "HW1", "Desc", datetime.now(), datetime.now(), 100
    )
    assert result is True
    mock_repos['assignment'].create.assert_called_once()

def test_create_assignment_course_not_found(instructor_service, mock_repos):
    """Line 71: ValidationError when course not found"""
    instructor = Mock()
    instructor.role = 'instructor'
    mock_repos['user'].get_by_id.return_value = instructor
    mock_repos['course'].get_by_id.return_value = None
    
    from core.exceptions.validation_error import ValidationError
    with pytest.raises(ValidationError, match="Course not found"):
        instructor_service.create_assignment(10, 999, "T", "D", None, None, 100)

def test_create_assignment_unauthorized(instructor_service, mock_repos):
    """Line 74: AuthError when instructor doesn't own course"""
    instructor = Mock()
    instructor.role = 'instructor'
    instructor.get_id.return_value = 10
    mock_repos['user'].get_by_id.return_value = instructor
    
    course = Mock()
    course.get_instructor_id.return_value = 99 # Different
    mock_repos['course'].get_by_id.return_value = course
    
    with pytest.raises(AuthError, match="own courses"):
        instructor_service.create_assignment(10, 1, "T", "D", None, None, 100)

def test_export_grades_success(instructor_service, mock_repos):
    """Lines 111-121: Successfully export grades"""
    instructor = Mock()
    instructor.role = 'instructor'
    instructor.get_id.return_value = 10
    mock_repos['user'].get_by_id.return_value = instructor
    
    course = Mock()
    course.get_instructor_id.return_value = 10
    mock_repos['course'].get_by_id.return_value = course
    
    enrollment = Mock()
    enrollment.get_student_id.return_value = 5
    enrollment.status = "enrolled"
    enrollment.final_grade = 95
    enrollment.enrolled_at = None
    enrollment.dropped_at = None
    mock_repos['enrollment'].list_by_course.return_value = [enrollment]
    
    result = instructor_service.export_grades(10, 1)
    assert len(result) == 1
    assert result[0]["student_id"] == 5

def test_export_grades_course_not_found(instructor_service, mock_repos):
    """Line 102: Course not found during export"""
    instructor = Mock()
    instructor.role = 'instructor'
    mock_repos['user'].get_by_id.return_value = instructor
    mock_repos['course'].get_by_id.return_value = None
    from core.exceptions.validation_error import ValidationError
    with pytest.raises(ValidationError, match="Course not found"):
        instructor_service.export_grades(10, 999)

def test_export_grades_unauthorized(instructor_service, mock_repos):
    """Line 106: Unauthorized grade export"""
    instructor = Mock()
    instructor.role = 'instructor'
    instructor.get_id.return_value = 10
    mock_repos['user'].get_by_id.return_value = instructor
    course = Mock()
    course.get_instructor_id.return_value = 99
    mock_repos['course'].get_by_id.return_value = course
    with pytest.raises(AuthError, match="own courses"):
        instructor_service.export_grades(10, 1)

def test_list_instructor_courses(instructor_service, mock_repos):
    """Line 126: List courses for instructor"""
    instructor = Mock()
    instructor.role = 'instructor'
    instructor.get_id.return_value = 10
    mock_repos['user'].get_by_id.return_value = instructor
    mock_repos['course'].list_by_instructor.return_value = []
    result = instructor_service.list_instructor_courses(10)
    assert result == []

def test_review_similarity_success_all_actions(instructor_service, mock_repos):
    """Lines 180-199: Review similarity with all valid actions"""
    instructor = Mock()
    instructor.role = 'instructor'
    instructor.get_id.return_value = 10
    mock_repos['user'].get_by_id.return_value = instructor
    
    flag = Mock()
    flag.get_submission_id.return_value = 1
    mock_repos['flag'].get_by_id.return_value = flag
    
    submission = Mock()
    submission.get_assignment_id.return_value = 1
    mock_repos['submission'].get_by_id.return_value = submission
    
    assignment = Mock()
    assignment.get_course_id.return_value = 1
    mock_repos['assignment'].get_by_id.return_value = assignment
    
    course = Mock()
    course.get_instructor_id.return_value = 10
    mock_repos['course'].get_by_id.return_value = course
    
    # Test Approve
    instructor_service.review_similarity(10, 1, "approve", "Looks fine")
    mock_repos['flag'].mark_reviewed.assert_called_once()
    
    # Test Dismiss
    instructor_service.review_similarity(10, 1, "dismiss")
    mock_repos['flag'].dismiss.assert_called_once()
    
    # Test Escalate
    instructor_service.review_similarity(10, 1, "escalate")
    mock_repos['flag'].escalate.assert_called_once()

def test_review_similarity_invalid_action(instructor_service, mock_repos):
    """Line 202: Invalid action raises ValidationError"""
    instructor = Mock()
    instructor.role = 'instructor'
    instructor.get_id.return_value = 10
    mock_repos['user'].get_by_id.return_value = instructor
    
    flag = Mock()
    flag.get_submission_id.return_value = 1
    mock_repos['flag'].get_by_id.return_value = flag
    
    submission = Mock()
    submission.get_assignment_id.return_value = 1
    mock_repos['submission'].get_by_id.return_value = submission
    
    assignment = Mock()
    assignment.get_course_id.return_value = 1
    mock_repos['assignment'].get_by_id.return_value = assignment
    
    course = Mock()
    course.get_instructor_id.return_value = 10
    mock_repos['course'].get_by_id.return_value = course
    
    from core.exceptions.validation_error import ValidationError
    with pytest.raises(ValidationError, match="Invalid action"):
        instructor_service.review_similarity(10, 1, "hack")

def test_review_similarity_missing_entities(instructor_service, mock_repos):
    """Lines 145, 152, 159, 166: Missing entities during review"""
    instructor = Mock()
    instructor.get_id.return_value = 10
    mock_repos['user'].get_by_id.return_value = instructor
    from core.exceptions.validation_error import ValidationError
    
    # Flag missing
    mock_repos['flag'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Similarity flag not found"):
        instructor_service.review_similarity(10, 1, "approve")
    
    # Submission missing
    mock_repos['flag'].get_by_id.return_value = Mock()
    mock_repos['submission'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Submission not found"):
        instructor_service.review_similarity(10, 1, "approve")
        
    # Assignment missing
    mock_repos['submission'].get_by_id.return_value = Mock()
    mock_repos['assignment'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Assignment not found"):
        instructor_service.review_similarity(10, 1, "approve")
        
    # Course missing
    mock_repos['assignment'].get_by_id.return_value = Mock()
    mock_repos['course'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Course not found"):
        instructor_service.review_similarity(10, 1, "approve")

def test_review_similarity_unauthorized(instructor_service, mock_repos):
    """Line 169: Unauthorized similarity review"""
    instructor = Mock()
    instructor.get_id.return_value = 10
    mock_repos['user'].get_by_id.return_value = instructor
    mock_repos['flag'].get_by_id.return_value = Mock()
    mock_repos['submission'].get_by_id.return_value = Mock()
    mock_repos['assignment'].get_by_id.return_value = Mock()
    course = Mock()
    course.get_instructor_id.return_value = 99 # Different
    mock_repos['course'].get_by_id.return_value = course
    
    with pytest.raises(AuthError, match="not allowed"):
        instructor_service.review_similarity(10, 1, "approve")

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

