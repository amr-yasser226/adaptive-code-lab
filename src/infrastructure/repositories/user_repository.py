from core.entities.user import User 
import sqlite3

class UserRepository:
    def __init__(self, db):
        self.db = db
    
    def get_by_id(self, id):
        """
        FIXED ISSUES:
        1. SQL injection vulnerability (used parameterized query)
        2. Duplicate 'role' parameter in User constructor
        3. Wrong column order mapping
        """
        query = "SELECT * FROM users WHERE id = :id"
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if row is None:
            return None
        # Correct column order: id, name, email, password_hash, role, is_active, created_at, updated_at
        return User(
            id=row[0],           # id
            name=row[1],         # name
            email=row[2],        # email
            password=row[3],     # password_hash
            role=row[4],         # role
            created_at=row[6],   # created_at
            updated_at=row[7],   # updated_at
            is_active=row[5]     # is_active
        )
    
    def get_by_email(self, email: str):
        """
        FIXED: SQL injection vulnerability
        """
        query = "SELECT * FROM users WHERE email = :email"
        result = self.db.execute(query, {"email": email})
        row = result.fetchone()
        if row is None:
            return None
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            password=row[3],
            role=row[4],
            created_at=row[6],
            updated_at=row[7],
            is_active=row[5]
        )
    
    def create(self, user: User):
        """
        Creates a new user record.
        """
        try:
            if user.get_id() is None:
                query = """
                    INSERT INTO users(name, email, password_hash, role, is_active)
                    VALUES (:name, :email, :password_hash, :role, :is_active)
                """
                self.db.execute(query, {
                    "name": user.name,
                    "email": user.email,
                    "password_hash": user.get_password_hash(),
                    "role": user.role,
                    "is_active": int(user.is_active)
                })
                
                new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone()[0]
                self.db.commit()
                return self.get_by_id(new_id)
        except sqlite3.Error:
            self.db.rollback()
            raise
    
    def delete(self, id: int):
        try:
            query = "DELETE FROM users WHERE id = :id"
            self.db.execute(query, {"id": id})
            self.db.commit()
        except sqlite3.Error:
            self.db.rollback()
            raise
    
    def list_all(self, filters: dict = None):
        base_query = "SELECT * FROM users"
        params = {}
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = :{key}")
                params[key] = value
            base_query += " WHERE " + " AND ".join(conditions)
        
        result = self.db.execute(base_query, params)
        users = []
        for row in result.fetchall():
            users.append(
                User(
                    id=row[0],
                    name=row[1],
                    email=row[2],
                    password=row[3],
                    role=row[4],
                    created_at=row[6],
                    updated_at=row[7],
                    is_active=row[5]
                )
            )
        return users
    
    def update(self, user: User):
        try:
            query = """
                UPDATE users
                SET 
                    name = :name,
                    email = :email,
                    password_hash = :password_hash,
                    role = :role,
                    is_active = :is_active,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """
            self.db.execute(query, {
                "id": user.get_id(),
                "name": user.name,
                "email": user.email,
                "password_hash": user.get_password_hash(),
                "role": user.role,
                "is_active": int(user.is_active)
            })
            
            self.db.commit()
            return self.get_by_id(user.get_id())
        except Exception as e:
            self.db.rollback()
            print("Error updating user:", e)
            return None