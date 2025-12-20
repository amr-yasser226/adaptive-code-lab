class Assignment:
    def __init__(self, id, course_id, title, description, release_date, due_date, max_points, is_published, allow_late_submissions, late_submission_penalty, created_at, updated_at):
        self.__id = id
        self.__course_id = course_id
        self.title = title
        self.description = description
        self.release_date = release_date
        self.due_date = due_date
        self.max_points = max_points
        self.is_published = bool(is_published)
        self.allow_late_submissions = bool(allow_late_submissions)
        self.late_submission_penalty = late_submission_penalty
        self.created_at = created_at
        self.updated_at = updated_at
        # Template-required attributes
        self.languages = ['python']
        self.points = max_points or 100
        self.submission_count = 0  # Will be populated by routes if needed
    def get_id(self):
        return self.__id
    def get_course_id(self):
        return self.__course_id
    # def add_test_case(self, testcase): Not implemeted in the Assignment service ---> (Testcases_service)
    #     pass
    def publish(self):
        self.is_published = True
    
    def unpublish(self):
        self.is_published = False
    
    def extend_deadline(self, new_due_date):
        self.due_date = new_due_date
        
    # def get_submissions(self):
    #     pass
    # def calculate_statistics(self):
    #     pass
