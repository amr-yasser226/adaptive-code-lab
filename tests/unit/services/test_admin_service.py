import pytest
from unittest.mock import Mock, MagicMock
from core.services.admin_service import AdminService
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_user_repo():
    return Mock()


@pytest.fixture
def mock_admin_repo():
    return Mock()


@pytest.fixture
def mock_course_repo():
    return Mock()


@pytest.fixture
def mock_enrollment_repo():
    return Mock()


@pytest.fixture
def mock_submission_repo():
    return Mock()


@pytest.fixture
def admin_service(mock_user_repo, mock_admin_repo, mock_course_repo, 
                  mock_enrollment_repo, mock_submission_repo):
    return AdminService(
        user_repo=mock_user_repo,
        admin_repo=mock_admin_repo,
        course_repo=mock_course_repo,
        enrollment_repo=mock_enrollment_repo,
        submission_repo=mock_submission_repo,
        db_path="/tmp/test.db"
    )


@pytest.fixture
def admin_user():
    user = Mock()
    user.role = "admin"
    user.get_id.return_value = 1
    return user


@pytest.fixture
def non_admin_user():
    user = Mock()
    user.role = "student"
    user.get_id.return_value = 2
    return user


class TestAdminService:
    """Test suite for AdminService"""

    def test_ensure_admin_raises_for_non_admin(self, admin_service, non_admin_user):
        """Non-admin users should be rejected"""
        with pytest.raises(AuthError, match="Admin privileges required"):
            admin_service._ensure_admin(non_admin_user)

    def test_ensure_admin_passes_for_admin(self, admin_service, admin_user):
        """Admin users should pass validation"""
        # Should not raise
        admin_service._ensure_admin(admin_user)

    def test_manage_user_account_activate(self, admin_service, admin_user, mock_user_repo):
        """Test activating a user account"""
        target_user = Mock()
        mock_user_repo.get_by_id.return_value = target_user
        mock_user_repo.Update_data.return_value = target_user

        result = admin_service.manage_user_account(admin_user, 2, "activate")

        target_user.activate_account.assert_called_once()
        mock_user_repo.Update_data.assert_called_once_with(target_user)

    def test_manage_user_account_deactivate(self, admin_service, admin_user, mock_user_repo):
        """Test deactivating a user account"""
        target_user = Mock()
        mock_user_repo.get_by_id.return_value = target_user
        mock_user_repo.Update_data.return_value = target_user

        result = admin_service.manage_user_account(admin_user, 2, "deactivate")

        target_user.deactivate_account.assert_called_once()

    def test_manage_user_account_delete(self, admin_service, admin_user, mock_user_repo):
        """Test deleting a user account"""
        target_user = Mock()
        mock_user_repo.get_by_id.return_value = target_user

        result = admin_service.manage_user_account(admin_user, 2, "delete")

        mock_user_repo.delete.assert_called_once_with(2)
        assert result is True

    def test_manage_user_account_user_not_found(self, admin_service, admin_user, mock_user_repo):
        """User not found should raise ValidationError"""
        mock_user_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="User not found"):
            admin_service.manage_user_account(admin_user, 999, "activate")

    def test_manage_user_account_invalid_action(self, admin_service, admin_user, mock_user_repo):
        """Invalid action should raise ValidationError"""
        target_user = Mock()
        mock_user_repo.get_by_id.return_value = target_user

        with pytest.raises(ValidationError, match="Invalid action"):
            admin_service.manage_user_account(admin_user, 2, "invalid")

    def test_manage_user_account_non_admin_denied(self, admin_service, non_admin_user):
        """Non-admin users cannot manage accounts"""
        with pytest.raises(AuthError, match="Admin privileges required"):
            admin_service.manage_user_account(non_admin_user, 2, "activate")

    def test_generate_report_users(self, admin_service, admin_user, mock_user_repo):
        """Test generating users report"""
        users = [Mock(), Mock()]
        mock_user_repo.findALL.return_value = users

        result = admin_service.generate_report(admin_user, "users")

        assert result == users

    def test_generate_report_courses(self, admin_service, admin_user, mock_course_repo):
        """Test generating courses report"""
        courses = [Mock(), Mock()]
        mock_course_repo.list_all.return_value = courses

        result = admin_service.generate_report(admin_user, "courses")

        assert result == courses

    def test_generate_report_invalid_type(self, admin_service, admin_user):
        """Invalid report type should raise ValidationError"""
        with pytest.raises(ValidationError, match="Invalid or unsupported report type"):
            admin_service.generate_report(admin_user, "invalid")

    def test_configure_system_setting(self, admin_service, admin_user):
        """Test configuring system setting without settings_repo"""
        result = admin_service.configure_system_setting(admin_user, "theme", "dark")

        assert result["key"] == "theme"
        assert result["value"] == "dark"

    def test_configure_system_setting_empty_key(self, admin_service, admin_user):
        """Empty key should raise ValidationError"""
        with pytest.raises(ValidationError, match="Setting key is required"):
            admin_service.configure_system_setting(admin_user, "", "value")

    def test_export_db_dump_success(self, admin_service, admin_user, tmp_path):
        """Test successful database export"""
        # Create a mock source db file
        import os
        admin_service.db_path = str(tmp_path / "source.db")
        with open(admin_service.db_path, "w") as f:
            f.write("test")

        output_path = str(tmp_path / "backup.db")
        result = admin_service.export_db_dump(admin_user, output_path)

        assert result["status"] == "success"
        assert os.path.exists(output_path)

    def test_export_db_dump_no_db_path(self, admin_user, mock_user_repo, mock_admin_repo):
        """Export without db_path configured should raise ValidationError"""
        service = AdminService(mock_user_repo, mock_admin_repo, db_path=None)

        with pytest.raises(ValidationError, match="Database path not configured"):
            service.export_db_dump(admin_user, "/tmp/backup.db")
