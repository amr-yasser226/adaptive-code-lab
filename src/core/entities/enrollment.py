class Enrollment : 
    VALID_STATUS =('enrolled','dropped','completed')
    def __init__(self, student_id , course_id , status , enrolled_at , dropped_at , final_grade):
        if status not in Enrollment.VALID_STATUS:
            raise ValueError(
                f"Invalid enrollment status: {status}. "
                f"Allowed: {Enrollment.VALID_STATUS}"
            )
        self.__student_id = student_id
        self.__course_id = course_id
        self.status = status
        self.final_grade = final_grade
        self.enrolled_at = enrolled_at
        self.dropped_at = dropped_at


    def get_student_id(self):
            return self.__student_id
    def get_course_id(self):
            return self.__course_id  


    def get_progress(self):
        # Placeholder for future logic (e.g., calculating completion %)
        return 0.0

    def calculate_grade(self):
        return self.final_grade if self.final_grade is not None else 0.0

    def drop(self , dropped_at):
        self.status = 'dropped'
        self.dropped_at = dropped_at

    def complete(self, grade):
        self.status = 'completed'
        self.final_grade = grade