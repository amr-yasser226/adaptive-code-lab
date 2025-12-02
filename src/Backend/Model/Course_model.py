class Course:
    def __init__(self, id, instructor_id, code , title ,describtion,year,semester,max_students,created_at,status,updated_at,credits):

        self.__id = id
        self.__instructor_id = instructor_id
        self.code = code
        self.title = title
        self.describtion = describtion
        self.year = year
        self.semester = semester
        self.max_students = max_students
        self.created_at = created_at
        self.status = status
        self.updated_at = updated_at
        self.credits = credits 
    def get_if(self):
        return self.__id
    def get_instructor_id(self):
            return self.__instructor_id
    def add_assignment(self, assignment):
            pass
    def enroll_student(self, student_id):
            pass
    def list_assignments(self):
            pass
    def get_enrolled_student(self):
          pass
    def archive(self):
                self.status = "inactive"
    def publish(self):
                self.status = "active"
    