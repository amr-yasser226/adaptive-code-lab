from datetime import datetime
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError
from core.entities.user import User


class UserService:
    def __init__(self, user_repo):
        self.user_repo = user_repo

    # -------------------------------------------------
    # CREATE USER (REGISTER)
    # -------------------------------------------------
    def register_user(self, name, email, password, role="student"):
        if not name or not email or not password:
            raise ValidationError("Name, email, and password are required")

        # Check if email already exists
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValidationError("Email already registered")

        user = User(
            id=None,
            name=name,
            email=email,
            password=None,
            role=role,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True
        )

        # hash password safely
        user.set_password(password)

        return self.user_repo.save_user(user)

    # -------------------------------------------------
    # AUTHENTICATION
    # -------------------------------------------------
    def authenticate(self, email, password):
        user = self.user_repo.get_by_email(email)
        if not user:
            raise AuthError("Invalid email or password")

        if not user.is_active:
            raise AuthError("Account is deactivated")

        if not user.authenticate_password(password):
            raise AuthError("Invalid email or password")

        return user

    # -------------------------------------------------
    # GET USER
    # -------------------------------------------------
    def get_user(self, user_id):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
        return user

    # -------------------------------------------------
    # UPDATE PROFILE (SELF)
    # -------------------------------------------------
    def update_profile(self, user, name=None, email=None, password=None):
        if not user.is_active:
            raise AuthError("Inactive accounts cannot be updated")

        if email:
            existing = self.user_repo.get_by_email(email)
            if existing and existing.get_id() != user.get_id():
                raise ValidationError("Email already in use")

        user.update_profile(
            name=name,
            email=email,
            password=password
        )

        return self.user_repo.Update_data(user)

    # -------------------------------------------------
    # ADMIN: UPDATE USER ROLE
    # -------------------------------------------------
    def update_user_role(self, admin, user_id, new_role):
        if admin.role != "admin":
            raise AuthError("Only admins can change user roles")

        user = self.get_user(user_id)
        user.role = new_role

        return self.user_repo.Update_data(user)

    # -------------------------------------------------
    # ADMIN: ACTIVATE / DEACTIVATE
    # -------------------------------------------------
    def deactivate_user(self, admin, user_id):
        if admin.role != "admin":
            raise AuthError("Only admins can deactivate users")

        user = self.get_user(user_id)
        user.deactivate_account()

        return self.user_repo.Update_data(user)

    def activate_user(self, admin, user_id):
        if admin.role != "admin":
            raise AuthError("Only admins can activate users")

        user = self.get_user(user_id)
        user.activate_account()

        return self.user_repo.Update_data(user)

    # -------------------------------------------------
    # ADMIN: LIST USERS
    # -------------------------------------------------
    def list_users(self, admin, filters=None):
        if admin.role != "admin":
            raise AuthError("Only admins can list users")

        return self.user_repo.findALL(filters)
