import pytest
from unittest.mock import Mock, MagicMock
from core.services.auth_service import AuthService
from core.entities.user import User
from core.exceptions.auth_error import AuthError

@pytest.fixture
def mock_user_repo():
    return Mock()

@pytest.fixture
def auth_service(mock_user_repo):
    return AuthService(mock_user_repo)

def test_register_success(auth_service, mock_user_repo):
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = True
    
    result = auth_service.register("Test User", "test@example.com", "password")
    
    assert result is True
    mock_user_repo.create.assert_called_once()
    args, _ = mock_user_repo.create.call_args
    user = args[0]
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.role == "student"
    assert user.get_password_hash() != "password" # Should be hashed


def test_register_duplicate_email(auth_service, mock_user_repo):
    existing_user = Mock(spec=User)
    mock_user_repo.get_by_email.return_value = existing_user
    
    with pytest.raises(AuthError, match="Email already registered"):
        auth_service.register("Test User", "test@example.com", "password")
        
    mock_user_repo.create.assert_not_called()

def test_login_success(auth_service, mock_user_repo):
    user = MagicMock(spec=User)
    user.is_active = True
    # Setup mock hash behavior
    user.get_password_hash.return_value = "hashed_secret"
    
    mock_user_repo.get_by_email.return_value = user
    
    # We need to mock verify_password since it's a static method using check_password_hash
    # But since we are testing the service logic, let's mock check_password_hash in the module
    with pytest.MonkeyPatch.context() as m:
        m.setattr("core.services.auth_service.check_password_hash", lambda h, p: True)
        result = auth_service.login("test@example.com", "secret")
        assert result == user

def test_login_invalid_credentials_not_found(auth_service, mock_user_repo):
    mock_user_repo.get_by_email.return_value = None
    
    with pytest.raises(AuthError, match="Invalid credentials"):
        auth_service.login("test@example.com", "wrong")

def test_login_deactivated_account(auth_service, mock_user_repo):
    """Line 53: AuthError on deactivated account"""
    user = Mock(spec=User)
    user.is_active = False
    mock_user_repo.get_by_email.return_value = user
    with pytest.raises(AuthError, match="Account is deactivated"):
        auth_service.login("test@example.com", "password")

def test_register_failed_to_create(auth_service, mock_user_repo):
    """Line 42: AuthError when user repository fails to create user"""
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = None
    with pytest.raises(AuthError, match="Failed to create user"):
        auth_service.register("T", "t@e.com", "p")

def test_login_invalid_password(auth_service, mock_user_repo, monkeypatch):
    """Line 59: AuthError on password mismatch"""
    user = Mock(spec=User)
    user.is_active = True
    user.get_password_hash.return_value = "hash"
    mock_user_repo.get_by_email.return_value = user
    monkeypatch.setattr("core.services.auth_service.check_password_hash", lambda h, p: False)
    with pytest.raises(AuthError, match="Invalid credentials"):
        auth_service.login("t@e.com", "wrong")

def test_require_role_success(auth_service):
    """Line 65: Path where role is allowed"""
    user = Mock()
    user.role = "admin"
    auth_service.require_role(user, ["admin", "instructor"]) # Should not raise

def test_require_role_denied(auth_service):
    """Line 66: AuthError when role not in allowed list"""
    user = Mock()
    user.role = "student"
    with pytest.raises(AuthError, match="Permission denied"):
        auth_service.require_role(user, ["admin"])

def test_change_password_success(auth_service, mock_user_repo, monkeypatch):
    """Lines 70-84: Successful password change"""
    user = Mock(spec=User)
    user.get_password_hash.return_value = "old_hash"
    mock_user_repo.get_by_id.return_value = user
    mock_user_repo.update.return_value = True
    monkeypatch.setattr("core.services.auth_service.check_password_hash", lambda h, p: True)
    monkeypatch.setattr("core.services.auth_service.generate_password_hash", lambda p: "new_hash")
    
    result = auth_service.change_password(1, "old", "new")
    assert result is True
    assert user.password == "new_hash"
    mock_user_repo.update.assert_called_once()

def test_change_password_user_not_found(auth_service, mock_user_repo):
    """Line 72: AuthError when user not found during password change"""
    mock_user_repo.get_by_id.return_value = None
    with pytest.raises(AuthError, match="User not found"):
        auth_service.change_password(1, "o", "n")

def test_change_password_incorrect_current(auth_service, mock_user_repo, monkeypatch):
    """Line 77: AuthError when current password verification fails"""
    user = Mock(spec=User)
    user.get_password_hash.return_value = "hash"
    mock_user_repo.get_by_id.return_value = user
    monkeypatch.setattr("core.services.auth_service.check_password_hash", lambda h, p: False)
    with pytest.raises(AuthError, match="Current password is incorrect"):
        auth_service.change_password(1, "wrong", "new")
