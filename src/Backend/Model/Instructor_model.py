from Backend.Model.User_model import User
class Instructor(User):
    def __init__(self, id, name, email, password, created_at, updated_at, instructor_code, bio, office_hours, is_active=True):
        super().__init__(id=id, name=name, email=email, password=password, role="instructor", created_at=created_at, updated_at=updated_at, is_active=is_active)
        self.instructor_code = instructor_code
        self.bio = bio
        self.office_hours = office_hours
    

    def Create_course(self, course_name, course_description):
        pass
    def create_assignment(self, course_id, assignment_details):
        pass
    def review_similarity(self, Flag_id,action,notes):
        pass
    def export_grades(self, course_id):
        pass
    def get_courses(self):
        pass