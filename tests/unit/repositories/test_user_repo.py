import pytest
from core.entities.user import User


@pytest.mark.repo
@pytest.mark.unit
class TestUserRepo:
    """Test suite for User_repo"""
    
    def test_create_creates_new_user(self, user_repo):
        """Test creating a new user"""
        user = User(
            id=None,
            name="Alice Smith",
            email="alice@example.com",
            password="secure_hash_123",
            role="student",
            is_active=True
        )
        
        saved_user = user_repo.create(user)
        
        assert saved_user is not None
        assert saved_user.get_id() is not None
        assert saved_user.name == "Alice Smith"
        assert saved_user.email == "alice@example.com"
        assert saved_user.role == "student"
        assert saved_user.is_active is True
    
    def test_get_by_id_returns_user(self, user_repo, sample_user):
        """Test retrieving user by ID"""
        retrieved = user_repo.get_by_id(sample_user.get_id())
        
        assert retrieved is not None
        assert retrieved.get_id() == sample_user.get_id()
        assert retrieved.email == sample_user.email
    
    def test_get_by_id_returns_none_for_nonexistent(self, user_repo):
        """Test retrieving non-existent user returns None"""
        retrieved = user_repo.get_by_id(99999)
        assert retrieved is None
    
    def test_get_by_email_returns_user(self, user_repo, sample_user):
        """Test retrieving user by email"""
        retrieved = user_repo.get_by_email(sample_user.email)
        
        assert retrieved is not None
        assert retrieved.email == sample_user.email
    
    def test_get_by_email_returns_none_for_nonexistent(self, user_repo):
        """Test retrieving non-existent email returns None"""
        retrieved = user_repo.get_by_email("nonexistent@example.com")
        assert retrieved is None
    
    def test_update_user_data(self, user_repo, sample_user):
        """Test updating user data"""
        sample_user.name = "Updated Name"
        sample_user.email = "updated@example.com"
        
        updated = user_repo.update(sample_user)
        
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.email == "updated@example.com"
    
    def test_delete_user(self, user_repo, sample_user):
        """Test deleting a user"""
        user_id = sample_user.get_id()
        user_repo.delete(user_id)
        
        retrieved = user_repo.get_by_id(user_id)
        assert retrieved is None
    
    def test_find_all_users(self, user_repo):
        """Test finding all users"""
        # Create multiple users
        for i in range(3):
            user = User(
                id=None,
                name=f"User {i}",
                email=f"user{i}@example.com",
                password="hash",
                role="student",
                is_active=True
            )
            user_repo.create(user)
        
        all_users = user_repo.list_all()
        assert len(all_users) >= 3
    
    def test_find_all_with_filters(self, user_repo):
        """Test finding users with filters"""
        # Create users with different roles
        for role in ["student", "instructor"]:
            user = User(
                id=None,
                name=f"{role} user",
                email=f"{role}@example.com",
                password="hash",
                role=role,
                is_active=True
            )
            user_repo.create(user)
        
        students = user_repo.list_all({"role": "student"})
        assert all(u.role == "student" for u in students)

    def test_get_user_with_missing_bio_col(self, user_repo, sample_user):
        """Line 24/49: Handle IndexError when bio column is missing (older schema)"""
        from unittest.mock import Mock
        mock_db = Mock()
        # Mocking row result with only 8 columns (0-7)
        row = (1, "N", "E", "H", "S", 1, "C", "U") 
        mock_db.execute.return_value.fetchone.return_value = row
        user_repo.db = mock_db
        
        user = user_repo.get_by_id(1)
        assert user.bio is None
        
        user2 = user_repo.get_by_email("E")
        assert user2.bio is None

    def test_create_user_error(self, user_repo):
        """Line 85-86: sqlite3.Error handling in create"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("DB Error")
        user_repo.db = mock_db
        
        user = User(None, "N", "E", "P", "student")
        with pytest.raises(sqlite3.Error):
            user_repo.create(user)
        mock_db.rollback.assert_called_once()

    def test_delete_user_error(self, user_repo):
        """Line 94-95: sqlite3.Error handling in delete"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("DB Error")
        user_repo.db = mock_db
        
        with pytest.raises(sqlite3.Error):
            user_repo.delete(1)
        mock_db.rollback.assert_called_once()

    def test_list_all_missing_bio_col(self, user_repo):
        """Line 113-114: Handle IndexError in list_all"""
        from unittest.mock import Mock
        mock_db = Mock()
        row = (1, "N", "E", "H", "S", 1, "C", "U")
        mock_db.execute.return_value.fetchall.return_value = [row]
        user_repo.db = mock_db
        
        users = user_repo.list_all()
        assert len(users) == 1
        assert users[0].bio is None

    def test_update_user_error(self, user_repo, sample_user):
        """Line 156-159: sqlite3.Error handling in update"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("DB Error")
        user_repo.db = mock_db
        
        result = user_repo.update(sample_user)
        assert result is None
        mock_db.rollback.assert_called_once()
