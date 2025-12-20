import pytest
from core.entities.admin import Admin, User


@pytest.mark.repo
@pytest.mark.unit
class TestAdminRepo:
    """Test suite for AdminRepository"""
    
    def test_save_admin_creates_record(self, user_repo, admin_repo):
        """Test creating a new admin"""
        
        user = User(
            id=None,
            name="Admin User",
            email="admin@system.com",
            password="hash",
            role="admin",
            is_active=True
        )
        saved_user = user_repo.create(user)
        
        admin = Admin(
            id=saved_user.get_id(),
            name=saved_user.name,
            email=saved_user.email,
            password=saved_user.get_password_hash(),
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at,
            privileges="all"
        )
        
        saved_admin = admin_repo.save_admin(admin)
        
        assert saved_admin is not None
        assert saved_admin.privileges == "all"
    
    def test_get_by_id_returns_admin(self, user_repo, admin_repo):
        """Test retrieving admin by ID"""
        
        user = User(
            id=None,
            name="Admin Two",
            email="admin2@system.com",
            password="hash",
            role="admin",
            is_active=True
        )
        saved_user = user_repo.create(user)
        
        admin = Admin(
            id=saved_user.get_id(),
            name=saved_user.name,
            email=saved_user.email,
            password=saved_user.get_password_hash(),
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at,
            privileges="limited"
        )
        saved_admin = admin_repo.save_admin(admin)
        
        retrieved = admin_repo.get_by_id(saved_admin.get_id())
        
        assert retrieved is not None
        assert retrieved.privileges == "limited"

    def test_get_by_id_not_found(self, admin_repo):
        """Line 21: get_by_id returns None for non-existent ID"""
        assert admin_repo.get_by_id(9999) is None
    
    def test_update_admin_privileges(self, user_repo, admin_repo):
        """Test updating admin privileges"""
        
        user = User(
            id=None,
            name="Admin Three",
            email="admin3@system.com",
            password="hash",
            role="admin",
            is_active=True
        )
        saved_user = user_repo.create(user)
        
        admin = Admin(
            id=saved_user.get_id(),
            name=saved_user.name,
            email=saved_user.email,
            password=saved_user.get_password_hash(),
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at,
            privileges="read_only"
        )
        saved_admin = admin_repo.save_admin(admin)
        
        saved_admin.privileges = "full_access"
        updated = admin_repo.save_admin(saved_admin)
        
        assert updated.privileges == "full_access"

    def test_save_admin_no_id(self, admin_repo):
        """Line 37: save_admin raises Exception if ID is None"""
        admin = Admin(None, "N", "E", "P", None, None, True, "all")
        with pytest.raises(Exception, match="Admin must have a user ID"):
            admin_repo.save_admin(admin)

    def test_save_admin_user_not_found(self, admin_repo):
        """Line 42: save_admin raises Exception if user doesn't exist"""
        admin = Admin(999, "N", "E", "P", None, None, True, "all")
        with pytest.raises(Exception, match="User does not exist"):
            admin_repo.save_admin(admin)

    def test_save_admin_wrong_role(self, user_repo, admin_repo):
        """Line 44: save_admin raises Exception if user is not an admin"""
        user = User(None, "S", "s@test.com", "P", "student")
        saved_user = user_repo.create(user)
        admin = Admin(saved_user.get_id(), "S", "s@test.com", "P", saved_user.created_at, saved_user.updated_at, True, "all")
        with pytest.raises(Exception, match="User role must be 'admin'"):
            admin_repo.save_admin(admin)

    def test_save_admin_error(self, admin_repo, user_repo):
        """Line 75-78: save_admin handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        
        # We need a real user first
        user = User(None, "A", "a@test.com", "P", "admin")
        saved_user = user_repo.create(user)
        admin = Admin(saved_user.get_id(), "A", "a@test.com", "P", saved_user.created_at, saved_user.updated_at, True, "all")

        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        admin_repo.db = mock_db
        
        assert admin_repo.save_admin(admin) is None
        mock_db.rollback.assert_called_once()
        
    def test_save_admin_user_exists_no_password_hash(self, user_repo, admin_repo):
        """Line 60: save_admin handles users without get_password_hash"""
        user = User(None, "A2", "a2@test.com", "P", "admin")
        saved_user = user_repo.create(user)
        
        class SimpleAdmin:
            def __init__(self, id, name, email, password, privileges):
                self.id = id
                self.name = name
                self.email = email
                self.password = password
                self.privileges = privileges
            def get_id(self): return self.id

        admin = SimpleAdmin(saved_user.get_id(), "A2", "a2@test.com", "P", "all")
        res = admin_repo.save_admin(admin)
        assert res is not None
        assert res.name == "A2"
