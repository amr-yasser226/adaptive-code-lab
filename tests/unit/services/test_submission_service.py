import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from core.services.submission_service import SubmissionService
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_submission_repo():
    return Mock()


@pytest.fixture
def mock_assignment_repo():
    return Mock()


@pytest.fixture
def mock_enrollment_repo():
    return Mock()


@pytest.fixture
def mock_file_repo():
    return Mock()


@pytest.fixture
def submission_service(mock_submission_repo, mock_assignment_repo, 
                       mock_enrollment_repo, mock_file_repo):
    return SubmissionService(
        submission_repo=mock_submission_repo,
        assignment_repo=mock_assignment_repo,
        enrollment_repo=mock_enrollment_repo,
        file_repo=mock_file_repo
    )


@pytest.fixture
def student_user():
    user = Mock()
    user.get_id.return_value = 1
    return user


class TestSubmissionService:
    """Test suite for SubmissionService"""

    def test_submit_success(self, submission_service, student_user,
                            mock_assignment_repo, mock_enrollment_repo,
                            mock_submission_repo):
        """Test successful submission creation"""
        assignment = Mock()
        assignment.get_course_id.return_value = 1
        assignment.due_date = datetime.utcnow() + timedelta(days=1)  # Future date
        mock_assignment_repo.get_by_id.return_value = assignment

        enrollment = Mock()
        enrollment.status = "enrolled"
        mock_enrollment_repo.get.return_value = enrollment

        mock_submission_repo.get_last_submission.return_value = None
        mock_submission_repo.create.return_value = Mock()

        result = submission_service.submit(student_user, 1, "python")

        mock_submission_repo.create.assert_called_once()

    def test_submit_first_version(self, submission_service, student_user,
                                   mock_assignment_repo, mock_enrollment_repo,
                                   mock_submission_repo):
        """First submission should have version 1"""
        assignment = Mock()
        assignment.get_course_id.return_value = 1
        assignment.due_date = datetime.utcnow() + timedelta(days=1)  # Future date
        mock_assignment_repo.get_by_id.return_value = assignment

        enrollment = Mock()
        enrollment.status = "enrolled"
        mock_enrollment_repo.get.return_value = enrollment

        mock_submission_repo.get_last_submission.return_value = None
        mock_submission_repo.create.return_value = Mock()

        submission_service.submit(student_user, 1, "python")

        args, _ = mock_submission_repo.create.call_args
        assert args[0].version == 1

    def test_submit_increments_version(self, submission_service, student_user,
                                        mock_assignment_repo, mock_enrollment_repo,
                                        mock_submission_repo):
        """Subsequent submission should increment version"""
        assignment = Mock()
        assignment.get_course_id.return_value = 1
        assignment.due_date = datetime.utcnow() + timedelta(days=1)  # Future date
        mock_assignment_repo.get_by_id.return_value = assignment

        enrollment = Mock()
        enrollment.status = "enrolled"
        mock_enrollment_repo.get.return_value = enrollment

        last_submission = Mock()
        last_submission.version = 2
        mock_submission_repo.get_last_submission.return_value = last_submission
        mock_submission_repo.create.return_value = Mock()

        submission_service.submit(student_user, 1, "python")

        args, _ = mock_submission_repo.create.call_args
        assert args[0].version == 3

    def test_submit_assignment_not_found(self, submission_service, student_user,
                                          mock_assignment_repo):
        """Assignment not found raises ValidationError"""
        mock_assignment_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Assignment not found"):
            submission_service.submit(student_user, 999, "python")

    def test_submit_not_enrolled(self, submission_service, student_user,
                                  mock_assignment_repo, mock_enrollment_repo):
        """Student not enrolled raises AuthError"""
        assignment = Mock()
        assignment.get_course_id.return_value = 1
        mock_assignment_repo.get_by_id.return_value = assignment

        mock_enrollment_repo.get.return_value = None

        with pytest.raises(AuthError, match="Student not enrolled in course"):
            submission_service.submit(student_user, 1, "python")

    def test_attach_file_success(self, submission_service, mock_submission_repo, mock_file_repo):
        """Test successful file attachment"""
        mock_submission_repo.get_by_id.return_value = Mock()
        mock_file_repo.save_file.return_value = Mock()

        result = submission_service.attach_file(
            submission_id=1,
            uploader_id=1,
            path="/files/",
            file_name="solution.py",
            content_type="text/python",
            size_bytes=1024,
            check_sum="abc123",
            storage_url="/storage/solution.py"
        )

        mock_file_repo.save_file.assert_called_once()

    def test_attach_file_submission_not_found(self, submission_service, mock_submission_repo):
        """Submission not found raises ValidationError"""
        mock_submission_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Submission not found"):
            submission_service.attach_file(1, 1)

    def test_enqueue_for_grading(self, submission_service, mock_submission_repo):
        """Test enqueue for grading"""
        submission = Mock()
        mock_submission_repo.get_by_id.return_value = submission
        mock_submission_repo.update.return_value = submission

        result = submission_service.enqueue_for_grading(1)

        assert submission.status == "queued"
        assert submission.status == "queued"
        mock_submission_repo.update.assert_called_once()

    def test_enqueue_for_grading_not_found(self, submission_service, mock_submission_repo):
        """Test enqueue for grading raises ValidationError when submission not found"""
        mock_submission_repo.get_by_id.return_value = None
        with pytest.raises(ValidationError, match="Submission not found"):
            submission_service.enqueue_for_grading(999)

    def test_regrade(self, submission_service, mock_submission_repo):
        """Test regrade submission"""
        submission = Mock()
        mock_submission_repo.get_by_id.return_value = submission
        mock_submission_repo.update.return_value = submission

        result = submission_service.regrade(1)

        assert submission.status == "queued"
        assert submission.score is None
        assert submission.status == "queued"
        assert submission.score is None
        assert submission.grade_at is None

    def test_regrade_not_found(self, submission_service, mock_submission_repo):
        """Test regrade raises ValidationError when submission not found"""
        mock_submission_repo.get_by_id.return_value = None
        with pytest.raises(ValidationError, match="Submission not found"):
            submission_service.regrade(999)

    def test_list_by_assignment(self, submission_service, mock_submission_repo):
        """Test listing submissions by assignment"""
        submissions = [Mock(), Mock()]
        mock_submission_repo.list_by_assignment.return_value = submissions

        result = submission_service.list_by_assignment(1)

        mock_submission_repo.list_by_assignment.assert_called_once_with(1)
        assert result == submissions

    def test_list_by_student(self, submission_service, mock_submission_repo):
        """Test listing submissions by student"""
        submissions = [Mock(), Mock()]
        mock_submission_repo.list_by_student.return_value = submissions

        result = submission_service.list_by_student(1)

        mock_submission_repo.list_by_student.assert_called_once_with(1)
        assert result == submissions
