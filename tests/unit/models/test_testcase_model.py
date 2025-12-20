import pytest
from datetime import datetime
from core.entities.test_case import Testcase


class TestTestcase:
    """Test suite for Testcase entity"""

    def test_init(self):
        """Test Testcase initialization"""
        now = datetime.now()
        testcase = Testcase(
            id=1,
            assignment_id=10,
            name="Basic Test",
            stdin="input",
            descripion="Test basic functionality",
            expected_out="output",
            timeout_ms=1000,
            memory_limit_mb=256,
            points=10,
            is_visible=True,
            sort_order=1,
            created_at=now
        )

        assert testcase.get_id() == 1
        assert testcase.get_assignment_id() == 10
        assert testcase.name == "Basic Test"
        assert testcase.points == 10
        assert testcase.is_visible is True

    def test_get_id(self):
        """Test get_id getter"""
        testcase = Testcase(
            id=42, assignment_id=1, name="Test",
            stdin="", descripion="", expected_out="",
            timeout_ms=1000, memory_limit_mb=256,
            points=1, is_visible=True, sort_order=0,
            created_at=datetime.now()
        )
        assert testcase.get_id() == 42

    def test_get_assignment_id(self):
        """Test get_assignment_id getter"""
        testcase = Testcase(
            id=1, assignment_id=99, name="Test",
            stdin="", descripion="", expected_out="",
            timeout_ms=1000, memory_limit_mb=256,
            points=1, is_visible=True, sort_order=0,
            created_at=datetime.now()
        )
        assert testcase.get_assignment_id() == 99

    def test_timeout_converted_to_int(self):
        """Test timeout_ms is converted to integer"""
        testcase = Testcase(
            id=1, assignment_id=1, name="Test",
            stdin="", descripion="", expected_out="",
            timeout_ms="1000", memory_limit_mb=256,
            points=1, is_visible=True, sort_order=0,
            created_at=datetime.now()
        )
        assert testcase.timeout_ms == 1000
        assert isinstance(testcase.timeout_ms, int)

    def test_memory_limit_converted_to_int(self):
        """Test memory_limit_mb is converted to integer"""
        testcase = Testcase(
            id=1, assignment_id=1, name="Test",
            stdin="", descripion="", expected_out="",
            timeout_ms=1000, memory_limit_mb="512",
            points=1, is_visible=True, sort_order=0,
            created_at=datetime.now()
        )
        assert testcase.memory_limit_mb == 512
        assert isinstance(testcase.memory_limit_mb, int)

    def test_is_visible_converted_to_bool(self):
        """Test is_visible is converted to boolean"""
        testcase = Testcase(
            id=1, assignment_id=1, name="Test",
            stdin="", descripion="", expected_out="",
            timeout_ms=1000, memory_limit_mb=256,
            points=1, is_visible=1, sort_order=0,
            created_at=datetime.now()
        )
        assert testcase.is_visible is True

    def test_nullable_timeout(self):
        """Test timeout_ms can be None"""
        testcase = Testcase(
            id=1, assignment_id=1, name="Test",
            stdin="", descripion="", expected_out="",
            timeout_ms=None, memory_limit_mb=None,
            points=1, is_visible=True, sort_order=0,
            created_at=datetime.now()
        )
        assert testcase.timeout_ms is None
        assert testcase.memory_limit_mb is None

    def test_validate_success(self):
        """Test validate returns True for valid test case"""
        testcase = Testcase(
            id=1, assignment_id=1, name="Test", stdin="", descripion="", 
            expected_out="out", timeout_ms=1000, memory_limit_mb=256,
            points=10, is_visible=True, sort_order=0, created_at=datetime.now()
        )
        assert testcase.validate() is True

    def test_validate_empty_name(self):
        """Test validate raises error for empty name"""
        testcase = Testcase(
            id=1, assignment_id=1, name="", stdin="", descripion="", 
            expected_out="out", timeout_ms=1000, memory_limit_mb=256,
            points=10, is_visible=True, sort_order=0, created_at=datetime.now()
        )
        with pytest.raises(ValueError, match="Test case name cannot be empty"):
            testcase.validate()

    def test_clone(self):
        """Test clone creates a copy with new ID"""
        original = Testcase(
            id=1, assignment_id=5, name="Original", stdin="in", descripion="desc", 
            expected_out="out", timeout_ms=1000, memory_limit_mb=256,
            points=10, is_visible=True, sort_order=1, created_at=datetime.now()
        )
        
        clone = original.clone()
        
        assert clone.get_id() is None
        assert clone.get_assignment_id() == 5
        assert clone.name == "Original (Copy)"
        assert clone.stdin == "in"
        assert clone.points == 10

    def test_run_on_raises_error(self):
        """Test run_on raises NotImplementedError"""
        testcase = Testcase(
            id=1, assignment_id=1, name="Test", stdin="", descripion="", 
            expected_out="", timeout_ms=1000, memory_limit_mb=256,
            points=10, is_visible=True, sort_order=0, created_at=datetime.now()
        )
        with pytest.raises(NotImplementedError):
            testcase.run_on(123)
