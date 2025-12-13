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
    mock_user_repo.save_user.return_value = True
    
    result = auth_service.register("Test User", "test@example.com", "password")
    
    assert result is True
    mock_user_repo.save_user.assert_called_once()
    args, _ = mock_user_repo.save_user.call_args
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
        
    mock_user_repo.save_user.assert_not_called()

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
    user = Mock(spec=User)
    user.is_active = False
    mock_user_repo.get_by_email.return_value = user
    
    with pytest.raises(AuthError, match="Account is deactivated"):
        auth_service.login("test@example.com", "password")
