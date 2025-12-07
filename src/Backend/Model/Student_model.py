from os import major
from Model.User_model import User

class Student(User):
    def __init__(self, id, name, email, password, created_at, updated_at, student_number, Program, year_Level, is_Active=True):
        super().__init__(id=id, name=name, email=email, password=password, role="student", created_at=created_at, updated_at=updated_at, is_Active=is_Active)
        self.student_number = student_number
        self.program = Program
        self.year_Level = year_Level
    def Enroll_course(self, course_id):
        pass    
    def Submit_assignment(self, assignment_id, submission):
        pass
    def View_GPA(self):
        pass
    def get_submissions(self):
        pass
    def Drop_course(self, course_id):
        pass