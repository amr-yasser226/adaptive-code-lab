import pytest
from datetime import datetime
from core.entities.user import User


class TestUser:
    """Test suite for User entity"""

    def test_init(self):
        """Test User initialization"""
        now = datetime.now()
        user = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            password="hashed_pwd",
            role="student",
            created_at=now,
            updated_at=now,
            is_active=True
        )

        assert user.get_id() == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.role == "student"
        assert user.is_active is True

    def test_get_id(self):
        """Test get_id getter"""
        user = User(
            id=42, name="Test", email="test@test.com",
            password="pwd", role="student"
        )
        assert user.get_id() == 42

    def test_is_active_default(self):
        """Test is_active defaults to True"""
        user = User(
            id=1, name="Test", email="test@test.com",
            password="pwd", role="student"
        )
        assert user.is_active is True

    def test_is_active_converted_to_bool(self):
        """Test is_active is converted to boolean"""
        user = User(
            id=1, name="Test", email="test@test.com",
            password="pwd", role="student", is_active=0
        )
        assert user.is_active is False

    def test_hash_password(self):
        """Test hash_password static method"""
        hashed = User.hash_password("secret123")
        assert hashed != "secret123"
        assert hashed.startswith("pbkdf2:sha256") or hashed.startswith("scrypt")

    def test_set_password(self):
        """Test set_password method"""
        user = User(
            id=1, name="Test", email="test@test.com",
            password="old_hash", role="student"
        )
        old_hash = user.get_password_hash()
        
        user.set_password("new_password")
        
        assert user.get_password_hash() != old_hash

    def test_get_password_hash(self):
        """Test get_password_hash returns the hash"""
        user = User(
            id=1, name="Test", email="test@test.com",
            password="stored_hash", role="student"
        )
        assert user.get_password_hash() == "stored_hash"

    def test_authenticate_password_correct(self):
        """Test authenticate_password with correct password"""
        hashed = User.hash_password("correct_pwd")
        user = User(
            id=1, name="Test", email="test@test.com",
            password=hashed, role="student"
        )
        
        assert user.authenticate_password("correct_pwd") is True

    def test_authenticate_password_wrong(self):
        """Test authenticate_password with wrong password"""
        hashed = User.hash_password("correct_pwd")
        user = User(
            id=1, name="Test", email="test@test.com",
            password=hashed, role="student"
        )
        
        assert user.authenticate_password("wrong_pwd") is False

    def test_update_profile_name(self):
        """Test update_profile updates name"""
        user = User(
            id=1, name="Old Name", email="test@test.com",
            password="pwd", role="student"
        )
        
        user.update_profile(name="New Name")
        
        assert user.name == "New Name"

    def test_update_profile_email(self):
        """Test update_profile updates email"""
        user = User(
            id=1, name="Test", email="old@test.com",
            password="pwd", role="student"
        )
        
        user.update_profile(email="new@test.com")
        
        assert user.email == "new@test.com"

    def test_deactivate_account(self):
        """Test deactivate_account method"""
        user = User(
            id=1, name="Test", email="test@test.com",
            password="pwd", role="student", is_active=True
        )
        
        user.deactivate_account()
        
        assert user.is_active is False

    def test_activate_account(self):
        """Test activate_account method"""
        user = User(
            id=1, name="Test", email="test@test.com",
            password="pwd", role="student", is_active=False
        )
        
        user.activate_account()
        
        assert user.is_active is True
