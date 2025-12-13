import sqlite3
from core.entities.similarity_flag import SimilarityFlag


class FlagRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT 
                f.id, f.submission_id, f.similarity_score, f.highlighted_spans,
                f.is_reviewed, f.reviewed_by, f.review_notes, f.reviewed_at, f.created_at
            FROM similarity_flags f
            WHERE f.id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return SimilarityFlag(
            id=row.id,
            submission_id=row.submission_id,
            similarity_score=row.similarity_score,
            highlighted_spans=row.highlighted_spans,
            is_reviewed=row.is_reviewed,
            reviewd_by=row.reviewed_by,
            review_notes=row.review_notes,
            reviewed_at=row.reviewed_at,
            created_at=row.created_at
        )

    def save_similarityflag(self, flag: SimilarityFlag):
        try:
            query = """
                INSERT INTO similarity_flags (
                    submission_id, similarity_score, highlighted_spans,
                    is_reviewed, reviewed_by, review_notes, reviewed_at
                )
                VALUES (
                    :submission_id, :similarity_score, :highlighted_spans,
                    :is_reviewed, :reviewed_by, :review_notes, :reviewed_at
                )
            """
            self.db.execute(query, {
                "submission_id": flag.get_submission_id(),
                "similarity_score": flag.similarity_score,
                "highlighted_spans": flag.highlighted_spans,
                "is_reviewed": int(flag.is_reviewed),
                "reviewed_by": flag.reviewd_by,
                "review_notes": flag.review_notes,
                "reviewed_at": flag.reviewed_at
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone()[0]
            self.db.commit()
            return self.get_by_id(new_id)
        except sqlite3.Error as e:
            self.db.rollback()
            print("Error saving flag:", e)
            return None

    def find_unreviewed(self):
        query = """
            SELECT 
                f.id, f.submission_id, f.similarity_score, f.highlighted_spans,
                f.is_reviewed, f.reviewed_by, f.review_notes, f.reviewed_at, f.created_at
            FROM similarity_flags f
            WHERE f.is_reviewed = 0
            ORDER BY f.created_at ASC
        """
        result = self.db.execute(query, {})
        flags = []
        for row in result.fetchall():
            flags.append(SimilarityFlag(
                id=row.id,
                submission_id=row.submission_id,
                similarity_score=row.similarity_score,
                highlighted_spans=row.highlighted_spans,
                is_reviewed=row.is_reviewed,
                reviewd_by=row.reviewed_by,
                review_notes=row.review_notes,
                reviewed_at=row.reviewed_at,
                created_at=row.created_at
            ))
        return flags
