import pytest
from datetime import datetime
from core.entities.admin import Admin

def test_admin_initialization():
    admin = Admin(1, "Admin User", "admin@example.com", "hash", datetime.now(), datetime.now())
    assert admin.name == "Admin User"
    assert admin.role == "admin"
    assert admin.email == "admin@example.com"
    assert admin.is_active is True

def test_admin_inheritance():
    admin = Admin(1, "Name", "email", "pwd", datetime.now(), datetime.now())
    assert hasattr(admin, 'activate_account') # Inherited from User
    assert hasattr(admin, 'deactivate_account')
