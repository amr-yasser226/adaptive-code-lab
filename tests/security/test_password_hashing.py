import pytest
from datetime import datetime


class TestPasswordHashing:
    """Test suite for password security"""

    def test_password_is_hashed(self, clean_db, user_repo):
        """Test passwords are stored as hashes, not plaintext"""
        from core.entities.student import Student
        from core.entities.user import User

        # Hash a password
        plain_password = "my_secret_password_123"
        hashed = User.hash_password(plain_password)

        # Verify it's hashed (not plaintext)
        assert hashed != plain_password
        assert len(hashed) > len(plain_password)
        assert hashed.startswith("pbkdf2:sha256") or hashed.startswith("scrypt")

    def test_password_verification(self):
        """Test password verification works correctly"""
        from core.entities.user import User

        # Create user with hashed password
        plain_password = "correct_password"
        hashed = User.hash_password(plain_password)
        
        user = User(
            id=1, name="Test", email="test@test.com",
            password=hashed, role="student",
            created_at=datetime.now(), updated_at=datetime.now()
        )

        # Correct password should verify
        assert user.authenticate_password(plain_password) is True

        # Wrong password should not verify
        assert user.authenticate_password("wrong_password") is False

    def test_same_password_different_hashes(self):
        """Test same password produces different hashes (salt)"""
        from core.entities.user import User

        password = "same_password"
        hash1 = User.hash_password(password)
        hash2 = User.hash_password(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # But both should verify the same password
        user1 = User(1, "U1", "u1@test.com", hash1, "student")
        user2 = User(2, "U2", "u2@test.com", hash2, "student")
        assert user1.authenticate_password(password) is True
        assert user2.authenticate_password(password) is True

    def test_password_change_updates_hash(self):
        """Test changing password updates the hash"""
        from core.entities.user import User

        user = User(
            id=1, name="Test", email="test@test.com",
            password=User.hash_password("old_password"),
            role="student"
        )

        old_hash = user.get_password_hash()

        # Change password
        user.set_password("new_password")
        new_hash = user.get_password_hash()

        # Hash should have changed
        assert new_hash != old_hash

        # Old password should not work
        assert user.authenticate_password("old_password") is False

        # New password should work
        assert user.authenticate_password("new_password") is True

    def test_empty_password_handling(self):
        """Test empty/weak passwords are handled"""
        from core.entities.user import User

        # Empty password can be hashed (validation should be in service layer)
        empty_hash = User.hash_password("")
        assert len(empty_hash) > 0

        # Very short password
        short_hash = User.hash_password("123")
        assert len(short_hash) > 3

    def test_special_characters_in_password(self):
        """Test passwords with special characters are handled"""
        from core.entities.user import User

        # Password with special characters
        special_password = "P@ssw0rd!#$%^&*()"
        hashed = User.hash_password(special_password)

        user = User(
            id=1, name="Test", email="test@test.com",
            password=hashed, role="student"
        )

        assert user.authenticate_password(special_password) is True
        assert user.authenticate_password("P@ssw0rd") is False

    def test_unicode_password(self):
        """Test unicode characters in passwords"""
        from core.entities.user import User

        # Unicode password
        unicode_password = "密码test🔒"
        hashed = User.hash_password(unicode_password)

        user = User(
            id=1, name="Test", email="test@test.com",
            password=hashed, role="student"
        )

        assert user.authenticate_password(unicode_password) is True
