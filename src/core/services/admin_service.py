import shutil
from datetime import datetime

from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


class AdminService:
    def __init__(
        self,
        user_repo,
        admin_repo,
        course_repo=None,
        enrollment_repo=None,
        submission_repo=None,
        db_path=None
    ):
        self.user_repo = user_repo
        self.admin_repo = admin_repo
        self.course_repo = course_repo
        self.enrollment_repo = enrollment_repo
        self.submission_repo = submission_repo
        self.db_path = db_path

    def _ensure_admin(self, user):
        if not user or user.role != "admin":
            raise AuthError("Admin privileges required")

    def manage_user_account(self, admin_user, target_user_id, action):
        """
        action: activate | deactivate | delete
        """
        self._ensure_admin(admin_user)

        user = self.user_repo.get_by_id(target_user_id)
        if not user:
            raise ValidationError("User not found")

        if action == "activate":
            user.activate_account()
            return self.user_repo.update(user)


        if action == "deactivate":
            user.deactivate_account()
            return self.user_repo.update(user)


        if action == "delete":
            self.user_repo.delete(target_user_id)
            return True

        raise ValidationError("Invalid action. Use activate, deactivate, or delete.")


    def generate_report(self, admin_user, report_type):
        """
        report_type: users | courses | enrollments | submissions
        """
        self._ensure_admin(admin_user)

        if report_type == "users":
            return self.user_repo.list_all()


        if report_type == "courses" and self.course_repo:
            return self.course_repo.list_all()

        if report_type == "enrollments" and self.enrollment_repo:
            return self.enrollment_repo.list_all()

        if report_type == "submissions" and self.submission_repo:
            return self.submission_repo.get_all()

        raise ValidationError("Invalid or unsupported report type")

   
    def configure_system_setting(self, admin_user, key, value, settings_repo=None):
        self._ensure_admin(admin_user)

        if not key:
            raise ValidationError("Setting key is required")

        if settings_repo:
            return settings_repo.set(key, value)

        # fallback simple config
        return {
            "key": key,
            "value": value,
            "updated_at": datetime.utcnow()
        }


    def export_db_dump(self, admin_user, output_path):
        self._ensure_admin(admin_user)

        if not self.db_path:
            raise ValidationError("Database path not configured")

        try:
            shutil.copy(self.db_path, output_path)
            return {
                "status": "success",
                "output_path": output_path,
                "exported_at": datetime.utcnow()
            }
        except Exception as e:
            raise ValidationError(f"Database export failed: {e}")
