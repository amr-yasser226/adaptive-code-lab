from sqlalchemy.exc import SQLAlchemyError
from core.entities.admin import Admin

class Admin_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT
                u.id, u.name, u.email, u.password_hash, u.role,
                u.created_at, u.updated_at, u.is_active,
                a.privileges
            FROM users u
            LEFT JOIN admins a ON u.id = a.id
            WHERE u.id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Admin(
            id=row.id,
            name=row.name,
            email=row.email,
            password=row.password_hash,
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_active=row.is_active,  # Changed from is_Active
            privileges=row.privileges
        )

    def save_admin(self, admin: Admin):
        try:

            if admin.get_id() is None:
                raise Exception("Admin must have a user ID before saving admin record")

            # ROLE CHECK
            role_row = self.db.execute("SELECT role FROM users WHERE id = :id", {"id": admin.get_id()}).fetchone()
            if not role_row:
                raise Exception("User does not exist")
            if role_row[0] != "admin":
                raise Exception("User role must be 'admin' to save admin record")

            # UPDATE USERS
            update_user_query = """
                UPDATE users
                SET name = :name,
                    email = :email,
                    password_hash = :password_hash,
                    role = 'admin',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(update_user_query, {
                "id": admin.get_id(),
                "name": admin.name,
                "email": admin.email,
                "password_hash": admin.get_password_hash() if hasattr(admin, "get_password_hash") else admin.password
            })

            # INSERT OR UPDATE ADMINS
            exists = self.db.execute("SELECT id FROM admins WHERE id = :id", {"id": admin.get_id()}).fetchone()
            if exists:
                update_admin = "UPDATE admins SET privileges = :privileges WHERE id = :id"
                self.db.execute(update_admin, {"id": admin.get_id(), "privileges": admin.privileges})
            else:
                insert_admin = "INSERT INTO admins (id, privileges) VALUES (:id, :privileges)"
                self.db.execute(insert_admin, {"id": admin.get_id(), "privileges": admin.privileges})

            self.db.commit()
            return self.get_by_id(admin.get_id())

        except SQLAlchemyError as e:
            self.db.rollback()
            print("Error saving admin:", e)
            return None
