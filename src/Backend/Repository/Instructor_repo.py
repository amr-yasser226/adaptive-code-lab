from sqlalchemy.exc import SQLAlchemyError
from Backend.Model.Instructor_model import Instructor

class Instructor_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT 
                u.id, u.name, u.email, u.password_hash, u.role,
                u.created_at, u.updated_at, u.is_active,
                i.instructor_code, i.bio, i.office_hours
            FROM users u
            INNER JOIN instructors i ON u.id = i.id
            WHERE u.id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Instructor(
            id=row.id,
            name=row.name,
            email=row.email,
            password=row.password_hash,
            created_at=row.created_at,
            updated_at=row.updated_at,
            instructor_code=row.instructor_code,
            bio=row.bio,
            office_hours=row.office_hours,
            is_active=row.is_active  # Changed from is_Active 
        )

    def get_by_code(self, instructor_code: str):
        query = """
            SELECT 
                u.id, u.name, u.email, u.password_hash, u.role,
                u.created_at, u.updated_at, u.is_active,
                i.instructor_code, i.bio, i.office_hours
            FROM users u
            INNER JOIN instructors i ON u.id = i.id
            WHERE i.instructor_code = :code
        """
        result = self.db.execute(query, {"code": instructor_code})
        row = result.fetchone() if result else None
        if not row:
            return None
        return Instructor(
            id=row.id,
            name=row.name,
            email=row.email,
            password=row.password_hash,
            created_at=row.created_at,
            updated_at=row.updated_at,
            instructor_code=row.instructor_code,
            bio=row.bio,
            office_hours=row.office_hours,
            is_active=row.is_active # Changed from is_Active
        )

    def save(self, instructor: Instructor):
        try:
            self.db.begin_transaction()

            # ROLE CHECK
            role_row = self.db.execute("SELECT role FROM users WHERE id = :id", {"id": instructor.get_id()}).fetchone()
            if not role_row:
                raise Exception("User does not exist")
            if role_row[0] != "instructor":
                raise Exception("User role must be 'instructor' to save instructor record")

            # UPDATE USERS
            update_user = """
                UPDATE users
                SET name = :name,
                    email = :email,
                    password_hash = :password_hash,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(update_user, {
                "id": instructor.get_id(),
                "name": instructor.name,
                "email": instructor.email,
                "password_hash": instructor.get_password_hash(),
            })

            # INSERT OR UPDATE INSTRUCTORS
            exists = self.db.execute("SELECT id FROM instructors WHERE id = :id", {"id": instructor.get_id()}).fetchone()
            if exists:
                update_instructor = """
                    UPDATE instructors
                    SET instructor_code = :code,
                        bio = :bio,
                        office_hours = :hours
                    WHERE id = :id
                """
                self.db.execute(update_instructor, {
                    "id": instructor.get_id(),
                    "code": instructor.instructor_code,
                    "bio": instructor.bio,
                    "hours": instructor.office_hours
                })
            else:
                insert_instructor = """
                    INSERT INTO instructors (id, instructor_code, bio, office_hours)
                    VALUES (:id, :code, :bio, :hours)
                """
                self.db.execute(insert_instructor, {
                    "id": instructor.get_id(),
                    "code": instructor.instructor_code,
                    "bio": instructor.bio,
                    "hours": instructor.office_hours
                })

            self.db.commit()
            return self.get_by_id(instructor.get_id())

        except Exception as e:
            self.db.rollback()
            print("Error saving instructor:", e)
            return None