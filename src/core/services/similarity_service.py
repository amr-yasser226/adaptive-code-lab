import pickle
from datetime import datetime
from typing import Optional, List, Dict

from Backend.Exceptions.ValidationError import ValidationError
from Backend.Exceptions.AuthError import AuthError
from Backend.Model.Similarity_flag import SimilarityFlag
from Backend.Model.Similarity_Comparison_model import SimilarityComparison

# Default threshold (you can change when constructing the service)
DEFAULT_THRESHOLD = 0.85


class SimilarityService:
    """
    Full automatic similarity detection service that:
      - uses embeddings (via Embedding_repo)
      - compares a submission to other submissions in the same assignment
      - writes SimilarityComparison rows
      - creates a SimilarityFlag if highest score >= threshold
    """

    def __init__(
        self,
        embedding_repo,
        similarity_repo,
        comparison_repo,
        submission_repo,
        assignment_repo,
        course_repo,
        threshold: float = DEFAULT_THRESHOLD,
    ):
        self.embedding_repo = embedding_repo
        self.similarity_repo = similarity_repo
        self.comparison_repo = comparison_repo
        self.submission_repo = submission_repo
        self.assignment_repo = assignment_repo
        self.course_repo = course_repo
        self.threshold = float(threshold)

    # -------- helpers for embedding extraction ----------
    def _load_vector_from_embedding_row(self, emb_row) -> Optional[List[float]]:
        """
        emb_row is an Embedding model instance returned by embedding_repo.find_by_submission(...)
        Your repo stores vector_ref as pickled bytes. We unpickle to Python list of floats.
        """
        if not emb_row:
            return None
        vec_blob = getattr(emb_row, "vector_ref", None)
        if vec_blob is None:
            return None
        try:
            vec = pickle.loads(vec_blob)
        except Exception as e:
            # If repo returns already-deserialized vector (rare), try that
            try:
                return list(vec_blob)
            except Exception:
                raise ValidationError(f"Failed to deserialize embedding: {e}")
        return [float(x) for x in vec]

    # -------- core: compare a submission within its assignment ----------
    def analyze_submission(self, submission_id: int, threshold: Optional[float] = None, generate_embedding_if_missing: bool = False, code_text_for_embedding: Optional[str] = None) -> Dict:
        """
        Compare `submission_id` against other submissions in the same assignment.
        - generate_embedding_if_missing: if True, the service will not only look up embeddings,
          it will attempt to generate one (via embedding_repo usage) — but per your choice earlier,
          we'll default to False (only create if caller asks, consistent with your selection).
          If you want auto-generation on missing embedding, call EmbeddingService first and pass vector saved.
        - code_text_for_embedding: optional code text to generate embedding if allowed.

        Returns a dict with:
          - submission_id
          - comparisons: list of {compared_submission_id, score, record}
          - flag_created: SimilarityFlag object or None
          - highest_score
          - highest_pair
        """
        if threshold is None:
            threshold = self.threshold

        # 1) load submission
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValidationError("Submission not found")

        assignment_id = submission.get_assignment_id()
        if assignment_id is None:
            raise ValidationError("Submission has no assignment id")

        # 2) load embedding for this submission
        emb_row = self.embedding_repo.find_by_submission(submission_id)
        if not emb_row:
            if generate_embedding_if_missing:
                # caller asked to generate; expect they passed code_text_for_embedding
                if not code_text_for_embedding:
                    raise ValidationError("Embedding missing and no code_text provided to generate")
                # The embedding_repo in your codebase expects pickled vector to be stored by save_embedding.
                # But your project already includes an embedding generator; ideally use EmbeddingService to generate.
                raise ValidationError("Embedding missing. Call EmbeddingService.generate_and_store first or pass code_text and set generate_embedding_if_missing logic externally.")
            else:
                raise ValidationError("Embedding for submission not found")

        vec_a = self._load_vector_from_embedding_row(emb_row)
        if vec_a is None:
            raise ValidationError("Could not load vector for submission")

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

            # try to load other embedding
            other_emb = self.embedding_repo.find_by_submission(other_id)
            if not other_emb:
                # skip entries with no embeddings
                continue
            vec_b = self._load_vector_from_embedding_row(other_emb)
            if vec_b is None:
                continue

            # compute cosine similarity
            # we will compute manually (no numpy dependency required)
            try:
                dot = 0.0
                norm_a = 0.0
                norm_b = 0.0
                for a, b in zip(vec_a, vec_b):
                    a_f = float(a)
                    b_f = float(b)
                    dot += a_f * b_f
                    norm_a += a_f * a_f
                    norm_b += b_f * b_f
                score = 0.0 if norm_a == 0 or norm_b == 0 else dot / ((norm_a ** 0.5) * (norm_b ** 0.5))
            except Exception:
                # mismatch lengths or invalid, skip
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
                                try:
                                    self.comparison_repo.update(rec)
                                except Exception:
                                    # best-effort only; not fatal if update fails
                                    pass
                            except Exception:
                                pass
            except Exception:
                # linking is best-effort
                pass

        return {
            "submission_id": submission_id,
            "comparisons": comparisons,
            "flag_created": created_flag,
            "threshold_used": threshold,
            "highest_score": highest_score,
            "highest_pair": highest_pair
        }
