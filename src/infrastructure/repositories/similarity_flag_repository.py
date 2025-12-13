import json
import sqlite3
from core.entities.similarity_flag import SimilarityFlag

class SimilarityFlagRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT id, submission_id, similarity_score, highlighted_spans,
                   is_reviewed, reviewed_by, review_notes, reviewed_at, created_at
            FROM similarity_flags
            WHERE id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        segments = json.loads(row.highlighted_spans) if row.highlighted_spans else None
        return SimilarityFlag(
            id=row.id,
            submission_id=row.submission_id,
            similarity_score=row.similarity_score,
            highlighted_spans=segments,
            is_reviewed=row.is_reviewed,
            reviewd_by=row.reviewed_by,
            review_notes=row.review_notes,
            reviewed_at=row.reviewed_at,
            created_at=row.created_at
        )

    def get_by_submission(self, submission_id: int):
        query = """
            SELECT id, submission_id, similarity_score, highlighted_spans,
                   is_reviewed, reviewed_by, review_notes, reviewed_at, created_at
            FROM similarity_flags
            WHERE submission_id = :sid
        """
        result = self.db.execute(query, {"sid": submission_id})
        row = result.fetchone()
        if not row:
            return None
        segments = json.loads(row.highlighted_spans) if row.highlighted_spans else None
        return SimilarityFlag(
            id=row.id,
            submission_id=row.submission_id,
            similarity_score=row.similarity_score,
            highlighted_spans=segments,
            is_reviewed=row.is_reviewed,
            reviewd_by=row.reviewed_by,
            review_notes=row.review_notes,
            reviewed_at=row.reviewed_at,
            created_at=row.created_at
        )

    def create(self, flag: SimilarityFlag):
        try:
            query = """
                INSERT INTO similarity_flags (
                    submission_id, similarity_score, highlighted_spans,
                    is_reviewed, reviewed_by, review_notes, reviewed_at, created_at
                )
                VALUES (
                    :submission_id, :similarity_score, :highlighted_spans,
                    :is_reviewed, :reviewed_by, :review_notes, :reviewed_at, :created_at
                )
            """
            self.db.execute(query, {
                "submission_id": flag.get_submission_id(),
                "similarity_score": flag.similarity_score,
                "highlighted_spans": json.dumps(flag.highlighted_spans) if flag.highlighted_spans is not None else None,
                "is_reviewed": int(flag.is_reviewed),
                "reviewed_by": flag.reviewd_by,
                "review_notes": flag.review_notes,
                "reviewed_at": flag.reviewed_at,
                "created_at": flag.created_at
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone()[0]
            self.db.commit()
            return self.get_by_id(new_id)
        except sqlite3.Error:
            self.db.rollback()
            return None

    def update(self, flag: SimilarityFlag):
        try:
            query = """
                UPDATE similarity_flags
                SET
                    similarity_score = :similarity_score,
                    highlighted_spans = :highlighted_spans,
                    is_reviewed = :is_reviewed,
                    reviewed_by = :reviewed_by,
                    review_notes = :review_notes,
                    reviewed_at = :reviewed_at
                WHERE id = :id
            """
            self.db.execute(query, {
                "id": flag.get_id(),
                "similarity_score": flag.similarity_score,
                "highlighted_spans": json.dumps(flag.highlighted_spans) if flag.highlighted_spans is not None else None,
                "is_reviewed": int(flag.is_reviewed),
                "reviewed_by": flag.reviewd_by,
                "review_notes": flag.review_notes,
                "reviewed_at": flag.reviewed_at
            })
            self.db.commit()
            return self.get_by_id(flag.get_id())
        except sqlite3.Error:
            self.db.rollback()
            return None

    def delete(self, id: int):
        try:
            self.db.execute("DELETE FROM similarity_flags WHERE id = :id", {"id": id})
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            return False

    def list_unreviewed(self, limit: int = 100):
        query = """
            SELECT id, submission_id, similarity_score, highlighted_spans,
                   is_reviewed, reviewed_by, review_notes, reviewed_at, created_at
            FROM similarity_flags
            WHERE is_reviewed = 0
            ORDER BY created_at DESC
            LIMIT :limit
        """
        result = self.db.execute(query, {"limit": limit})
        rows = result.fetchall()
        comps = []
        for row in rows:
            segments = json.loads(row.highlighted_spans) if row.highlighted_spans else None
            comps.append(SimilarityFlag(
                id=row.id,
                submission_id=row.submission_id,
                similarity_score=row.similarity_score,
                highlighted_spans=segments,
                is_reviewed=row.is_reviewed,
                reviewd_by=row.reviewed_by,
                review_notes=row.review_notes,
                reviewed_at=row.reviewed_at,
                created_at=row.created_at
            ))
        return comps

    def mark_reviewed(self, id: int, reviewer_id: int, review_notes: str = None, reviewed_at = None):
        try:
            self.db.execute("""
                UPDATE similarity_flags
                SET is_reviewed = 1, reviewed_by = :reviewer_id, review_notes = :review_notes, reviewed_at = :reviewed_at
                WHERE id = :id
            """, {"id": id, "reviewer_id": reviewer_id, "review_notes": review_notes, "reviewed_at": reviewed_at})
            self.db.commit()
            return self.get_by_id(id)
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def dismiss(self, id: int, reviewer_id: int, reviewed_at = None):
        try:
            self.db.execute("""
                UPDATE similarity_flags
                SET is_reviewed = 1, reviewed_by = :reviewer_id, review_notes = :notes, reviewed_at = :reviewed_at
                WHERE id = :id
            """, {"id": id, "reviewer_id": reviewer_id, "notes": "Dismissed", "reviewed_at": reviewed_at})
            self.db.commit()
            return self.get_by_id(id)
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def escalate(self, id: int, reviewer_id: int, reviewed_at = None):
        try:
            self.db.execute("""
                UPDATE similarity_flags
                SET is_reviewed = 1, reviewed_by = :reviewer_id, review_notes = :notes, reviewed_at = :reviewed_at
                WHERE id = :id
            """, {"id": id, "reviewer_id": reviewer_id, "notes": "Escalated for further investigation", "reviewed_at": reviewed_at})
            self.db.commit()
            return self.get_by_id(id)
        except SQLAlchemyError:
            self.db.rollback()
            return None
