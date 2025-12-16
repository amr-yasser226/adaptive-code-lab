from datetime import datetime
from core.entities.submission import Submission
from core.entities.file import File
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


class SubmissionService:
    def __init__(
        self,
        submission_repo,
        assignment_repo,
        enrollment_repo,
        file_repo
    ):
        self.submission_repo = submission_repo
        self.assignment_repo = assignment_repo
        self.enrollment_repo = enrollment_repo
        self.file_repo = file_repo

    # --------------------------------------------------
    # CREATE SUBMISSION
    # --------------------------------------------------
    def submit(self, student, assignment_id, language):
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValidationError("Assignment not found")

        enrollment = self.enrollment_repo.get(student.get_id(), assignment.get_course_id())
        if not enrollment or enrollment.status != "enrolled":
            raise AuthError("Student not enrolled in course")

        last = self.submission_repo.get_last_submission(student.get_id(), assignment_id)
        version = (last.version + 1) if last else 1

        submission = Submission(
            id=None,
            assignment_id=assignment_id,
            student_id=student.get_id(),
            version=version,
            language=language,
            status="pending",
            score=None,
            is_late=datetime.utcnow() > assignment.due_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            grade_at=None
        )

        return self.submission_repo.create(submission)

    # --------------------------------------------------
    # ATTACH FILE
    # --------------------------------------------------
    def attach_file(self, submission_id, uploader_id, **file_data):
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValidationError("Submission not found")

        file = File(
            id=None,
            submission_id=submission_id,
            uploader_id=uploader_id,
            created_at=datetime.utcnow(),
            **file_data
        )

        return self.file_repo.save_file(file)

    # --------------------------------------------------
    # QUEUE FOR GRADING
    # --------------------------------------------------
    def enqueue_for_grading(self, submission_id):
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValidationError("Submission not found")

        submission.status = "queued"
        return self.submission_repo.update(submission)

    # --------------------------------------------------
    # RE-GRADE
    # --------------------------------------------------
    def regrade(self, submission_id):
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValidationError("Submission not found")

        submission.status = "queued"
        submission.score = None
        submission.grade_at = None

        return self.submission_repo.update(submission)

    # --------------------------------------------------
    # READ OPERATIONS
    # --------------------------------------------------
    def list_by_assignment(self, assignment_id):
        return self.submission_repo.list_by_assignment(assignment_id)

    def list_by_student(self, student_id):
        return self.submission_repo.list_by_student(student_id)
