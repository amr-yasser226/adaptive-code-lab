import pytest
from Backend.Model.Admin_model import Admin, User


@pytest.mark.repo
@pytest.mark.unit
class TestAdminRepo:
    """Test suite for Admin_repo"""
    
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
        saved_user = user_repo.save_user(user)
        
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
        saved_user = user_repo.save_user(user)
        
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
        saved_user = user_repo.save_user(user)
        
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
