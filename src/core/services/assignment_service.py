from datetime import datetime
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError
from core.entities.assignment import Assignment

class AssignmentService:
    def __init__(
        self,
        assignment_repo,
        course_repo,
        submission_repo
    ):
        self.assignment_repo = assignment_repo
        self.course_repo = course_repo
        self.submission_repo = submission_repo


    def _verify_instructor_owns_course(self, instructor_id, course_id):
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise ValidationError("Course not found")

        if course.get_instructor_id() != instructor_id:
            raise AuthError("You do not own this course")

        return course

    
    def create_assignment(
        self,
        instructor,
        course_id,
        title,
        description,
        release_date,
        due_date,
        max_points,
        allow_late_submissions=False,
        late_submission_penalty=None,
        is_published=True
    ):
        if instructor.role != "instructor":
            raise AuthError("Only instructors can create assignments")

        course = self._verify_instructor_owns_course(
            instructor.get_id(), course_id
        )

        if course.status != "active":
            raise ValidationError("Cannot add assignment to inactive course")

        assignment = Assignment(
            id=None,
            course_id=course_id,
            title=title,
            description=description,
            release_date=release_date,
            due_date=due_date,
            max_points=max_points,
            is_published=is_published,
            allow_late_submissions=allow_late_submissions,
            late_submission_penalty=late_submission_penalty,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        return self.assignment_repo.create(assignment)

    def publish_assignment(self, instructor, assignment_id):
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValidationError("Assignment not found")

        self._verify_instructor_owns_course(
            instructor.get_id(), assignment.get_course_id()
        )

        return self.assignment_repo.publish(assignment_id)


    def unpublish_assignment(self, instructor, assignment_id):
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValidationError("Assignment not found")

        self._verify_instructor_owns_course(
            instructor.get_id(), assignment.get_course_id()
        )

        return self.assignment_repo.unpublish(assignment_id)

    def extend_deadline(self, instructor, assignment_id, new_due_date):
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValidationError("Assignment not found")

        self._verify_instructor_owns_course(
            instructor.get_id(), assignment.get_course_id()
        )

        if new_due_date <= assignment.release_date:
            raise ValidationError("Due date must be after release date")

        return self.assignment_repo.extend_deadline(
            assignment_id, new_due_date
        )

    def list_assignments_for_course(self, user, course_id):
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise ValidationError("Course not found")

        # Students can only see published assignments
        assignments = self.assignment_repo.list_by_course(course_id)

        if user.role == "student":
            return [a for a in assignments if a.is_published]

        # Instructor / Admin sees all
        return assignments


    def get_submissions(self, instructor, assignment_id):
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValidationError("Assignment not found")

        self._verify_instructor_owns_course(
            instructor.get_id(), assignment.get_course_id()
        )

        return self.submission_repo.list_by_assignment(assignment_id)


    def calculate_statistics(self, instructor, assignment_id):
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValidationError("Assignment not found")

        self._verify_instructor_owns_course(
            instructor.get_id(), assignment.get_course_id()
        )

        submissions = self.submission_repo.list_by_assignment(assignment_id)

        scores = [s.score for s in submissions if s.score is not None]

        if not scores:
            return {
                "count": 0,
                "average": 0,
                "min": 0,
                "max": 0
            }

        return {
            "count": len(scores),
            "average": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores)
        }



    