class SimilarityComparison : 
    def __init__ (self , similarity_id , compared_submission_id , match_score , note  ,match_segments ): 
        self.__similarity_id = similarity_id
        self.__compared_submission_id = compared_submission_id
        self.match_score = match_score
        self.note = note
        self.match_segments = match_segments
        
    def get_similarity_id (self):
            return self.__similarity_id
    def get_compared_submission_id (self):
            return self.__compared_submission_id
    def get_match_details (self):
        return {
            "similarity_id": self.__similarity_id,
            "compared_submission_id": self.__compared_submission_id,
            "match_score": self.match_score,
            "match_segments": self.match_segments,
            "note": self.note
        }