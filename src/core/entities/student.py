from datetime import datetime
from core.entities.user import User
from core.entities.enrollment import Enrollment
from core.entities.submission import Submission


class Student(User):
    def __init__(self, id, name, email, password, created_at, updated_at, 
                 student_number, program, year_level, is_active=True):
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
        self.program = program
        self.year_level = year_level
    