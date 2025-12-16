import pytest
from datetime import datetime
from core.entities.result import Result


class TestResult:
    """Test suite for Result entity"""

    def test_init(self):
        """Test Result initialization"""
        now = datetime.now()
        result = Result(
            id=1,
            submission_id=10,
            test_case_id=5,
            passed=True,
            stdout="output",
            stderr="",
            runtime_ms=100,
            memory_kb=1024,
            exit_code=0,
            error_message=None,
            created_at=now
        )

        assert result.get_id() == 1
        assert result.get_submission_id() == 10
        assert result.get_test_case_id() == 5
        assert result.passed is True
        assert result.stdout == "output"

    def test_get_id(self):
        """Test get_id getter"""
        result = Result(
            id=42, submission_id=1, test_case_id=1, passed=True,
            stdout="", stderr="", runtime_ms=0, memory_kb=0,
            exit_code=0, error_message=None, created_at=datetime.now()
        )
        assert result.get_id() == 42

    def test_get_submission_id(self):
        """Test get_submission_id getter"""
        result = Result(
            id=1, submission_id=99, test_case_id=1, passed=True,
            stdout="", stderr="", runtime_ms=0, memory_kb=0,
            exit_code=0, error_message=None, created_at=datetime.now()
        )
        assert result.get_submission_id() == 99

    def test_get_test_case_id(self):
        """Test get_test_case_id getter"""
        result = Result(
            id=1, submission_id=1, test_case_id=77, passed=True,
            stdout="", stderr="", runtime_ms=0, memory_kb=0,
            exit_code=0, error_message=None, created_at=datetime.now()
        )
        assert result.get_test_case_id() == 77

    def test_passed_converted_to_bool(self):
        """Test passed is converted to boolean"""
        result = Result(
            id=1, submission_id=1, test_case_id=1, passed=1,
            stdout="", stderr="", runtime_ms=0, memory_kb=0,
            exit_code=0, error_message=None, created_at=datetime.now()
        )
        assert result.passed is True

    def test_issuccessful_true(self):
        """Test issuccessful returns True when passed and no error"""
        result = Result(
            id=1, submission_id=1, test_case_id=1, passed=True,
            stdout="ok", stderr="", runtime_ms=50, memory_kb=512,
            exit_code=0, error_message=None, created_at=datetime.now()
        )
        assert result.issuccessful() is True

    def test_issuccessful_false_not_passed(self):
        """Test issuccessful returns False when not passed"""
        result = Result(
            id=1, submission_id=1, test_case_id=1, passed=False,
            stdout="", stderr="error", runtime_ms=50, memory_kb=512,
            exit_code=1, error_message=None, created_at=datetime.now()
        )
        assert result.issuccessful() is False

    def test_issuccessful_false_with_error(self):
        """Test issuccessful returns False when has error_message"""
        result = Result(
            id=1, submission_id=1, test_case_id=1, passed=True,
            stdout="", stderr="", runtime_ms=50, memory_kb=512,
            exit_code=0, error_message="Runtime error", created_at=datetime.now()
        )
        assert result.issuccessful() is False

    def test_get_detail(self):
        """Test get_detail returns complete result info"""
        now = datetime.now()
        result = Result(
            id=1, submission_id=2, test_case_id=3, passed=True,
            stdout="out", stderr="err", runtime_ms=100, memory_kb=1024,
            exit_code=0, error_message=None, created_at=now
        )

        detail = result.get_detail()

        assert detail["id"] == 1
        assert detail["submission_id"] == 2
        assert detail["test_case_id"] == 3
        assert detail["passed"] is True
        assert detail["stdout"] == "out"
        assert detail["runtime_ms"] == 100
