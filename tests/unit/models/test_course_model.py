import pytest
from datetime import datetime
from core.entities.course import Course


class TestCourse:
    """Test suite for Course entity"""

    def test_init(self):
        """Test Course initialization"""
        now = datetime.now()
        course = Course(
            id=1,
            instructor_id=10,
            code="CS101",
            title="Intro to CS",
            description="Basic programming",
            year=2024,
            semester="Fall",
            max_students=30,
            created_at=now,
            status="active",
            updated_at=now,
            credits=3
        )

        assert course.get_id() == 1
        assert course.get_instructor_id() == 10
        assert course.code == "CS101"
        assert course.title == "Intro to CS"
        assert course.max_students == 30
        assert course.credits == 3

    def test_get_id(self):
        """Test get_id getter"""
        course = Course(
            id=42, instructor_id=1, code="CS", title="Test",
            description="", year=2024, semester="Fall",
            max_students=10, created_at=datetime.now(),
            status="active", updated_at=datetime.now(), credits=3
        )
        assert course.get_id() == 42

    def test_get_instructor_id(self):
        """Test get_instructor_id getter"""
        course = Course(
            id=1, instructor_id=99, code="CS", title="Test",
            description="", year=2024, semester="Fall",
            max_students=10, created_at=datetime.now(),
            status="active", updated_at=datetime.now(), credits=3
        )
        assert course.get_instructor_id() == 99

    def test_is_active_true(self):
        """Test is_active returns True for active course"""
        course = Course(
            id=1, instructor_id=1, code="CS", title="Test",
            description="", year=2024, semester="Fall",
            max_students=10, created_at=datetime.now(),
            status="active", updated_at=datetime.now(), credits=3
        )
        assert course.is_active() is True

    def test_is_active_false(self):
        """Test is_active returns False for inactive course"""
        course = Course(
            id=1, instructor_id=1, code="CS", title="Test",
            description="", year=2024, semester="Fall",
            max_students=10, created_at=datetime.now(),
            status="archived", updated_at=datetime.now(), credits=3
        )
        assert course.is_active() is False

    def test_has_capacity_true(self):
        """Test has_capacity returns True when under limit"""
        course = Course(
            id=1, instructor_id=1, code="CS", title="Test",
            description="", year=2024, semester="Fall",
            max_students=30, created_at=datetime.now(),
            status="active", updated_at=datetime.now(), credits=3
        )
        assert course.has_capacity(25) is True

    def test_has_capacity_false(self):
        """Test has_capacity returns False when at/over limit"""
        course = Course(
            id=1, instructor_id=1, code="CS", title="Test",
            description="", year=2024, semester="Fall",
            max_students=30, created_at=datetime.now(),
            status="active", updated_at=datetime.now(), credits=3
        )
        assert course.has_capacity(30) is False
        assert course.has_capacity(35) is False
