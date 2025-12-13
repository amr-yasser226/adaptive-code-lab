class SimilarityFlag:
    def __init__(self, id , submission_id , similarity_score,  highlighted_spans, is_reviewed ,reviewd_by  , review_notes , reviewed_at,created_at  ):
        self.__id = id
        self.__submission_id = submission_id
        self.similarity_score = similarity_score
        self.highlighted_spans = highlighted_spans
        self.is_reviewed = bool(is_reviewed)
        self.reviewd_by = reviewd_by
        self.review_notes = review_notes
        self.reviewed_at = reviewed_at
        self.created_at = created_at
    def get_id(self):
            return self.__id
    def get_submission_id(self):
            return self.__submission_id    
#     def mark_reviewed(self, reviewd_by , reviewed_at ,review_notes = None  ):
#             self.is_reviewed = True
#             self.reviewd_by = reviewd_by
#             self.review_notes = review_notes
#             self.reviewed_at = reviewed_at
        
#     def dismiss (self , reviewd_by , reviewed_at , ):
#             self.is_reviewed = True
#             self.reviewd_by = reviewd_by
#             self.review_notes = "Dismissed"
#             self.reviewed_at = reviewed_at
#     def escalate(self,reviewed_by , reviewed_at ):
#         self.is_reviewed = True
#         self.reviewd_by = reviewed_by
#         self.reviewed_at = reviewed_at
#         self.review_notes = "Escalated for further investigation"