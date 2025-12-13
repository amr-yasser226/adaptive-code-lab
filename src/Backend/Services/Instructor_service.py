from datetime import datetime
from Backend.Exceptions.ValidationError import ValidationError
from Backend.Exceptions.AuthError import AuthError
from Backend.Model.Course_model import Course
from Backend.Model.Assignment_model import Assignment


class InstructorService:
    def __init__(self, instructor_repo, course_repo, assignment_repo, enrollment_repo, submission_repo, flag_repo):
        self.instructor_repo = instructor_repo
        self.course_repo = course_repo
        self.assignment_repo = assignment_repo
        self.enrollment_repo = enrollment_repo
        self.submission_repo = submission_repo
        self.flag_repo = flag_repo


    def get_instructor(self, instructor_id):
        instructor = self.instructor_repo.get_by_id(instructor_id)
        if not instructor:
            raise ValidationError("Instructor not found")
        return instructor


    def create_course(self, instructor_id, code, title, description, year, semester, max_students, credits):
        instructor = self.get_instructor(instructor_id)


        new_course = Course(
            id=None,
            instructor_id=instructor.get_id(),
            code=code,
            title=title,
            describtion=description,
            year=year,
            semester=semester,
            max_students=max_students,
            created_at=datetime.now(),
            status="inactive",     # by system rule: new courses are inactive
            updated_at=datetime.now(),
            credits=credits
        )

        # Save using repo
        return self.course_repo.create(new_course)

    def create_assignment(
        self,
        instructor_id,
        course_id,
        title,
        description,
        release_date,
        due_date,
        max_points,
        allow_late_submissions=False,
        late_submission_penalty=0
    ):
        instructor = self.get_instructor(instructor_id)

        
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise ValidationError("Course not found")

        if course.get_instructor_id() != instructor.get_id():
            raise AuthError("You can only create assignments for your own courses", code="not_owner")

 
        new_assignment = Assignment(
            id=None,
            course_id=course_id,
            title=title,
            describtion=description,
            releaseDate=release_date,
            due_date=due_date,
            max_points=max_points,
            is_published=False,   # new assignments default to unpublished
            allow_late_submissions=allow_late_submissions,
            late_submission_penalty=late_submission_penalty,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )


        return self.assignment_repo.create(new_assignment)

 
    def export_grades(self, instructor_id, course_id):
        instructor = self.get_instructor(instructor_id)


        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise ValidationError("Course not found")


        if course.get_instructor_id() != instructor.get_id():
            raise AuthError("You can only export grades for your own courses", code="not_owner")


        enrollments = self.enrollment_repo.list_by_course(course_id)

        grades_data = []
        for e in enrollments:
            grades_data.append({
                "student_id": e.get_student_id(),
                "status": e.status,
                "final_grade": e.final_grade,
                "enrolled_at": e.enrolled_at,
                "dropped_at": e.dropped_at
            })

        return grades_data


    def list_instructor_courses(self, instructor_id):
        instructor = self.get_instructor(instructor_id)
        return self.course_repo.list_by_instructor(instructor.get_id())



    def review_similarity(self, instructor_id, flag_id, action, notes=None):
        """
        action must be: 'approve', 'dismiss', or 'escalate'
        """

        # -----------------------------------------
        # 1. Verify instructor exists
        # -----------------------------------------
        instructor = self.get_instructor(instructor_id)

        # -----------------------------------------
        # 2. Load similarity flag
        # -----------------------------------------
        flag = self.flag_repo.get_by_id(flag_id)
        if not flag:
            raise ValidationError("Similarity flag not found")

        # -----------------------------------------
        # 3. Load submission
        # -----------------------------------------
        submission = self.submission_repo.get_by_id(flag.get_submission_id())
        if not submission:
            raise ValidationError("Submission not found for this similarity flag")

        # -----------------------------------------
        # 4. Load assignment
        # -----------------------------------------
        assignment = self.assignment_repo.get_by_id(submission.get_assignment_id())
        if not assignment:
            raise ValidationError("Assignment not found for the submission")

        # -----------------------------------------
        # 5. Load course and check instructor ownership
        # -----------------------------------------
        course = self.course_repo.get_by_id(assignment.get_course_id())
        if not course:
            raise ValidationError("Course not found for the assignment")

        if course.get_instructor_id() != instructor.get_id():
            raise AuthError(
                "You are not allowed to review similarity flags for this course",
                code="not_owner"
            )

        # -----------------------------------------
        # 6. Apply action
        # -----------------------------------------
        now = datetime.now()

        if action == "approve":
            updated_flag = self.flag_repo.mark_reviewed(
                id=flag_id,
                reviewer_id=instructor_id,
                review_notes=notes,
                reviewed_at=now
            )

        elif action == "dismiss":
            updated_flag = self.flag_repo.dismiss(
                id=flag_id,
                reviewer_id=instructor_id,
                reviewed_at=now
            )

        elif action == "escalate":
            updated_flag = self.flag_repo.escalate(
                id=flag_id,
                reviewer_id=instructor_id,
                reviewed_at=now
            )

        else:
            raise ValidationError(
                "Invalid action. Must be one of: approve, dismiss, escalate"
            )

        return updated_flag

