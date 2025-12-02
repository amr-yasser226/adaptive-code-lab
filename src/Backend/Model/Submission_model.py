class Submission :
    valid_languages =('python', 'java', 'cpp', 'javascript') 
    valid_statuses =('pending','queued', 'running', 'graded', 'failed', 'error')
    def __init__(self, id , assignmnet_id , student_id , version , language , status , score , is_late , created_at , update_at , grade_at ): 
        if language not in Submission.valid_languages:
            raise ValueError(
                f"Invalid language: {language}. "
                f"Allowed languages: {Submission.valid_languages}"
            )
        if status not in Submission.valid_statuses:
            raise ValueError(
                f"Invalid status: {status}. "
                f"Allowed statuses: {Submission.valid_statuses}"
            )
        self.__id = id
        self.__assignmnet_id = assignmnet_id
        self.__student_id = student_id
        self.version = version
        self.language = language
        self.status = status
        self.score = score
        self.is_late = bool(is_late)
        self.created_at = created_at
        self.update_at = update_at
        self.grade_at = grade_at

    def get_id(self):
            return self.__id
    def get_assignment_id(self):
            return self.__assignmnet_id
    def get_student_id(self):
            return self.__student_id
    
    def enqueue_for_grading(self):
            self.status = 'queued'
    def attach_file(): 
         pass 
    def get_results(self):
            pass
    def regrade(self):
            pass 
    def calcualted_score(self):
            pass
    def get_files(self):
            pass