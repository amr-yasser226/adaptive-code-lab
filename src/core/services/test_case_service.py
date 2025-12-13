from datetime import datetime
from core.entities.test_case import Testcase
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError


class TestCaseService:
    def __init__(
        self,
        testcase_repo,
        assignment_repo,
        course_repo
    ):
        self.testcase_repo = testcase_repo
        self.assignment_repo = assignment_repo
        self.course_repo = course_repo


    def _verify_instructor_owns_assignment(self, instructor_id, assignment):
        course = self.course_repo.get_by_id(assignment.get_course_id())
        if not course:
            raise ValidationError("Course not found")

        if course.get_instructor_id() != instructor_id:
            raise AuthError("You do not own this course")

    def create_test_case(
        self,
        instructor,
        assignment_id,
        name,
        stdin,
        expected_out,
        points,
        description=None,
        timeout_ms=None,
        memory_limit_mb=None,
        is_visible=False,
        sort_order=0
    ):
        if instructor.role != "instructor":
            raise AuthError("Only instructors can create test cases")

        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValidationError("Assignment not found")

        self._verify_instructor_owns_assignment(
            instructor.get_id(), assignment
        )

        if points <= 0:
            raise ValidationError("Points must be greater than zero")

        testcase = Testcase(
            id=None,
            assignment_id=assignment_id,
            name=name,
            stdin=stdin,
            descripion=description,
            expected_out=expected_out,
            timeout_ms=timeout_ms,
            memory_limit_mb=memory_limit_mb,
            points=points,
            is_visible=is_visible,
            sort_order=sort_order,
            created_at=datetime.now()
        )

        return self.testcase_repo.create(testcase)

    def update_test_case(self, instructor, testcase_id, **fields):
        testcase = self.testcase_repo.get_by_id(testcase_id)
        if not testcase:
            raise ValidationError("Test case not found")

        assignment = self.assignment_repo.get_by_id(
            testcase.get_assignment_id()
        )
        if not assignment:
            raise ValidationError("Assignment not found")

        self._verify_instructor_owns_assignment(
            instructor.get_id(), assignment
        )

        # Update allowed fields only
        for field in [
            "name", "stdin", "descripion", "expected_out",
            "timeout_ms", "memory_limit_mb",
            "points", "is_visible", "sort_order"
        ]:
            if field in fields:
                setattr(testcase, field, fields[field])

        if testcase.points <= 0:
            raise ValidationError("Points must be greater than zero")

        return self.testcase_repo.update(testcase)

    def delete_test_case(self, instructor, testcase_id):
        testcase = self.testcase_repo.get_by_id(testcase_id)
        if not testcase:
            raise ValidationError("Test case not found")

        assignment = self.assignment_repo.get_by_id(
            testcase.get_assignment_id()
        )
        if not assignment:
            raise ValidationError("Assignment not found")

        self._verify_instructor_owns_assignment(
            instructor.get_id(), assignment
        )

        return self.testcase_repo.delete(testcase_id)

    def list_test_cases(self, user, assignment_id):
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValidationError("Assignment not found")

        testcases = self.testcase_repo.list_by_assignment(assignment_id)

        # Students see only visible test cases
        if user.role == "student":
            return [tc for tc in testcases if tc.is_visible]

        # Instructor / Admin see all
        return testcases
