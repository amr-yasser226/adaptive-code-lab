from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

from core.exceptions.validation_error import ValidationError
from core.entities.similarity_flag import SimilarityFlag
from core.entities.similarity_comparison import SimilarityComparison

DEFAULT_THRESHOLD = 0.85


class SimilarityService:
    def __init__(
        self,
        embedding_service,
        similarity_repo,
        comparison_repo,
        submission_repo,
        assignment_repo=None,
        course_repo=None,
        threshold: float = DEFAULT_THRESHOLD,
    ):
        self.embedding_service = embedding_service
        self.similarity_repo = similarity_repo
        self.comparison_repo = comparison_repo
        self.submission_repo = submission_repo
        self.assignment_repo = assignment_repo
        self.course_repo = course_repo
        self.threshold = float(threshold)

    def _compute_cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = 0.0
        norm_a = 0.0
        norm_b = 0.0
        for a, b in zip(vec_a, vec_b):
            a_f, b_f = float(a), float(b)
            dot += a_f * b_f
            norm_a += a_f * a_f
            norm_b += b_f * b_f
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / ((norm_a ** 0.5) * (norm_b ** 0.5))

    def analyze_submission(self, submission_id: int, threshold: Optional[float] = None, generate_embedding_if_missing: bool = False, code_text_for_embedding: Optional[str] = None) -> Dict:
        if threshold is None:
            threshold = self.threshold

        # 1) load submission
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValidationError("Submission not found")

        assignment_id = submission.get_assignment_id()
        if assignment_id is None:
            raise ValidationError("Submission has no assignment id")

        # 2) Get embedding for this submission via EmbeddingService
        if generate_embedding_if_missing and code_text_for_embedding:
            vec_a = self.embedding_service.ensure_embedding(submission_id, code_text_for_embedding)
        else:
            vec_a = self.embedding_service.get_embedding_vector(submission_id)
        
        if vec_a is None:
            raise ValidationError("Embedding for submission not found")

        # 3) find other submissions in same assignment
        others = self.submission_repo.list_by_assignment(assignment_id)
        comparisons = []
        highest_score = 0.0
        highest_pair = None
        flag_needed = False

        for other in others:
            other_id = other.get_id()
            if other_id == submission_id:
                continue

            # Get embedding via EmbeddingService
            vec_b = self.embedding_service.get_embedding_vector(other_id)
            if vec_b is None:
                continue

            # Compute cosine similarity using helper
            try:
                score = self._compute_cosine_similarity(vec_a, vec_b)
            except Exception as e:
                logger.error(f"Error computing similarity: {e}")
                continue

            # create Comparison model and persist
            comp_model = SimilarityComparison(
                similarity_id=None,
                compared_submission_id=other_id,
                match_score=score,
                note=None,
                match_segments=None
            )
            created_comp = self.comparison_repo.create(comp_model)

            comparisons.append({
                "compared_submission_id": other_id,
                "score": score,
                "comparison_record": created_comp
            })

            if score > highest_score:
                highest_score = score
                highest_pair = other_id

            if score >= threshold:
                flag_needed = True

        # 4) create flag if needed (use highest_score as flag score)
        created_flag = None
        if flag_needed:
            flag = SimilarityFlag(
                id=None,
                submission_id=submission_id,
                similarity_score=highest_score,
                highlighted_spans=None,
                is_reviewed=False,
                reviewd_by=None,
                review_notes=None,
                reviewed_at=None,
                created_at=datetime.utcnow()
            )
            created_flag = self.similarity_repo.create(flag)

            # Link existing comparison records to this similarity_id if repo supports update:
            try:
                sim_id = created_flag.get_id() if hasattr(created_flag, "get_id") else None
                if sim_id is not None:
                    for c in comparisons:
                        rec = c.get("comparison_record")
                        if rec and hasattr(rec, "get_similarity_id") and (rec.get_similarity_id() is None):
                            # attempt to update the record's similarity_id and persist
                            try:
                                # some repo returns model instances, others dicts — handle common cases:
                                if hasattr(rec, "__dict__"):
                                    # set attribute if available
                                    if hasattr(rec, "similarity_id"):
                                        rec.similarity_id = sim_id
                                # call update (if exists)
                                self.comparison_repo.update(rec)
                            except Exception as e:
                                logger.warning(f"Failed to link comparison record: {e}")
            except Exception as e:
                logger.error(f"Error linking comparison records to flag: {e}")

        return {
            "submission_id": submission_id,
            "comparisons": comparisons,
            "flag_created": created_flag,
            "threshold_used": threshold,
            "highest_score": highest_score,
            "highest_pair": highest_pair
        }
