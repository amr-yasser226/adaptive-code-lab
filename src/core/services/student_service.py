from datetime import datetime
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError
from core.entities.enrollment import Enrollment
from core.entities.submission import Submission

class StudentService:
    def __init__(self, student_repo, course_repo, enrollment_repo, assignment_repo, submission_repo, sandbox_service=None, test_case_repo=None, result_repo=None):
        self.student_repo = student_repo
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo
        self.assignment_repo = assignment_repo
        self.submission_repo = submission_repo
        self.sandbox_service = sandbox_service
        self.test_case_repo = test_case_repo
        self.result_repo = result_repo

    def get_student(self, student_id):
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise ValidationError("Student not found")
        return student


    def enroll_course(self, student_id, course_id):
        student = self.get_student(student_id)

     
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise ValidationError("Course does not exist")

        
        existing = self.enrollment_repo.get(student_id, course_id)
        if existing:
            raise ValidationError("Student already enrolled in this course")


        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            status="enrolled",
            final_grade=None,
            enrolled_at=datetime.now(),
            dropped_at=None
        )

        return self.enrollment_repo.enroll(enrollment)

 
    def drop_course(self, student_id, course_id):
        enrollment = self.enrollment_repo.get(student_id, course_id)
        
        if not enrollment:
            raise ValidationError("Student is not enrolled in this course")

        enrollment.status = "dropped"
        enrollment.dropped_at = datetime.now()

        return self.enrollment_repo.update(enrollment)


    def submit_assignment(self, student_id, assignment_id, submission_text=""):

        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise ValidationError("Assignment does not exist")


        enrollment = self.enrollment_repo.get(student_id, assignment.get_course_id())
        if not enrollment:
            raise AuthError("You cannot submit — you are not enrolled in this course", code="not_enrolled")


        last_submission = self.submission_repo.get_last_submission(student_id, assignment_id)
        new_version = last_submission.version + 1 if last_submission else 1

        # Handle potential string from SQLite
        due_date = assignment.due_date
        if isinstance(due_date, str):
            try:
                # Remove Z if present and parse
                due_date = datetime.fromisoformat(due_date.replace('Z', ''))
            except (ValueError, AttributeError):
                # Fallback to current time if unparseable (should not happen with valid DB)
                due_date = datetime.now()
        
        is_late = datetime.now() > due_date

        new_submission = Submission(
            id=None,
            assignment_id=assignment_id,
            student_id=student_id,
            version=new_version,
            language="python",
            status="pending",
            score=0.0,
            content=submission_text,
            file_id=None,
            is_late=is_late,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            grade_at=None
        )

        created = self.submission_repo.create(new_submission)
        if not created:
            return None

        # FR-05: Automated Grading Trigger
        if hasattr(self, 'sandbox_service') and self.sandbox_service:
            try:
                # We need test cases to grade
                if hasattr(self, 'test_case_repo'):
                    test_cases = self.test_case_repo.list_by_assignment(assignment_id)
                    if test_cases:
                        # Update status to running
                        created.status = "running"
                        self.submission_repo.update(created)

                        # Run tests
                        results = self.sandbox_service.run_all_tests(
                            submission_text,
                            test_cases,
                            created.language
                        )

                        # Update submission with results
                        created.status = "graded"
                        created.score = results.get('score', 0.0)
                        created.grade_at = datetime.now()
                        self.submission_repo.update(created)

                        # Save individual results via result_repo if available
                        if hasattr(self, 'result_repo') and self.result_repo:
                            for res in results.get('results', []):
                                # In a real implementation, we'd save Result entities here
                                pass
            except Exception as e:
                created.status = "error"
                self.submission_repo.update(created)
                # Log error
                print(f"Grading error: {e}")

        return created


    def calculate_gpa(self, student_id):
        submissions = self.submission_repo.get_grades(student_id)
        if not submissions:
            return 0.0

        total_points = 0.0
        total_credits = 0

        for sub in submissions:
            course = self.course_repo.get_by_assignment(sub.get_assignment_id())
            if not course:
                continue

            total_points += sub.score * course.credits
            total_credits += course.credits

        if total_credits == 0:
            return 0.0

        return total_points / total_credits


    def get_student_submissions(self, student_id):
        return self.submission_repo.list_by_student(student_id)
