from sqlalchemy.exc import SQLAlchemyError
from core.entities.assignment import Assignment

class AssignmentRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT 
                id, course_id, title, description, 
                release_date, due_date, max_points,
                is_published, allow_late_submissions,
                late_submission_penalty,
                created_at, updated_at
            FROM assignments
            WHERE id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Assignment(
            id=row.id,
            course_id=row.course_id,
            title=row.title,
            description=row.description,
            release_date=row.release_date,
            due_date=row.due_date,
            max_points=row.max_points,
            is_published=row.is_published,
            allow_late_submissions=row.allow_late_submissions,
            late_submission_penalty=row.late_submission_penalty,
            created_at=row.created_at,
            updated_at=row.updated_at
        )

    def create(self, assignment: Assignment):
        try:
            query = """
                INSERT INTO assignments (
                    course_id, title, description, release_date,
                    due_date, max_points, is_published,
                    allow_late_submissions, late_submission_penalty,
                    created_at, updated_at
                )
                VALUES (
                    :course_id, :title, :description, :release_date,
                    :due_date, :max_points, :is_published,
                    :allow_late_submissions, :late_submission_penalty,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """
            self.db.execute(query, {
                "course_id": assignment.get_course_id(),
                "title": assignment.title,
                "description": assignment.description,
                "release_date": assignment.release_date,
                "due_date": assignment.due_date,
                "max_points": assignment.max_points,
                "is_published": int(assignment.is_published),
                "allow_late_submissions": int(assignment.allow_late_submissions),
                "late_submission_penalty": assignment.late_submission_penalty,
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone()[0]
            self.db.commit()
            return self.get_by_id(new_id)
        except Exception as e:
            self.db.rollback()
            print("Error creating assignment:", e)
            return None

    def update(self, assignment: Assignment):
        try:
            query = """
                UPDATE assignments
                SET 
                    title = :title,
                    description = :description,
                    release_date = :release_date,
                    due_date = :due_date,
                    max_points = :max_points,
                    is_published = :is_published,
                    allow_late_submissions = :allow_late,
                    late_submission_penalty = :penalty,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(query, {
                "id": assignment.get_id(),
                "title": assignment.title,
                "description": assignment.description,
                "release_date": assignment.release_date,
                "due_date": assignment.due_date,
                "max_points": assignment.max_points,
                "is_published": int(assignment.is_published),
                "allow_late": int(assignment.allow_late_submissions),
                "penalty": assignment.late_submission_penalty,
            })
            self.db.commit()
            return self.get_by_id(assignment.get_id())
        except Exception as e:
            self.db.rollback()
            print("Error updating assignment:", e)
            return None

    def publish(self, id: int):
        try:
            query = """
                UPDATE assignments
                SET is_published = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(query, {"id": id})
            self.db.commit()
            return self.get_by_id(id)
        except Exception as e:
            self.db.rollback()
            print("Error publishing assignment:", e)
            return None

    def unpublish(self, id: int):
        try:
            query = """
                UPDATE assignments
                SET is_published = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(query, {"id": id})
            self.db.commit()
            return self.get_by_id(id)
        except Exception as e:
            self.db.rollback()
            print("Error unpublishing assignment:", e)
            return None

    def extend_deadline(self, id: int, new_due_date):
        try:
            query = """
                UPDATE assignments
                SET due_date = :due, updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(query, {"id": id, "due": new_due_date})
            self.db.commit()
            return self.get_by_id(id)
        except Exception as e:
            self.db.rollback()
            print("Error extending deadline:", e)
            return None

    def list_by_course(self, course_id: int):
        query = """
            SELECT *
            FROM assignments
            WHERE course_id = :course_id
            ORDER BY release_date DESC
        """
        result = self.db.execute(query, {"course_id": course_id})
        rows = result.fetchall()
        return [
            Assignment(
                id=row.id,
                course_id=row.course_id,
                title=row.title,
                description=row.description,
                release_date=row.release_date,
                due_date=row.due_date,
                max_points=row.max_points,
                is_published=row.is_published,
                allow_late_submissions=row.allow_late_submissions,
                late_submission_penalty=row.late_submission_penalty,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            for row in rows
        ]

    def get_all(self):
        query = """
            SELECT *
            FROM assignments
            ORDER BY release_date DESC
        """
        result = self.db.execute(query)
        rows = result.fetchall()
        return [
            Assignment(
                id=row.id,
                course_id=row.course_id,
                title=row.title,
                description=row.description,
                release_date=row.release_date,
                due_date=row.due_date,
                max_points=row.max_points,
                is_published=row.is_published,
                allow_late_submissions=row.allow_late_submissions,
                late_submission_penalty=row.late_submission_penalty,
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            for row in rows
        ]
