import pickle
from datetime import datetime
from typing import Optional, List

from core.exceptions.validation_error import ValidationError
from core.entities.embedding import Embedding
# from Backend.Model import Embedding_model as EmbModel  # only if needed; safe to ignore

# Note: your embedding generation function lives elsewhere (you provided it).
# We'll import the helper that calls Gemini if available.
try:
    from infrastructure.ai.embeddings import generate_embedding  # your module that calls genai
except Exception:
    # Fall back: generate_embedding may be in another path; user already has it in project root.
    def generate_embedding(_text):
        raise RuntimeError("generate_embedding not available; please import your generator module")


class EmbeddingService:
    """
    Wrapper around Embedding_repo and the actual embedding generator.
    Policy: only generate embedding if missing (user's choice).
    """

    def __init__(self, embedding_repo, model_name: str = None):
        """
        embedding_repo: instance of Embedding_repo (has find_by_submission, save_embedding, etc.)
        model_name: optional descriptive name for model; if None we use generator defaults
        """
        self.embedding_repo = embedding_repo
        self.model_name = model_name

    def get_embedding_vector(self, submission_id: int) -> Optional[List[float]]:
        """
        Return the raw vector (Python list of floats) for submission_id, or None if missing.
        """
        emb = self.embedding_repo.find_by_submission(submission_id)
        if not emb:
            return None

        # emb.vector_ref is stored as pickled bytes by your embedding pipeline
        try:
            vec = pickle.loads(emb.vector_ref) if emb.vector_ref is not None else None
        except Exception as e:
            raise ValidationError(f"Failed to deserialize embedding for submission {submission_id}: {e}")
        return vec

    def ensure_embedding(self, submission_id: int, code_text: Optional[str] = None, generate_if_missing: bool = True) -> List[float]:
        """
        Ensure an embedding exists for `submission_id`.
        - If an embedding exists -> returns it.
        - If missing and generate_if_missing==True and code_text provided -> generate, store and return it.
        - If missing and cannot generate -> raises ValidationError.
        """
        vec = self.get_embedding_vector(submission_id)
        if vec is not None:
            return vec

        if not generate_if_missing:
            raise ValidationError("Embedding not found and generation is disabled")

        if not code_text:
            raise ValidationError("Embedding missing and no code_text provided to generate it")

        # call the actual generator (Gemini)
        generated = generate_embedding(code_text)
        if generated is None:
            raise ValidationError("Embedding generation failed")

        # Save embedding via repo: repo.save_embedding expects an Embedding object whose vector_ref is pickled bytes
        pickled = pickle.dumps(generated)
        emb_obj = Embedding(
            id=None,
            submission_id=submission_id,
            vector_ref=pickled,
            model_version=self.model_name if self.model_name else "gemini-default",
            dimensions=len(generated),
            created_at=datetime.utcnow()
        )

        saved = self.embedding_repo.save_embedding(emb_obj)
        if not saved:
            # If repo returns None on error
            raise ValidationError("Failed to save generated embedding")
        return generated

    def compute_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Compute cosine similarity safely. Uses pure Python math to avoid an explicit numpy dependency here.
        If you prefer, replace with numpy for speed.
        """
        if vec_a is None or vec_b is None:
            raise ValidationError("One or both vectors are None")
        if len(vec_a) != len(vec_b):
            raise ValidationError("Embedding vector lengths differ")

        dot = 0.0
        norm_a = 0.0
        norm_b = 0.0
        for a, b in zip(vec_a, vec_b):
            a_f = float(a)
            b_f = float(b)
            dot += a_f * b_f
            norm_a += a_f * a_f
            norm_b += b_f * b_f

        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / ((norm_a ** 0.5) * (norm_b ** 0.5))
