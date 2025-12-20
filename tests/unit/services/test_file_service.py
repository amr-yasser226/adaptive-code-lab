import pytest
from unittest.mock import Mock
from core.services.file_service import FileService
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_file_repo():
    return Mock()


@pytest.fixture
def mock_submission_repo():
    return Mock()


@pytest.fixture
def file_service(mock_file_repo, mock_submission_repo):
    return FileService(mock_file_repo, mock_submission_repo)


@pytest.fixture
def student_user():
    user = Mock()
    user.role = "student"
    user.get_id.return_value = 1
    return user


@pytest.fixture
def instructor_user():
    user = Mock()
    user.role = "instructor"
    user.get_id.return_value = 2
    return user


class TestFileService:
    """Test suite for FileService"""

    def test_upload_file_success_as_owner(self, file_service, student_user, 
                                           mock_submission_repo, mock_file_repo):
        """Test successful file upload by submission owner"""
        submission = Mock()
        submission.get_student_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission
        mock_file_repo.save_file.return_value = Mock()

        result = file_service.upload_file(
            user=student_user,
            submission_id=1,
            path="/submissions/1/",
            file_name="solution.py",
            content_type="text/x-python",
            size_bytes=1024,
            checksum="abc123",
            storage_url="/storage/solution.py"
        )

        mock_file_repo.save_file.assert_called_once()

    def test_upload_file_as_instructor(self, file_service, instructor_user, 
                                        mock_submission_repo, mock_file_repo):
        """Instructors can upload files to any submission"""
        submission = Mock()
        submission.get_student_id.return_value = 999  # Not the instructor
        mock_submission_repo.get_by_id.return_value = submission
        mock_file_repo.save_file.return_value = Mock()

        result = file_service.upload_file(
            user=instructor_user,
            submission_id=1,
            path="/submissions/1/",
            file_name="feedback.txt",
            content_type="text/plain",
            size_bytes=512,
            checksum="abc123",
            storage_url="/storage/feedback.txt"
        )

        mock_file_repo.save_file.assert_called_once()

    def test_upload_file_submission_not_found(self, file_service, student_user, mock_submission_repo):
        """Submission not found raises ValidationError"""
        mock_submission_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Submission not found"):
            file_service.upload_file(
                user=student_user,
                submission_id=999,
                path="/submissions/1/",
                file_name="solution.py",
                content_type="text/x-python",
                size_bytes=1024,
                checksum="abc123",
                storage_url="/storage/solution.py"
            )

    def test_upload_file_not_owner_denied(self, file_service, student_user, mock_submission_repo):
        """Students cannot upload to others' submissions"""
        submission = Mock()
        submission.get_student_id.return_value = 999  # Different student
        mock_submission_repo.get_by_id.return_value = submission

        with pytest.raises(AuthError, match="You cannot upload files to this submission"):
            file_service.upload_file(
                user=student_user,
                submission_id=1,
                path="/submissions/1/",
                file_name="solution.py",
                content_type="text/x-python",
                size_bytes=1024,
                checksum="abc123",
                storage_url="/storage/solution.py"
            )

    def test_upload_file_invalid_size(self, file_service, student_user, mock_submission_repo):
        """Invalid file size raises ValidationError"""
        submission = Mock()
        submission.get_student_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission

        with pytest.raises(ValidationError, match="Invalid file size"):
            file_service.upload_file(
                user=student_user,
                submission_id=1,
                path="/submissions/1/",
                file_name="solution.py",
                content_type="text/x-python",
                size_bytes=0,
                checksum="abc123",
                storage_url="/storage/solution.py"
            )

    def test_upload_file_missing_filename(self, file_service, student_user, mock_submission_repo):
        """Missing file name raises ValidationError"""
        submission = Mock()
        submission.get_student_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission

        with pytest.raises(ValidationError, match="File name is required"):
            file_service.upload_file(
                user=student_user,
                submission_id=1,
                path="/submissions/1/",
                file_name="",
                content_type="text/x-python",
                size_bytes=1024,
                checksum="abc123",
                storage_url="/storage/solution.py"
            )

    def test_delete_file_success(self, file_service, student_user, mock_file_repo):
        """Test successful file deletion by owner"""
        file = Mock()
        file.uploader_id = 1
        mock_file_repo.get_by_id.return_value = file

        result = file_service.delete_file(student_user, 1)

        mock_file_repo.delete.assert_called_once_with(1)
        assert result is True

    def test_delete_file_not_found(self, file_service, student_user, mock_file_repo):
        """File not found raises ValidationError"""
        mock_file_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="File not found"):
            file_service.delete_file(student_user, 999)

    def test_delete_file_not_owner_denied(self, file_service, student_user, mock_file_repo):
        """Students cannot delete others' files"""
        file = Mock()
        file.uploader_id = 999  # Different user
        mock_file_repo.get_by_id.return_value = file

        with pytest.raises(AuthError, match="You cannot delete this file"):
            file_service.delete_file(student_user, 1)

    def test_list_files_success(self, file_service, student_user, 
                                 mock_submission_repo, mock_file_repo):
        """Test listing files for a submission"""
        submission = Mock()
        submission.get_student_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission
        files = [Mock(), Mock()]
        mock_file_repo.find_by_submission.return_value = files

        result = file_service.list_files(student_user, 1)

        assert result == files

    def test_list_files_not_owner_denied(self, file_service, student_user, mock_submission_repo):
        """Students cannot view others' files"""
        submission = Mock()
        submission.get_student_id.return_value = 999
        mock_submission_repo.get_by_id.return_value = submission

        with pytest.raises(AuthError, match="You cannot view these files"):
            file_service.list_files(student_user, 1)

    def test_list_files_submission_not_found(self, file_service, student_user, mock_submission_repo):
        """Line 72: ValidationError when submission not found in list_files"""
        mock_submission_repo.get_by_id.return_value = None
        with pytest.raises(ValidationError, match="Submission not found"):
            file_service.list_files(student_user, 999)

    def test_upload_file_missing_content_type(self, file_service, student_user, mock_submission_repo):
        """Line 91: ValidationError when content_type is missing"""
        submission = Mock()
        submission.get_student_id.return_value = 1
        mock_submission_repo.get_by_id.return_value = submission
        with pytest.raises(ValidationError, match="Content type is required"):
            file_service.upload_file(
                user=student_user,
                submission_id=1,
                path="/",
                file_name="test.txt",
                content_type="",
                size_bytes=100,
                checksum="abc",
                storage_url="url"
            )
