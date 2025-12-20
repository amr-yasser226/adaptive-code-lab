import pytest
from core.entities.instructor import Instructor, User


@pytest.mark.repo
@pytest.mark.unit
class TestInstructorRepo:
    """Test suite for Instructor_repo"""
    
    def test_save_instructor_creates_record(self, user_repo, instructor_repo):
        """Test creating a new instructor"""
        
        user = User(
            id=None,
            name="Prof. Johnson",
            email="prof.johnson@university.com",
            password="hash",
            role="instructor",
            is_active=True
        )
        saved_user = user_repo.create(user)
        
        instructor = Instructor(
            id=saved_user.get_id(),
            name=saved_user.name,
            email=saved_user.email,
            password=saved_user.get_password_hash(),
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at,
            instructor_code="INST002",
            bio="Expert in algorithms",
            office_hours="Tue/Thu 3-5pm"
        )
        
        saved_instructor = instructor_repo.save(instructor)
        
        assert saved_instructor is not None
        assert saved_instructor.instructor_code == "INST002"
        assert saved_instructor.bio == "Expert in algorithms"
    
    def test_get_by_id_returns_instructor(self, sample_instructor, instructor_repo):
        """Test retrieving instructor by ID"""
        retrieved = instructor_repo.get_by_id(sample_instructor.get_id())
        
        assert retrieved is not None
        assert retrieved.instructor_code == sample_instructor.instructor_code

    def test_get_by_id_not_found(self, instructor_repo):
        """Line 21: get_by_id returns None for non-existent ID"""
        assert instructor_repo.get_by_id(9999) is None
    
    def test_get_by_code_returns_instructor(self, sample_instructor, instructor_repo):
        """Test retrieving instructor by code"""
        retrieved = instructor_repo.get_by_code(sample_instructor.instructor_code)
        
        assert retrieved is not None
        assert retrieved.get_id() == sample_instructor.get_id()
    
    def test_update_instructor_data(self, sample_instructor, instructor_repo):
        """Test updating instructor data"""
        sample_instructor.bio = "Updated bio"
        sample_instructor.office_hours = "Mon/Wed/Fri 1-3pm"
        
        updated = instructor_repo.save(sample_instructor)
        
        assert updated.bio == "Updated bio"
        assert updated.office_hours == "Mon/Wed/Fri 1-3pm"

    def test_get_by_code_not_found(self, instructor_repo):
        """Line 48: get_by_code returns None for non-existent code"""
        assert instructor_repo.get_by_code("NONEXISTENT") is None

    def test_save_user_not_found(self, instructor_repo):
        """Line 68: save raises Exception if user doesn't exist"""
        instructor = Instructor(999, "N", "E", "P", None, None, "C", "B", "H")
        with pytest.raises(Exception, match="User does not exist"):
            instructor_repo.save(instructor)

    def test_save_wrong_role(self, user_repo, instructor_repo):
        """Line 70: save raises Exception if user is not an instructor"""
        user = User(None, "S", "student@test.com", "P", "student")
        saved_user = user_repo.create(user)
        instructor = Instructor(saved_user.get_id(), "S", "student@test.com", "P", saved_user.created_at, saved_user.updated_at, "C", "B", "H")
        with pytest.raises(Exception, match="User role must be 'instructor'"):
            instructor_repo.save(instructor)

    def test_save_error(self, instructor_repo, sample_instructor):
        """Line 119-122: save handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        instructor_repo.db = mock_db
        assert instructor_repo.save(sample_instructor) is None
        mock_db.rollback.assert_called_once()
