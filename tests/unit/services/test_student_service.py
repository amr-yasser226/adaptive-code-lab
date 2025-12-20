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

def test_get_student_not_found(student_service, mock_repos):
    mock_repos['student'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Student not found"):
        student_service.get_student(999)

def test_enroll_course_not_found(student_service, mock_repos):
    mock_repos['student'].get_by_id.return_value = Mock()
    mock_repos['course'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Course does not exist"):
        student_service.enroll_course(1, 999)

def test_drop_course_not_enrolled(student_service, mock_repos):
    mock_repos['enrollment'].get.return_value = None
    with pytest.raises(ValidationError, match="not enrolled"):
        student_service.drop_course(1, 101)

def test_submit_assignment_not_found(student_service, mock_repos):
    mock_repos['assignment'].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="Assignment does not exist"):
        student_service.submit_assignment(1, 999)

def test_submit_assignment_grading_success(mock_repos):
    # Setup service with grading dependencies
    sandbox = Mock()
    results = {'score': 0.85, 'results': [{'passed': True}]}
    sandbox.run_all_tests.return_value = results
    
    test_case_repo = Mock()
    test_case_repo.list_by_assignment.return_value = [Mock()]
    
    service = StudentService(
        mock_repos['student'], mock_repos['course'], mock_repos['enrollment'],
        mock_repos['assignment'], mock_repos['submission'],
        sandbox_service=sandbox, test_case_repo=test_case_repo
    )
    
    assignment = Mock()
    assignment.get_course_id.return_value = 101
    assignment.due_date = datetime.now()
    mock_repos['assignment'].get_by_id.return_value = assignment
    mock_repos['enrollment'].get.return_value = Mock()
    mock_repos['submission'].get_last_submission.return_value = None
    
    created_sub = Mock()
    created_sub.language = "python"
    mock_repos['submission'].create.return_value = created_sub
    
    result = service.submit_assignment(1, 5, "print('hi')")
    
    assert created_sub.status == "graded"
    assert created_sub.score == 0.85
    sandbox.run_all_tests.assert_called_once()
    mock_repos['submission'].update.assert_called()

def test_submit_assignment_grading_error(mock_repos):
    sandbox = Mock()
    sandbox.run_all_tests.side_effect = Exception("Crash")
    
    service = StudentService(
        mock_repos['student'], mock_repos['course'], mock_repos['enrollment'],
        mock_repos['assignment'], mock_repos['submission'],
        sandbox_service=sandbox, test_case_repo=Mock()
    )
    
    assignment = Mock()
    assignment.get_course_id.return_value = 101
    assignment.due_date = datetime.now()
    mock_repos['assignment'].get_by_id.return_value = assignment
    mock_repos['enrollment'].get.return_value = Mock()
    mock_repos['submission'].get_last_submission.return_value = None
    
    created_sub = Mock()
    mock_repos['submission'].create.return_value = created_sub
    
    # Logic will print and set status to error
    result = service.submit_assignment(1, 5, "error")
    
    assert created_sub.status == "error"
    mock_repos['submission'].update.assert_called()

def test_calculate_gpa_success(student_service, mock_repos):
    sub1 = Mock()
    sub1.score = 4.0
    sub1.get_assignment_id.return_value = 1
    
    sub2 = Mock()
    sub2.score = 3.0
    sub2.get_assignment_id.return_value = 2
    
    mock_repos['submission'].get_grades.return_value = [sub1, sub2]
    
    course1 = Mock()
    course1.credits = 3
    
    course2 = Mock()
    course2.credits = 4
    
    # We need to simulate get_by_assignment returning different courses
    mock_repos['course'].get_by_assignment.side_effect = [course1, course2]
    
    gpa = student_service.calculate_gpa(1)
    
    # Total points = (4.0*3) + (3.0*4) = 12 + 12 = 24
    # Total credits = 3 + 4 = 7
    # GPA = 24 / 7 = 3.428...
    assert pytest.approx(gpa, 0.01) == 24.0 / 7.0

def test_calculate_gpa_empty(student_service, mock_repos):
    mock_repos['submission'].get_grades.return_value = []
    assert student_service.calculate_gpa(1) == 0.0

def test_calculate_gpa_no_credits(student_service, mock_repos):
    sub = Mock()
    sub.score = 4.0
    mock_repos['submission'].get_grades.return_value = [sub]
    
    course = Mock()
    course.credits = 0 # EDGE CASE
    mock_repos['course'].get_by_assignment.return_value = course
    
    assert student_service.calculate_gpa(1) == 0.0

def test_get_student_submissions(student_service, mock_repos):
    mock_repos['submission'].list_by_student.return_value = [Mock()]
    result = student_service.get_student_submissions(1)
    assert len(result) == 1
    mock_repos['submission'].list_by_student.assert_called_with(1)

def test_submit_assignment_repo_failure(student_service, mock_repos):
    """Test when submission_repo.create returns None"""
    assignment = Mock()
    assignment.due_date = datetime.now()
    assignment.get_course_id.return_value = 1
    mock_repos['assignment'].get_by_id.return_value = assignment
    mock_repos['enrollment'].get.return_value = Mock()
    mock_repos['submission'].get_last_submission.return_value = None
    mock_repos['submission'].create.return_value = None
    
    result = student_service.submit_assignment(1, 5, "code")
    assert result is None

def test_submit_assignment_executes_result_loop(mock_repos):
    """Test that the loop over results executes to cover lines 126-128"""
    sandbox = Mock()
    sandbox.run_all_tests.return_value = {'score': 1.0, 'results': [{'passed': True}, {'passed': False}]}
    
    service = StudentService(
        mock_repos['student'], mock_repos['course'], mock_repos['enrollment'],
        mock_repos['assignment'], mock_repos['submission'],
        sandbox_service=sandbox, test_case_repo=Mock(), result_repo=Mock()
    )
    
    assignment = Mock()
    assignment.due_date = datetime.now()
    assignment.get_course_id.return_value = 1
    mock_repos['assignment'].get_by_id.return_value = assignment
    mock_repos['enrollment'].get.return_value = Mock()
    mock_repos['submission'].get_last_submission.return_value = None
    mock_repos['submission'].create.return_value = Mock()
    service.test_case_repo.list_by_assignment.return_value = [Mock()]
    
    result = service.submit_assignment(1, 5, "code")
    assert result is not None

def test_calculate_gpa_course_not_found(student_service, mock_repos):
    """Test calculate_gpa when a course is not found for an assignment (covers line 149)"""
    sub = Mock()
    sub.score = 4.0
    mock_repos['submission'].get_grades.return_value = [sub]
    mock_repos['course'].get_by_assignment.return_value = None # COVER LINE 149
    
    gpa = student_service.calculate_gpa(1)
    assert gpa == 0.0

