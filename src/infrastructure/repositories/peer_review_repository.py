import json
import sqlite3
from core.entities.peer_review import PeerReview

class PeerReviewRepository:
    def __init__(self, db):
        self.db = db

    def get(self, submission_id: int, reviewer_student_id: int):
        query = """
            SELECT
                submission_id, reviewer_student_id, rubric_scores, comments,
                is_submitted, submitted_at, created_at
            FROM peer_reviews
            WHERE submission_id = :sid AND reviewer_student_id = :rid
        """
        result = self.db.execute(query, {"sid": submission_id, "rid": reviewer_student_id})
        row = result.fetchone()
        if not row:
            return None
        rubric = json.loads(row.rubric_scores) if row.rubric_scores else None
        return PeerReview(
            submission_id=row.submission_id,
            reviewer_student_id=row.reviewer_student_id,
            rubric_score=rubric,
            comments=row.comments,
            is_submitted=row.is_submitted,
            submitted_at=row.submitted_at,
            created_at=row.created_at
        )

    def create(self, review: PeerReview):
        try:
            query = """
                INSERT INTO peer_reviews (
                    submission_id, reviewer_student_id, rubric_scores, comments,
                    is_submitted, submitted_at, created_at
                )
                VALUES (
                    :submission_id, :reviewer_student_id, :rubric_scores, :comments,
                    :is_submitted, :submitted_at, :created_at
                )
            """
            self.db.execute(query, {
                "submission_id": review.get_submission_id(),
                "reviewer_student_id": review.get_reviewer_student_id(),
                "rubric_scores": json.dumps(review.rubric_score) if review.rubric_score is not None else None,
                "comments": review.comments,
                "is_submitted": int(review.is_submitted),
                "submitted_at": review.submitted_at,
                "created_at": review.created_at
            })
            self.db.commit()
            return self.get(review.get_submission_id(), review.get_reviewer_student_id())
        except sqlite3.Error:
            self.db.rollback()
            return None

    def update(self, review: PeerReview):
        try:
            query = """
                UPDATE peer_reviews
                SET
                    rubric_scores = :rubric_scores,
                    comments = :comments,
                    is_submitted = :is_submitted,
                    submitted_at = :submitted_at
                WHERE submission_id = :submission_id AND reviewer_student_id = :reviewer_student_id
            """
            self.db.execute(query, {
                "submission_id": review.get_submission_id(),
                "reviewer_student_id": review.get_reviewer_student_id(),
                "rubric_scores": json.dumps(review.rubric_score) if review.rubric_score is not None else None,
                "comments": review.comments,
                "is_submitted": int(review.is_submitted),
                "submitted_at": review.submitted_at
            })
            self.db.commit()
            return self.get(review.get_submission_id(), review.get_reviewer_student_id())
        except sqlite3.Error:
            self.db.rollback()
            return None

    def delete(self, submission_id: int, reviewer_student_id: int):
        try:
            self.db.execute("DELETE FROM peer_reviews WHERE submission_id = :sid AND reviewer_student_id = :rid", {"sid": submission_id, "rid": reviewer_student_id})
            self.db.commit()
            return True
        except sqlite3.Error:
            self.db.rollback()
            return False

    def list_by_submission(self, submission_id: int):
        query = """
            SELECT *
            FROM peer_reviews
            WHERE submission_id = :sid
            ORDER BY created_at DESC
        """
        result = self.db.execute(query, {"sid": submission_id})
        rows = result.fetchall()
        reviews = []
        for row in rows:
            rubric = json.loads(row.rubric_scores) if row.rubric_scores else None
            reviews.append(PeerReview(
                submission_id=row.submission_id,
                reviewer_student_id=row.reviewer_student_id,
                rubric_score=rubric,
                comments=row.comments,
                is_submitted=row.is_submitted,
                submitted_at=row.submitted_at,
                created_at=row.created_at
            ))
        return reviews

    def list_by_reviewer(self, reviewer_student_id: int):
        query = """
            SELECT *
            FROM peer_reviews
            WHERE reviewer_student_id = :rid
            ORDER BY created_at DESC
        """
        result = self.db.execute(query, {"rid": reviewer_student_id})
        rows = result.fetchall()
        reviews = []
        for row in rows:
            rubric = json.loads(row.rubric_scores) if row.rubric_scores else None
            reviews.append(PeerReview(
                submission_id=row.submission_id,
                reviewer_student_id=row.reviewer_student_id,
                rubric_score=rubric,
                comments=row.comments,
                is_submitted=row.is_submitted,
                submitted_at=row.submitted_at,
                created_at=row.created_at
            ))
        return reviews
