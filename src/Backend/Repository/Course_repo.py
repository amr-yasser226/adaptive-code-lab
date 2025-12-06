from sqlalchemy.exc import SQLAlchemyError
from Model.Course_model import Course

class Course_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT 
                id, instructor_id, code, title, description,
                year, semester, max_students, created_at,
                status, updated_at, credits
            FROM courses
            WHERE id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Course(
            id=row.id,
            instructor_id=row.instructor_id,
            code=row.code,
            title=row.title,
            describtion=row.description,
            year=row.year,
            semester=row.semester,
            max_students=row.max_students,
            created_at=row.created_at,
            status=row.status,
            updated_at=row.updated_at,
            credits=row.credits
        )

    def create(self, course: Course):
        try:
            self.db.begin_transaction()
            query = """
                INSERT INTO courses (
                    instructor_id, code, title, description,
                    year, semester, max_students, created_at,
                    status, updated_at, credits
                )
                VALUES (
                    :instructor_id, :code, :title, :description,
                    :year, :semester, :max_students, CURRENT_TIMESTAMP,
                    :status, CURRENT_TIMESTAMP, :credits
                )
            """
            self.db.execute(query, {
                "instructor_id": course.get_instructor_id(),
                "code": course.code,
                "title": course.title,
                "description": course.describtion,
                "year": course.year,
                "semester": course.semester,
                "max_students": course.max_students,
                "status": course.status,
                "credits": course.credits
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone().id
            self.db.commit()
            return self.get_by_id(new_id)
        except Exception as e:
            self.db.rollback()
            print("Error creating course:", e)
            return None

    def update(self, course: Course):
        """
        FIXED: get_if() -> get_id()
        """
        try:
            self.db.begin_transaction()
            query = """
                UPDATE courses
                SET 
                    instructor_id = :instructor_id,
                    code = :code,
                    title = :title,
                    description = :description,
                    year = :year,
                    semester = :semester,
                    max_students = :max_students,
                    status = :status,
                    credits = :credits,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(query, {
                "id": course.get_id(),
                "instructor_id": course.get_instructor_id(),
                "code": course.code,
                "title": course.title,
                "description": course.describtion,
                "year": course.year,
                "semester": course.semester,
                "max_students": course.max_students,
                "status": course.status,
                "credits": course.credits
            })
            self.db.commit()
            return self.get_by_id(course.get_id())  # FIXED: was get_if()
        except Exception as e:
            self.db.rollback()
            print("Error updating course:", e)
            return None

    def publish(self, id: int):
        try:
            self.db.begin_transaction()
            query = """
                UPDATE courses
                SET status = 'active', updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(query, {"id": id})
            self.db.commit()
            return self.get_by_id(id)
        except Exception as e:
            self.db.rollback()
            print("Error publishing course:", e)
            return None

    def archive(self, id: int):
        try:
            self.db.begin_transaction()
            query = """
                UPDATE courses
                SET status = 'inactive', updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(query, {"id": id})
            self.db.commit()
            return self.get_by_id(id)
        except Exception as e:
            self.db.rollback()
            print("Error archiving course:", e)
            return None

    def list_by_instructor(self, instructor_id: int):
        """
        FIXED: Argument order was swapped
        """
        query = """
            SELECT *
            FROM courses
            WHERE instructor_id = :instructor_id
            ORDER BY created_at DESC
        """
        # FIXED: was execute({"instructor_id": instructor_id}, query)
        result = self.db.execute(query, {"instructor_id": instructor_id})
        rows = result.fetchall()
        return [
            Course(
                id=row.id,
                instructor_id=row.instructor_id,
                code=row.code,
                title=row.title,
                describtion=row.description,
                year=row.year,
                semester=row.semester,
                max_students=row.max_students,
                created_at=row.created_at,
                status=row.status,
                updated_at=row.updated_at,
                credits=row.credits
            ) for row in rows
        ]