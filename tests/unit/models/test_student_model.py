import pytest
from datetime import datetime
from core.entities.student import Student

@pytest.mark.model
@pytest.mark.unit
class TestStudentModel:
    """Test suite for Student entity"""

    def test_student_initialization(self):
        """Test student initialization and getters"""
        now = datetime.now()
        student = Student(
            id=1,
            name="John Doe",
            email="john@example.com",
            password="hashed_pw",
            created_at=now,
            updated_at=now,
            student_number="S12345",
            program="CS",
            year_level=2,
            is_active=True
        )

        assert student.get_id() == 1
        assert student.name == "John Doe"
        assert student.student_number == "S12345"
        assert student.role == "student"