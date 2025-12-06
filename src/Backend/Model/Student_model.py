from os import major
from datetime import datetime
from Model.User_model import User
from Model.Enrollment_model import Enrollment
from Model.Submission_model import Submission
class Student(User):
    def __init__(self, id, name, email, password, created_at, updated_at, student_number, Program, year_Level, is_Active=True):
        super().__init__(id=id, name=name, email=email, password=password, role="student", created_at=created_at, updated_at=updated_at, is_Active=is_Active)
        self.student_number = student_number
        self.program = Program
        self.year_Level = year_Level
    def Enroll_course(self, course_id , Course_repo , Enrollment_repo):
        # check the course exist 
        course =Course_repo.get_by_id(course_id)
        if not course : 
            raise Exception("Course does not exist")
        
        existing =  Enrollment_repo.get(self.get_id(),course_id)
        if existing : 
            raise Exception("Student is already enrolled in this course")
        
        enrollment = Enrollment(
            student_id=self.get_id(), 
            course_id=course_id,
            status="enrolled", 
            enrolled_at= datetime.now(),
            dropped_at= None
        )
        return Enrollment_repo.enroll(enrollment)
            
    def Submit_assignment(self, assignment_id, submission_text , Assignment_repo , Submission_repo , Enrollment_repo):

        assignment =Assignment_repo.get_by_id(assignment_id)
        if not assignment : 
            raise Exception("Assignment does mot exist")
        enrollment =Enrollment_repo.get(self.get_id(),assignment.get_course_id())
        if not enrollment : 
            raise Exception("You cannot submit. You are not enrolled in this course.")
        last_sub =Submission_repo.get_latest_submission(self.get_id(),assignment_id)
        if last_sub: 

            new_version = last_sub.version +1 
        else : 
            new_version =1
        is_late= datetime.now()> assignment.due_date
        new_submission = Submission(
            id=None,
            assignment_id=assignment_id,
            student_id=self.get_id(),
            version=new_version,
            language="python",  # or choose based on UI input
            status="submitted",
            score=None,
            is_late=is_late,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            grade_at=None
        )
        return Submission_repo.create(new_submission)
    def View_GPA(self, Submssion_repo , Course_repo):
        submission=Submssion_repo.get_grades(self.get_id())
        if not submission : 
            return 0.0

        total_points =0 
        total_credits=0 

        for sub in submission : 
            course = Course_repo.get_by_assignment(sub.get_assignment_id())
            if not course : 
                continue 
            total_points += sub.score * course.credits
            total_credits+=course.credits

        if total_credits == 0 : 
            return 0.0

        return total_points/total_credits
        
    def get_submissions(self, Submission_repo):
        return Submission_repo.list_by_student(self.get_id())
    def Drop_course(self, course_id , Enrollment_repo):
        
        enrollment = Enrollment_repo.get(self.get_id(),course_id)
        
        if not enrollment : 
            raise Exception("Cannot drop: student is not enrolled in this course")
        
        enrollment.status ="dropped"
        enrollment.dropped_at= datetime.now()


        return Enrollment_repo.update(enrollment)