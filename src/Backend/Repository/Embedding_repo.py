from sqlalchemy.exc import SQLAlchemyError
from Model.Embedding_model import Embedding

class Embedding_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        """
        FIXED: Added submission_id to Embedding constructor
        """
        query = """
            SELECT 
                e.id, e.submission_id, e.vector_ref, e.model_version, e.dimension, e.created_at
            FROM embeddings e
            WHERE e.id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Embedding(
            id=row.id,
            submission_id=row.submission_id,  # FIXED: Added this field
            vector_ref=row.vector_ref,
            model_version=row.model_version,
            dimensions=row.dimension,
            created_at=row.created_at
        )

    def save_embedding(self, embedding: Embedding):
        try:
            self.db.begin_transaction()
            query = """
                INSERT INTO embeddings (
                    submission_id, vector_ref, model_version, dimension
                )
                VALUES (
                    :submission_id, :vector_ref, :model_version, :dimension
                )
            """
            self.db.execute(query, {
                "submission_id": embedding.get_submission_id(),
                "vector_ref": embedding.vector_ref,
                "model_version": embedding.model_version,
                "dimension": embedding.dimensions
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone().id
            self.db.commit()
            return self.get_by_id(new_id)
        except Exception as e:
            self.db.rollback()
            print("Error saving embedding:", e)
            return None

    def find_by_submission(self, submissionId: int):
        """
        FIXED: Added submission_id to Embedding constructor
        """
        query = """
            SELECT 
                e.id, e.submission_id, e.vector_ref, e.model_version, e.dimension, e.created_at
            FROM embeddings e
            WHERE e.submission_id = :submission_id
        """
        result = self.db.execute(query, {"submission_id": submissionId})
        row = result.fetchone()
        if not row:
            return None
        return Embedding(
            id=row.id,
            submission_id=row.submission_id,  # FIXED: Added this field
            vector_ref=row.vector_ref,
            model_version=row.model_version,
            dimensions=row.dimension,
            created_at=row.created_at
        )