import sqlite3
from core.entities.enrollment import Enrollment

class EnrollmentRepository:
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
            student_id=row[0],
            course_id=row[1],
            status=row[2],
            final_grade=row[3],
            enrolled_at=row[4],
            dropped_at=row[5]
        )

    def enroll(self, enrollment: Enrollment):
        try:
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
        except sqlite3.Error as e:
            self.db.rollback()
            raise e

    def update(self, enrollment: Enrollment):
        try:
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
        except sqlite3.Error as e:
            self.db.rollback()
            raise e

    def delete(self, student_id: int, course_id: int):
        try:
            self.db.execute(
                "DELETE FROM enrollments WHERE student_id = :sid AND course_id = :cid",
                {"sid": student_id, "cid": course_id}
            )
            self.db.commit()
            return True
        except sqlite3.Error:
            self.db.rollback()
            return False

    def list_by_student(self, student_id: int):
        query = """
            SELECT student_id, course_id, status, final_grade, enrolled_at, dropped_at
            FROM enrollments
            WHERE student_id = :sid
        """
        result = self.db.execute(query, {"sid": student_id})
        rows = result.fetchall()
        return [
            Enrollment(
                student_id=row[0],
                course_id=row[1],
                status=row[2],
                final_grade=row[3],
                enrolled_at=row[4],
                dropped_at=row[5]
            )
            for row in rows
        ]

    def list_by_course(self, course_id: int):
        query = """
            SELECT student_id, course_id, status, final_grade, enrolled_at, dropped_at
            FROM enrollments
            WHERE course_id = :cid
        """
        result = self.db.execute(query, {"cid": course_id})
        rows = result.fetchall()
        return [
            Enrollment(
                student_id=row[0],
                course_id=row[1],
                status=row[2],
                final_grade=row[3],
                enrolled_at=row[4],
                dropped_at=row[5]
            )
            for row in rows
        ]
    

    def list_all(self):
        query = """
            SELECT student_id, course_id, status, final_grade, enrolled_at, dropped_at
            FROM enrollments
            ORDER BY enrolled_at DESC
        """
        result = self.db.execute(query)
        rows = result.fetchall()

        return [
            Enrollment(
                student_id=row[0],
                course_id=row[1],
                status=row[2],
                final_grade=row[3],
                enrolled_at=row[4],
                dropped_at=row[5]
            )
            for row in rows
        ]
