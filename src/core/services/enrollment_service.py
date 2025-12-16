from datetime import datetime
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError
from core.entities.enrollment import Enrollment


class EnrollmentService:
    def __init__(self, enrollment_repo, course_repo):
        self.enrollment_repo = enrollment_repo
        self.course_repo = course_repo

    # --------------------------------------------------
    # ENROLL STUDENT
    # --------------------------------------------------
    def enroll_student(self, student, course_id):
        if student.role != "student":
            raise AuthError("Only students can enroll")

        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise ValidationError("Course not found")

        if course.status != "active":
            raise ValidationError("Course is not active")

        existing = self.enrollment_repo.get(student.get_id(), course_id)
        if existing and existing.status == "enrolled":
            raise ValidationError("Already enrolled")

        enrollment = Enrollment(
            student_id=student.get_id(),
            course_id=course_id,
            status="enrolled",
            enrolled_at=datetime.utcnow(),
            dropped_at=None,
            final_grade=None
        )

        return self.enrollment_repo.enroll(enrollment)

    # --------------------------------------------------
    # DROP COURSE
    # --------------------------------------------------
    def drop_course(self, student, course_id):
        enrollment = self.enrollment_repo.get(student.get_id(), course_id)
        if not enrollment:
            raise ValidationError("Enrollment not found")

        if enrollment.status != "enrolled":
            raise ValidationError("Cannot drop this enrollment")

        enrollment.status = "dropped"
        enrollment.dropped_at = datetime.utcnow()

        return self.enrollment_repo.update(enrollment)

    # --------------------------------------------------
    # COMPLETE COURSE (INSTRUCTOR / SYSTEM)
    # --------------------------------------------------
    def complete_course(self, enrollment, final_grade):
        enrollment.status = "completed"
        enrollment.final_grade = final_grade

        return self.enrollment_repo.update(enrollment)

    # --------------------------------------------------
    # READ OPERATIONS
    # --------------------------------------------------
    def list_by_student(self, student_id):
        return self.enrollment_repo.list_by_student(student_id)

    def list_by_course(self, course_id):
        return self.enrollment_repo.list_by_course(course_id)
