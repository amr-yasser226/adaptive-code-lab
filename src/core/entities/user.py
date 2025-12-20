from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id, name, email, password, role, created_at=None, updated_at=None, is_active=True, bio=None):
        self.__id = id
        self.name = name
        self.email = email
        self.__password_hash = password
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_active = bool(is_active)
        self.bio = bio

    def get_id(self):
        return self.__id
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using Werkzeug's secure hashing (pbkdf2:sha256 with salt)."""
        return generate_password_hash(password)

    def set_password(self, password: str):
        """Set a new password (will be securely hashed)."""
        self.__password_hash = User.hash_password(password)
    
    def get_password_hash(self) -> str:
        return self.__password_hash
    
    def authenticate_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.get_password_hash(), password)
    
    def update_profile(self, name=None, email=None, role=None, password=None):
        if name:
            self.name = name
        if email:
            self.email = email
        if role:
            self.role = role
        if password:
            self.set_password(password)

    def deactivate_account(self):
        self.is_active = False  # FIXED: was self.is_Active
    
    def activate_account(self):
        self.is_active = True  # FIXED: was self.is_Active