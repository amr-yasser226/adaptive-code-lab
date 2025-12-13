from sqlalchemy.exc import SQLAlchemyError
from core.entities.hint import Hint

class Hint_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT
                id, submission_id, model_used, confidence, hint_text,
                is_helpful, feedback_text, created_at
            FROM hints
            WHERE id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Hint(
            id=row.id,
            submission_id=row.submission_id,
            model_used=row.model_used,
            confidence=row.confidence,
            hint_text=row.hint_text,
            is_helpful=row.is_helpful,
            feedback=row.feedback_text,
            created_at=row.created_at
        )

    def create(self, hint: Hint):
        try:
            query = """
                INSERT INTO hints (
                    submission_id, model_used, confidence, hint_text,
                    is_helpful, feedback_text, created_at
                )
                VALUES (
                    :submission_id, :model_used, :confidence, :hint_text,
                    :is_helpful, :feedback_text, :created_at
                )
            """
            self.db.execute(query, {
                "submission_id": hint.get_submission_id(),
                "model_used": hint.model_used,
                "confidence": hint.confidence,
                "hint_text": hint.hint_text,
                "is_helpful": int(hint.is_helpful),
                "feedback_text": hint.feedback,
                "created_at": hint.created_at
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone()[0]
            self.db.commit()
            return self.get_by_id(new_id)
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def update(self, hint: Hint):
        try:
            query = """
                UPDATE hints
                SET
                    model_used = :model_used,
                    confidence = :confidence,
                    hint_text = :hint_text,
                    is_helpful = :is_helpful,
                    feedback_text = :feedback_text
                WHERE id = :id
            """
            self.db.execute(query, {
                "id": hint.get_id(),
                "model_used": hint.model_used,
                "confidence": hint.confidence,
                "hint_text": hint.hint_text,
                "is_helpful": int(hint.is_helpful),
                "feedback_text": hint.feedback
            })
            self.db.commit()
            return self.get_by_id(hint.get_id())
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def delete(self, id: int):
        try:
            self.db.execute("DELETE FROM hints WHERE id = :id", {"id": id})
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            return False

    def list_by_submission(self, submission_id: int):
        query = """
            SELECT *
            FROM hints
            WHERE submission_id = :sid
            ORDER BY created_at DESC
        """
        result = self.db.execute(query, {"sid": submission_id})
        rows = result.fetchall()
        return [
            Hint(
                id=row.id,
                submission_id=row.submission_id,
                model_used=row.model_used,
                confidence=row.confidence,
                hint_text=row.hint_text,
                is_helpful=row.is_helpful,
                feedback=row.feedback_text,
                created_at=row.created_at
            )
            for row in rows
        ]

    def mark_helpful(self, id: int):
        try:
            self.db.execute("UPDATE hints SET is_helpful = 1 WHERE id = :id", {"id": id})
            self.db.commit()
            return self.get_by_id(id)
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def mark_not_helpful(self, id: int):
        try:
            self.db.execute("UPDATE hints SET is_helpful = 0 WHERE id = :id", {"id": id})
            self.db.commit()
            return self.get_by_id(id)
        except SQLAlchemyError:
            self.db.rollback()
            return None
