from datetime import datetime
from core.entities.user import User
from core.entities.enrollment import Enrollment
from core.entities.submission import Submission


class Student(User):
    def __init__(self, id, name, email, password, created_at, updated_at, 
                 student_number, Program, year_Level, is_active=True):
        super().__init__(
            id=id, 
            name=name, 
            email=email, 
            password=password, 
            role="student", 
            created_at=created_at, 
            updated_at=updated_at, 
            is_active=is_active
        )
        self.student_number = student_number
        self.program = Program
        self.year_Level = year_Level
    
    def Enroll_course(self, course_id, Course_repo, Enrollment_repo):
        # Verify course exists
        course = Course_repo.get_by_id(course_id)
        if not course:
            raise Exception("Course does not exist")
        
        # Check if already enrolled
        existing_enrollment = Enrollment_repo.get(self.get_id(), course_id)
        if existing_enrollment:
            raise Exception("Student is already enrolled in this course")
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=self.get_id(),
            course_id=course_id,
            status="enrolled",
            final_grade=None,
            enrolled_at=datetime.now(),
            dropped_at=None
        )
        
        return Enrollment_repo.enroll(enrollment)
    
    def Submit_assignment(self, assignment_id, submission_text, 
                         Assignment_repo, Submission_repo, Enrollment_repo):

        # Verify assignment exists
        assignment = Assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise Exception("Assignment does not exist")
        
        # Verify student is enrolled in the course
        enrollment = Enrollment_repo.get(self.get_id(), assignment.get_course_id())
        if not enrollment:
            raise Exception("You cannot submit. You are not enrolled in this course.")
        
        # Determine version number
        last_submission = Submission_repo.get_laste_submission(
            self.get_id(), 
            assignment_id
        )
        new_version = last_submission.version + 1 if last_submission else 1
        
        # Check if late
        is_late = datetime.now() > assignment.dueDate
        
        # Create submission
        new_submission = Submission(
            id=None,
            assignment_id=assignment_id,
            student_id=self.get_id(),
            version=new_version,
            language="python",
            status="pending",
            score=0.0,
            is_late=is_late,
            created_at=None,
            updated_at=None,
            grade_at=None
        )
        
        return Submission_repo.create(new_submission)
    
    def View_GPA(self, Submission_repo, Course_repo):
        submissions = Submission_repo.get_grades(self.get_id())
        if not submissions:
            return 0.0
        
        total_points = 0.0
        total_credits = 0
        
        for submission in submissions:
            course = Course_repo.get_by_assignment(submission.get_assignment_id())
            if not course:
                continue
            
            total_points += submission.score * course.credits
            total_credits += course.credits
        
        if total_credits == 0:
            return 0.0
        
        return total_points / total_credits
    
    def get_submissions(self, Submission_repo):
        return Submission_repo.list_by_student(self.get_id())
    
    def Drop_course(self, course_id, Enrollment_repo):
        enrollment = Enrollment_repo.get(self.get_id(), course_id)
        if not enrollment:
            raise Exception("Cannot drop: student is not enrolled in this course")
        
        enrollment.status = "dropped"
        enrollment.dropped_at = datetime.now()
        
        return Enrollment_repo.update(enrollment)