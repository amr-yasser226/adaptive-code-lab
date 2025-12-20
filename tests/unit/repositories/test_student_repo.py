import pytest
from core.entities.student import Student, User


@pytest.mark.repo
@pytest.mark.unit
class TestStudentRepo:
    """Test suite for Student_repo"""
    
    def test_save_student_creates_record(self, user_repo, student_repo):
        """Test creating a new student"""
        
        # First create user
        user = User(
            id=None,
            name="Jane Doe",
            email="jane@student.com",
            password="hash",
            role="student",
            is_active=True
        )
        saved_user = user_repo.create(user)
        
        # Then create student
        student = Student(
            id=saved_user.get_id(),
            name=saved_user.name,
            email=saved_user.email,
            password=saved_user.get_password_hash(),
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at,
            student_number="S67890",
            program="Data Science",
            year_level=3
        )
        
        saved_student = student_repo.save_student(student)
        
        assert saved_student is not None
        assert saved_student.student_number == "S67890"
        assert saved_student.program == "Data Science"
        assert saved_student.year_level == 3
    
    def test_get_by_id_returns_student(self, sample_student, student_repo):
        """Test retrieving student by ID"""
        retrieved = student_repo.get_by_id(sample_student.get_id())
        
        assert retrieved is not None
        assert retrieved.get_id() == sample_student.get_id()
        assert retrieved.student_number == sample_student.student_number

    def test_get_by_id_not_found(self, student_repo):
        """Line 21: get_by_id returns None for non-existent ID"""
        assert student_repo.get_by_id(9999) is None
    
    def test_find_by_number(self, sample_student, student_repo):
        """Test finding student by student number"""
        retrieved = student_repo.find_by_number(sample_student)
        
        assert retrieved is not None
        assert retrieved.student_number == sample_student.student_number
    
    def test_update_student_data(self, sample_student, student_repo):
        """Test updating student data"""
        sample_student.program = "Software Engineering"
        sample_student.year_level = 4
        
        updated = student_repo.save_student(sample_student)
        
        assert updated.program == "Software Engineering"
        assert updated.year_level == 4

    def test_find_by_number_not_found(self, student_repo):
        """Line 113: find_by_number returns None for non-existent number"""
        student = Student(None, "N", "E", "P", None, None, "S99", "Pr", 1)
        assert student_repo.find_by_number(student) is None
    
    def test_save_student_without_user_fails(self, student_repo):
        """Test that saving student without user record fails"""
        student = Student(
            id=99999,  # Non-existent user ID
            name="No User",
            email="nouser@test.com",
            password="hash",
            created_at=None,
            updated_at=None,
            student_number="S99999",
            program="CS",
            year_level=1
        )
        
        with pytest.raises(Exception):
            student_repo.save_student(student)

    def test_save_student_no_id(self, student_repo):
        """Line 39: save_student raises Exception if ID is None"""
        student = Student(None, "N", "E", "P", None, None, "S1", "P", 1)
        with pytest.raises(Exception, match="Student must have a user ID"):
            student_repo.save_student(student)

    def test_save_student_wrong_role(self, user_repo, student_repo):
        """Line 46: save_student raises Exception if user is not a student"""
        user = User(None, "I", "inst@test.com", "P", "instructor")
        saved_user = user_repo.create(user)
        student = Student(saved_user.get_id(), "I", "inst@test.com", "P", saved_user.created_at, saved_user.updated_at, "S1", "P", 1)
        with pytest.raises(Exception, match="User role must be 'student'"):
            student_repo.save_student(student)

    def test_save_student_error(self, student_repo, sample_student):
        """Line 95-98: save_student handles sqlite3.Error"""
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        student_repo.db = mock_db
        with pytest.raises(sqlite3.Error):
            student_repo.save_student(sample_student)
        mock_db.rollback.assert_called_once()
