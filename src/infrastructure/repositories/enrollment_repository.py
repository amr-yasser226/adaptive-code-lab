from sqlalchemy.exc import SQLAlchemyError
from core.entities.enrollment import Enrollment

class Enrollment_repo:
    def __init__(self, db):
        self.db = db

    def get(self, student_id: int, course_id: int):
        query = """
            SELECT
                student_id, course_id, status,
                final_grade, enrolled_at, dropped_at
            FROM enrollments
            WHERE student_id = :sid AND course_id = :cid
        """
        result = self.db.execute(query, {"sid": student_id, "cid": course_id})
        row = result.fetchone()
        if not row:
            return None
        return Enrollment(
            student_id=row.student_id,
            course_id=row.course_id,
            status=row.status,
            final_grade=row.final_grade,
            enrolled_at=row.enrolled_at,
            dropped_at=row.dropped_at
        )

    def enroll(self, enrollment: Enrollment):
        try:
            self.db.begin_transaction()
            query = """
                INSERT INTO enrollments (
                    student_id, course_id, status,
                    final_grade, enrolled_at, dropped_at
                )
                VALUES (
                    :student_id, :course_id, :status,
                    :final_grade, :enrolled_at, :dropped_at
                )
            """
            self.db.execute(query, {
                "student_id": enrollment.get_student_id(),
                "course_id": enrollment.get_course_id(),
                "status": enrollment.status,
                "final_grade": enrollment.final_grade,
                "enrolled_at": enrollment.enrolled_at,
                "dropped_at": enrollment.dropped_at
            })
            self.db.commit()
            return self.get(enrollment.get_student_id(), enrollment.get_course_id())
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def update(self, enrollment: Enrollment):
        try:
            self.db.begin_transaction()
            query = """
                UPDATE enrollments
                SET
                    status = :status,
                    final_grade = :final_grade,
                    enrolled_at = :enrolled_at,
                    dropped_at = :dropped_at
                WHERE student_id = :student_id AND course_id = :course_id
            """
            self.db.execute(query, {
                "student_id": enrollment.get_student_id(),
                "course_id": enrollment.get_course_id(),
                "status": enrollment.status,
                "final_grade": enrollment.final_grade,
                "enrolled_at": enrollment.enrolled_at,
                "dropped_at": enrollment.dropped_at
            })
            self.db.commit()
            return self.get(enrollment.get_student_id(), enrollment.get_course_id())
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def delete(self, student_id: int, course_id: int):
        try:
            self.db.begin_transaction()
            self.db.execute(
                "DELETE FROM enrollments WHERE student_id = :sid AND course_id = :cid",
                {"sid": student_id, "cid": course_id}
            )
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            return False

    def list_by_student(self, student_id: int):
        query = """
            SELECT *
            FROM enrollments
            WHERE student_id = :sid
        """
        result = self.db.execute(query, {"sid": student_id})
        rows = result.fetchall()
        return [
            Enrollment(
                student_id=row.student_id,
                course_id=row.course_id,
                status=row.status,
                final_grade=row.final_grade,
                enrolled_at=row.enrolled_at,
                dropped_at=row.dropped_at
            )
            for row in rows
        ]

    def list_by_course(self, course_id: int):
        query = """
            SELECT *
            FROM enrollments
            WHERE course_id = :cid
        """
        result = self.db.execute(query, {"cid": course_id})
        rows = result.fetchall()
        return [
            Enrollment(
                student_id=row.student_id,
                course_id=row.course_id,
                status=row.status,
                final_grade=row.final_grade,
                enrolled_at=row.enrolled_at,
                dropped_at=row.dropped_at
            )
            for row in rows
        ]
