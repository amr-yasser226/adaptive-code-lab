from sqlalchemy.exc import SQLAlchemyError
from Model.Submission_model import Submission

class Submission_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT 
                id, assignment_id, student_id, version, language,
                status, score, is_late, created_at,
                updated_at, grade_at
            FROM submissions
            WHERE id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Submission(
            id=row.id,
            assignment_id=row.assignment_id,
            student_id=row.student_id,
            version=row.version,
            language=row.language,
            status=row.status,
            score=row.score,
            is_late=row.is_late,
            created_at=row.created_at,
            updated_at=row.updated_at,
            grade_at=row.grade_at
        )

    def create(self, submission: Submission):
        try:
            self.db.begin_transaction()
            query = """
                INSERT INTO submissions (
                    assignment_id, student_id, version, language,
                    status, score, is_late, created_at,
                    updated_at, grade_at
                )
                VALUES (
                    :assignment_id, :student_id, :version, :language,
                    :status, :score, :is_late, CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP, :grade_at
                )
            """
            self.db.execute(query, {
                "assignment_id": submission.get_assignment_id(),
                "student_id": submission.get_student_id(),
                "version": submission.version,
                "language": submission.language,
                "status": submission.status,
                "score": submission.score,
                "is_late": int(submission.is_late),
                "grade_at": submission.grade_at
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone().id
            self.db.commit()
            return self.get_by_id(new_id)
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def update(self, submission: Submission):
        try:
            self.db.begin_transaction()
            query = """
                UPDATE submissions
                SET 
                    version = :version,
                    language = :language,
                    status = :status,
                    score = :score,
                    is_late = :is_late,
                    updated_at = CURRENT_TIMESTAMP,
                    grade_at = :grade_at
                WHERE id = :id
            """
            self.db.execute(query, {
                "id": submission.get_id(),
                "version": submission.version,
                "language": submission.language,
                "status": submission.status,
                "score": submission.score,
                "is_late": int(submission.is_late),
                "grade_at": submission.grade_at
            })
            self.db.commit()
            return self.get_by_id(submission.get_id())
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def delete(self, id: int):
        try:
            self.db.begin_transaction()
            self.db.execute("DELETE FROM submissions WHERE id = :id", {"id": id})
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            return False

    def list_by_assignment(self, assignment_id: int):
        query = """
            SELECT *
            FROM submissions
            WHERE assignment_id = :aid
            ORDER BY created_at DESC
        """
        result = self.db.execute(query, {"aid": assignment_id})
        rows = result.fetchall()
        return [
            Submission(
                id=row.id,
                assignment_id=row.assignment_id,
                student_id=row.student_id,
                version=row.version,
                language=row.language,
                status=row.status,
                score=row.score,
                is_late=row.is_late,
                created_at=row.created_at,
                updated_at=row.updated_at,
                grade_at=row.grade_at
            )
            for row in rows
        ]

    def list_by_student(self, student_id: int):
        query = """
            SELECT *
            FROM submissions
            WHERE student_id = :sid
            ORDER BY created_at DESC
        """
        result = self.db.execute(query, {"sid": student_id})
        rows = result.fetchall()
        return [
            Submission(
                id=row.id,
                assignment_id=row.assignment_id,
                student_id=row.student_id,
                version=row.version,
                language=row.language,
                status=row.status,
                score=row.score,
                is_late=row.is_late,
                created_at=row.created_at,
                updated_at=row.updated_at,
                grade_at=row.grade_at
            )
            for row in rows
        ]
