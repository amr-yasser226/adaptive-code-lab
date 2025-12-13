class Embedding:
    """
    FIXED: Added submission_id parameter to constructor
    """
    def __init__(self, id, submission_id, vector_ref, model_version, dimensions, created_at):
        self.__id = id
        self.__submission_id = submission_id  # FIXED: Added this field
        self.vector_ref = vector_ref
        self.model_version = model_version
        self.dimensions = dimensions
        self.created_at = created_at

    def get_id(self):
        return self.__id
    
    def get_submission_id(self):  # FIXED: Added this method
        return self.__submission_id
    
    def refresh(self):
        pass
    
    def computer_similarity(self):
        pass