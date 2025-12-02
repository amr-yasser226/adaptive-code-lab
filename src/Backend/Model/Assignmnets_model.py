class Assignmnets : 
    def __init__(self, id , course_id , title , describtion , releaseDate, due_date , max_points , is_published, allow_late_submissions,late_submission_penalty , created_at , updated_at):
        self.__id =id 
        self.__course_id =course_id
        self.title =title
        self.describtion =describtion
        self.releaseDate = releaseDate
        self.dueDate = due_date
        self.maxpoints = max_points
        self.ispublished = bool(is_published)
        self.allowlateSubmissions = bool(allow_late_submissions)
        self.latesubmission_penealty = late_submission_penalty
        self.created_at = created_at
        self.updated_at = updated_at
    def get_id(self):
        return self.__id
    def get_course_id(self):
        return self.__course_id
    def addtestcase(self, testcase):
        pass
    def publish(self):
        self.ispublished = True
        pass
    def unpublish(self):
        self.ispublished = False
        pass
    def extend_deadline(self, new_due_date  ):
        self.dueDate = new_due_date
        pass
    def get_submissions(self):
        pass
    def calculate_statistics(self):
        pass
