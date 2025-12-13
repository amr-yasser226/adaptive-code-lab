from datetime import datetime
from Backend.Exceptions.AuthError import AuthError
from Backend.Exceptions.ValidationError import ValidationError
from Backend.Model.Enrollment_model import Enrollment
from Backend.Model.Submission_model import Submission

class StudentService:
    def __init__(self, student_repo, course_repo, enrollment_repo, assignment_repo, submission_repo):
        self.student_repo = student_repo
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo
        self.assignment_repo = assignment_repo
        self.submission_repo = submission_repo

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


        last_submission = self.submission_repo.get_laste_submission(student_id, assignment_id)
        new_version = last_submission.version + 1 if last_submission else 1

        is_late = datetime.now() > assignment.dueDate

        new_submission = Submission(
            id=None,
            assignment_id=assignment_id,
            student_id=student_id,
            version=new_version,
            language="python",
            status="pending",
            score=0.0,
            is_late=is_late,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            grade_at=None
        )

        return self.submission_repo.create(new_submission)


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
