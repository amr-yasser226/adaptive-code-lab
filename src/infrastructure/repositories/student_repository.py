from sqlalchemy.exc import SQLAlchemyError
from core.entities.student import Student

class Student_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT 
                u.id, u.name, u.email, u.password_hash, u.role,
                u.created_at, u.updated_at, u.is_active,
                s.student_number, s.program, s.YearLevel
            FROM users u
            INNER JOIN students s ON u.id = s.id
            WHERE u.id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Student(
            id=row.id,
            name=row.name,
            email=row.email,
            password=row.password_hash,
            created_at=row.created_at,
            updated_at=row.updated_at,
            student_number=row.student_number,
            Program=row.program,  # Model still uses Program parameter
            year_Level=row.YearLevel,
            is_active=row.is_active  # Model still uses is_Active
        )

    def save_student(self, student: Student):
        try:
            self.db.begin_transaction()

            if student.get_id() is None:
                raise Exception("Student must have a user ID before saving student record")

            # ROLE CHECK
            role_row = self.db.execute("SELECT role FROM users WHERE id = :id", {"id": student.get_id()}).fetchone()
            if not role_row:
                raise Exception("User does not exist")
            if role_row[0] != "student":
                raise Exception("User role must be 'student' to save a student record")

            # UPDATE USERS
            update_user_query = """
                UPDATE users
                SET name = :name,
                    email = :email,
                    password_hash = :password_hash,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(update_user_query, {
                "id": student.get_id(),
                "name": student.name,
                "email": student.email,
                "password_hash": student.get_password_hash(),
            })

            # INSERT OR UPDATE STUDENTS
            exists = self.db.execute("SELECT id FROM students WHERE id = :id", {"id": student.get_id()}).fetchone()
            if exists:
                update_student = """
                    UPDATE students
                    SET student_number = :num,
                        program = :program,
                        YearLevel = :year
                    WHERE id = :id
                """
                self.db.execute(update_student, {
                    "id": student.get_id(),
                    "num": student.student_number,
                    "program": student.program,
                    "year": student.year_Level
                })
            else:
                insert_student = """
                    INSERT INTO students (id, student_number, program, YearLevel)
                    VALUES (:id, :num, :program, :year)
                """
                self.db.execute(insert_student, {
                    "id": student.get_id(),
                    "num": student.student_number,
                    "program": student.program,
                    "year": student.year_Level
                })

            self.db.commit()
            return self.get_by_id(student.get_id())

        except Exception as e:
            self.db.rollback()
            print("Error saving student:", e)
            raise # Re-raise the exception instead of returning None

    def find_by_number(self, student: Student):
        query = """
            SELECT 
                u.id, u.name, u.email, u.password_hash, u.role,
                u.created_at, u.updated_at, u.is_active,
                s.student_number, s.program, s.YearLevel
            FROM users u
            INNER JOIN students s ON u.id = s.id
            WHERE s.student_number = :num
        """
        result = self.db.execute(query, {"num": student.student_number})
        row = result.fetchone() if result else None
        if not row:
            return None
        return Student(
            id=row.id,
            name=row.name,
            email=row.email,
            password=row.password_hash,
            created_at=row.created_at,
            updated_at=row.updated_at,
            student_number=row.student_number,
            Program=row.program,
            year_Level=row.YearLevel,
            is_active=row.is_active
        )
