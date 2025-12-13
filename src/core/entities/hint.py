class Hint : 
    def __init__(self , id , submission_id , model_used , confidence , hint_text , is_helpful , feedback , created_at ):
        self.__id = id
        self.__submission_id = submission_id
        self.model_used = model_used
        self.confidence = confidence
        self.hint_text = hint_text
        self.is_helpful = bool(is_helpful)
        self.feedback = feedback
        self.created_at = created_at
    def get_id(self):
            return self.__id
    def get_submission_id(self):
            return self.__submission_id
    
    
    def genrate_hint(self):
            pass
    def mark_helpful(self):
            self.is_helpful = True
            
    def mark_not_helpful(self):
            self.is_helpful = False
            