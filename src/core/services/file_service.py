from datetime import datetime
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError
from core.entities.file import File


class FileService:
    def __init__(self, file_repo, submission_repo):
        self.file_repo = file_repo
        self.submission_repo = submission_repo

    # -------------------------------------------------
    # UPLOAD FILE
    # -------------------------------------------------
    def upload_file(
        self,
        user,
        submission_id,
        path,
        file_name,
        content_type,
        size_bytes,
        checksum,
        storage_url
    ):
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValidationError("Submission not found")

        # permission: owner or instructor/admin
        if user.role == "student":
            if submission.get_student_id() != user.get_id():
                raise AuthError("You cannot upload files to this submission")

        file = File(
            id=None,
            submission_id=submission_id,
            uploader_id=user.get_id(),
            path=path,
            file_name=file_name,
            content_type=content_type,
            size_bytes=size_bytes,
            check_sum=checksum,
            storage_url=storage_url,
            created_at=datetime.now()
        )

        self._validate_file(file)

        return self.file_repo.save_file(file)

    # -------------------------------------------------
    # DELETE FILE
    # -------------------------------------------------
    def delete_file(self, user, file_id):
        file = self.file_repo.get_by_id(file_id)
        if not file:
            raise ValidationError("File not found")

        if user.role == "student" and file.uploader_id != user.get_id():
            raise AuthError("You cannot delete this file")

        self.file_repo.delete(file_id)
        return True

    # -------------------------------------------------
    # LIST FILES BY SUBMISSION
    # -------------------------------------------------
    def list_files(self, user, submission_id):
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValidationError("Submission not found")

        if user.role == "student":
            if submission.get_student_id() != user.get_id():
                raise AuthError("You cannot view these files")

        return self.file_repo.find_by_submission(submission_id)

    # -------------------------------------------------
    # INTERNAL VALIDATION
    # -------------------------------------------------
    def _validate_file(self, file: File):
        if file.size_bytes <= 0:
            raise ValidationError("Invalid file size")

        if not file.file_name:
            raise ValidationError("File name is required")

        if not file.content_type:
            raise ValidationError("Content type is required")
