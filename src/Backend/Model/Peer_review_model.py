import datetime
class PeerReview : 
    def __init__(self , submission_id , reviewer_student_id, rubric_score , comments , is_submitted , submitted_at ,created_at): 
        self.__submission_id = submission_id
        self.__reviewer_student_id = reviewer_student_id
        self.rubric_score = rubric_score
        self.comments = comments
        self.is_submitted = bool(is_submitted)
        self.submitted_at = submitted_at
        self.created_at = created_at
    def get_submission_id(self):
            return self.__submission_id
    def get_reviewer_student_id(self):
            return self.__reviewer_student_id
    def submit_review(self): 
        self.is_submitted = True
        self.submitted_at = datetime.datetime.now()
    def update_review(self , rubric_score , comments):
        if rubric_score is not None:
            self.rubric_score = rubric_score
        if comments is not None:
            self.comments = comments
    def calculate_rubric_score(self):
        pass