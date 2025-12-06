import pytest
from Backend.Model.Student_model import Student, User


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
        saved_user = user_repo.save_user(user)
        
        # Then create student
        student = Student(
            id=saved_user.get_id(),
            name=saved_user.name,
            email=saved_user.email,
            password=saved_user.get_password_hash(),
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at,
            student_number="S67890",
            Program="Data Science",
            year_Level=3
        )
        
        saved_student = student_repo.save_student(student)
        
        assert saved_student is not None
        assert saved_student.student_number == "S67890"
        assert saved_student.program == "Data Science"
        assert saved_student.year_Level == 3
    
    def test_get_by_id_returns_student(self, sample_student, student_repo):
        """Test retrieving student by ID"""
        retrieved = student_repo.get_by_id(sample_student.get_id())
        
        assert retrieved is not None
        assert retrieved.get_id() == sample_student.get_id()
        assert retrieved.student_number == sample_student.student_number
    
    def test_find_by_number(self, sample_student, student_repo):
        """Test finding student by student number"""
        retrieved = student_repo.find_by_number(sample_student)
        
        assert retrieved is not None
        assert retrieved.student_number == sample_student.student_number
    
    def test_update_student_data(self, sample_student, student_repo):
        """Test updating student data"""
        sample_student.program = "Software Engineering"
        sample_student.year_Level = 4
        
        updated = student_repo.save_student(sample_student)
        
        assert updated.program == "Software Engineering"
        assert updated.year_Level == 4
    
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
            Program="CS",
            year_Level=1
        )
        
        with pytest.raises(Exception):
            student_repo.save_student(student)
