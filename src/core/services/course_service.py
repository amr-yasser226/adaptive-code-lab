from core.exceptions.validation_error import ValidationError

class CourseService:
    def __init__(self, course_repo, assignment_repo, enrollment_repo):
        self.course_repo = course_repo
        self.assignment_repo = assignment_repo
        self.enrollment_repo = enrollment_repo

    def get_course(self, course_id):
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise ValidationError("Course not found")
        return course

    def publish_course(self, course_id):
        return self.course_repo.publish(course_id)

    def archive_course(self, course_id):
        return self.course_repo.archive(course_id)

    def list_assignments(self, course_id):
        return self.assignment_repo.list_by_course(course_id)

    def get_enrolled_students(self, course_id):
        enrollments = self.enrollment_repo.list_by_course(course_id)
        return [e for e in enrollments if e.status == "enrolled"]
