from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from core.entities.user import User
from core.exceptions.auth_error import AuthError

class AuthService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hash a password using Werkzeug's secure hashing (pbkdf2:sha256 with salt)."""
        return generate_password_hash(plain_password)

    @staticmethod
    def verify_password(plain_password: str, stored_hash: str) -> bool:
        """Verify a plain password against a stored hash."""
        return check_password_hash(stored_hash, plain_password)

   
    def register(self, name: str, email: str, password: str, role="student"):
 
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise AuthError("Email already registered")

        hashed_pw = self.hash_password(password)

        user = User(
            id=None,
            name=name,
            email=email,
            password=hashed_pw,
            role=role,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )

        created = self.user_repo.save_user(user)
        if not created:
            raise AuthError("Failed to create user")

        return created

    def login(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)

        if not user:
            raise AuthError("Invalid credentials")

        if not user.is_active:
            raise AuthError("Account is deactivated")

        stored_hash = user.get_password_hash()
        is_valid = self.verify_password(password, stored_hash)

        if not is_valid:
            raise AuthError("Invalid credentials")

        return user


    def require_role(self, user: User, allowed_roles):
        if user.role not in allowed_roles:
            raise AuthError("Permission denied")
