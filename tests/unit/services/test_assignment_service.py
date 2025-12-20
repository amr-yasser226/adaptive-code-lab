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

def test_verify_instructor_owns_course_not_found(assignment_service, mock_repos):
    """Line 21: ValidationError when course is not found"""
    mock_repos['course'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Course not found"):
        assignment_service._verify_instructor_owns_course(1, 999)

def test_create_assignment_not_instructor(assignment_service):
    """Line 43: AuthError when non-instructor tries to create assignment"""
    user = Mock()
    user.role = "student"
    with pytest.raises(AuthError, match="Only instructors can create"):
        assignment_service.create_assignment(user, 1, "T", "D", None, None, 100)

def test_create_assignment_inactive_course(assignment_service, mock_repos):
    """Line 50: ValidationError when course is inactive"""
    instructor = Mock()
    instructor.role = "instructor"
    instructor.get_id.return_value = 1
    course = Mock()
    course.status = "inactive"
    course.get_instructor_id.return_value = 1
    mock_repos['course'].get_by_id.return_value = course
    with pytest.raises(ValidationError, match="inactive course"):
        assignment_service.create_assignment(instructor, 1, "T", "D", None, None, 100)

def test_publish_assignment_not_found(assignment_service, mock_repos):
    """Line 72: ValidationError when assignment not found during publish"""
    mock_repos['assignment'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Assignment not found"):
        assignment_service.publish_assignment(Mock(), 999)

def test_unpublish_assignment_success(assignment_service, mock_repos):
    """Lines 82-90: Successful unpublish"""
    instructor = Mock()
    instructor.get_id.return_value = 1
    assignment = Mock()
    assignment.get_course_id.return_value = 10
    mock_repos['assignment'].get_by_id.return_value = assignment
    course = Mock()
    course.get_instructor_id.return_value = 1
    mock_repos['course'].get_by_id.return_value = course
    mock_repos['assignment'].unpublish.return_value = True
    assert assignment_service.unpublish_assignment(instructor, 1) is True

def test_unpublish_assignment_not_found(assignment_service, mock_repos):
    """Line 84: ValidationError when assignment not found during unpublish"""
    mock_repos['assignment'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Assignment not found"):
        assignment_service.unpublish_assignment(Mock(), 999)

def test_extend_deadline_success(assignment_service, mock_repos):
    """Lines 93-106: Successful deadline extension"""
    instructor = Mock()
    instructor.get_id.return_value = 1
    assignment = Mock()
    assignment.get_course_id.return_value = 10
    assignment.release_date = datetime(2023, 1, 1)
    mock_repos['assignment'].get_by_id.return_value = assignment
    course = Mock()
    course.get_instructor_id.return_value = 1
    mock_repos['course'].get_by_id.return_value = course
    mock_repos['assignment'].extend_deadline.return_value = True
    new_date = datetime(2023, 2, 1)
    assert assignment_service.extend_deadline(instructor, 1, new_date) is True

def test_extend_deadline_not_found(assignment_service, mock_repos):
    """Line 95: ValidationError when assignment not found during deadline extension"""
    mock_repos['assignment'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Assignment not found"):
        assignment_service.extend_deadline(Mock(), 999, datetime.now())

def test_extend_deadline_invalid_date(assignment_service, mock_repos):
    """Line 102: ValidationError when new due date is before release date"""
    instructor = Mock()
    instructor.get_id.return_value = 1
    assignment = Mock()
    assignment.get_course_id.return_value = 10
    assignment.release_date = datetime(2023, 1, 10)
    mock_repos['assignment'].get_by_id.return_value = assignment
    course = Mock()
    course.get_instructor_id.return_value = 1
    mock_repos['course'].get_by_id.return_value = course
    with pytest.raises(ValidationError, match="after release date"):
        assignment_service.extend_deadline(instructor, 1, datetime(2023, 1, 5))

def test_list_assignments_not_found(assignment_service, mock_repos):
    """Line 111: ValidationError when course not found during listing"""
    mock_repos['course'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Course not found"):
        assignment_service.list_assignments_for_course(Mock(), 999)

def test_list_assignments_student_filter(assignment_service, mock_repos):
    """Lines 116-117: Students only see published assignments"""
    user = Mock()
    user.role = "student"
    mock_repos['course'].get_by_id.return_value = Mock()
    a1 = Mock(); a1.is_published = True
    a2 = Mock(); a2.is_published = False
    mock_repos['assignment'].list_by_course.return_value = [a1, a2]
    result = assignment_service.list_assignments_for_course(user, 1)
    assert len(result) == 1
    assert result[0] == a1

def test_list_assignments_instructor_all(assignment_service, mock_repos):
    """Line 120: Instructors see all assignments"""
    user = Mock()
    user.role = "instructor"
    mock_repos['course'].get_by_id.return_value = Mock()
    a1 = Mock(); a1.is_published = True
    a2 = Mock(); a2.is_published = False
    mock_repos['assignment'].list_by_course.return_value = [a1, a2]
    result = assignment_service.list_assignments_for_course(user, 1)
    assert len(result) == 2

def test_get_submissions_success(assignment_service, mock_repos):
    """Lines 124-132: Successful submission retrieval"""
    instructor = Mock(); instructor.get_id.return_value = 1
    assignment = Mock(); assignment.get_course_id.return_value = 10
    mock_repos['assignment'].get_by_id.return_value = assignment
    mock_repos['course'].get_by_id.return_value = Mock(get_instructor_id=lambda: 1)
    mock_repos['submission'].list_by_assignment.return_value = [Mock()]
    result = assignment_service.get_submissions(instructor, 1)
    assert len(result) == 1

def test_get_submissions_not_found(assignment_service, mock_repos):
    """Line 126: ValidationError when assignment not found in get_submissions"""
    mock_repos['assignment'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Assignment not found"):
        assignment_service.get_submissions(Mock(), 999)

def test_calculate_statistics_success(assignment_service, mock_repos):
    """Lines 136-161: Successful statistics calculation"""
    instructor = Mock(); instructor.get_id.return_value = 1
    assignment = Mock(); assignment.get_course_id.return_value = 10
    mock_repos['assignment'].get_by_id.return_value = assignment
    mock_repos['course'].get_by_id.return_value = Mock(get_instructor_id=lambda: 1)
    s1 = Mock(); s1.score = 80
    s2 = Mock(); s2.score = 90
    s3 = Mock(); s3.score = None
    mock_repos['submission'].list_by_assignment.return_value = [s1, s2, s3]
    stats = assignment_service.calculate_statistics(instructor, 1)
    assert stats["count"] == 2
    assert stats["average"] == 85
    assert stats["min"] == 80
    assert stats["max"] == 90

def test_calculate_statistics_not_found(assignment_service, mock_repos):
    """Line 138: ValidationError when assignment not found in calculate_statistics"""
    mock_repos['assignment'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Assignment not found"):
        assignment_service.calculate_statistics(Mock(), 999)

def test_calculate_statistics_no_scores(assignment_service, mock_repos):
    """Lines 149-154: Empty stats when no scores available"""
    instructor = Mock(); instructor.get_id.return_value = 1
    assignment = Mock(); assignment.get_course_id.return_value = 10
    mock_repos['assignment'].get_by_id.return_value = assignment
    mock_repos['course'].get_by_id.return_value = Mock(get_instructor_id=lambda: 1)
    mock_repos['submission'].list_by_assignment.return_value = []
    stats = assignment_service.calculate_statistics(instructor, 1)
    assert stats["count"] == 0
    assert stats["average"] == 0
