import pickle
from datetime import datetime
from typing import Optional, List

from core.exceptions.validation_error import ValidationError
from core.entities.embedding import Embedding


class EmbeddingService:
    
    def __init__(self, embedding_repo, embedding_client=None):
        self.embedding_repo = embedding_repo
        self.embedding_client = embedding_client
    
    def get_embedding_vector(self, submission_id: int) -> Optional[List[float]]:
        emb = self.embedding_repo.find_by_submission(submission_id)
        if not emb:
            return None
        
        try:
            vec = pickle.loads(emb.vector_ref) if emb.vector_ref else None
        except Exception as e:
            raise ValidationError(f"Failed to deserialize embedding: {e}")
        return vec
    
    def generate_and_store_embedding(self, submission_id: int, code_text: str) -> List[float]:
        if not self.embedding_client:
            raise ValidationError("Embedding client not configured")
        
        if not code_text:
            raise ValidationError("Code text cannot be empty")
        
        # Generate via client
        try:
            vector = self.embedding_client.generate_embedding(code_text)
        except Exception as e:
            raise ValidationError(f"Embedding generation failed: {e}")
        
        # Store in database
        emb_obj = Embedding(
            id=None,
            submission_id=submission_id,
            vector_ref=pickle.dumps(vector),
            model_version=self.embedding_client.get_model_name(),
            dimensions=len(vector),
            created_at=datetime.utcnow()
        )
        
        saved = self.embedding_repo.save_embedding(emb_obj)
        if not saved:
            raise ValidationError("Failed to save embedding")
        
        return vector
    
    def ensure_embedding(self, submission_id: int, code_text: Optional[str] = None) -> List[float]:
        # Try to get existing
        vec = self.get_embedding_vector(submission_id)
        if vec is not None:
            return vec
        
        # Generate new one
        if not code_text:
            raise ValidationError("Embedding not found and no code_text provided")
        
        return self.generate_and_store_embedding(submission_id, code_text)
