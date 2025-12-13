import json
import sqlite3
from core.entities.similarity_comparison import SimilarityComparison

class SimilarityComparison_repo:
    def __init__(self, db):
        self.db = db

    def get(self, similarity_id: int, compared_submission_id: int):
        query = """
            SELECT
                similarity_id, compared_submission_id, match_score,
                note, matched_segments
            FROM similarity_comparisons
            WHERE similarity_id = :sid AND compared_submission_id = :cid
        """
        result = self.db.execute(query, {"sid": similarity_id, "cid": compared_submission_id})
        row = result.fetchone()
        if not row:
            return None
        segments = json.loads(row.matched_segments) if row.matched_segments else None
        return SimilarityComparison(
            similarity_id=row.similarity_id,
            compared_submission_id=row.compared_submission_id,
            match_score=row.match_score,
            note=row.note,
            match_segments=segments
        )

    def create(self, comp: SimilarityComparison):
        try:
            query = """
                INSERT INTO similarity_comparisons (
                    similarity_id, compared_submission_id,
                    match_score, note, matched_segments
                )
                VALUES (
                    :similarity_id, :compared_submission_id,
                    :match_score, :note, :matched_segments
                )
            """
            self.db.execute(query, {
                "similarity_id": comp.get_similarity_id(),
                "compared_submission_id": comp.get_compared_submission_id(),
                "match_score": comp.match_score,
                "note": comp.note,
                "matched_segments": json.dumps(comp.match_segments) if comp.match_segments is not None else None
            })
            self.db.commit()
            return self.get(comp.get_similarity_id(), comp.get_compared_submission_id())
        except sqlite3.Error:
            self.db.rollback()
            return None

    def update(self, comp: SimilarityComparison):
        try:
            query = """
                UPDATE similarity_comparisons
                SET
                    match_score = :match_score,
                    note = :note,
                    matched_segments = :matched_segments
                WHERE similarity_id = :similarity_id
                AND compared_submission_id = :compared_submission_id
            """
            self.db.execute(query, {
                "similarity_id": comp.get_similarity_id(),
                "compared_submission_id": comp.get_compared_submission_id(),
                "match_score": comp.match_score,
                "note": comp.note,
                "matched_segments": json.dumps(comp.match_segments) if comp.match_segments is not None else None
            })
            self.db.commit()
            return self.get(comp.get_similarity_id(), comp.get_compared_submission_id())
        except sqlite3.Error:
            self.db.rollback()
            return None

    def delete(self, similarity_id: int, compared_submission_id: int):
        try:
            self.db.execute(
                "DELETE FROM similarity_comparisons WHERE similarity_id = :sid AND compared_submission_id = :cid",
                {"sid": similarity_id, "cid": compared_submission_id}
            )
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            return False

    def list_by_similarity(self, similarity_id: int):
        query = """
            SELECT *
            FROM similarity_comparisons
            WHERE similarity_id = :sid
        """
        result = self.db.execute(query, {"sid": similarity_id})
        rows = result.fetchall()
        comps = []
        for row in rows:
            segments = json.loads(row.matched_segments) if row.matched_segments else None
            comps.append(SimilarityComparison(
                similarity_id=row.similarity_id,
                compared_submission_id=row.compared_submission_id,
                match_score=row.match_score,
                note=row.note,
                match_segments=segments
            ))
        return comps
