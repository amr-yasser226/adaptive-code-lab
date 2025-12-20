import pytest
import sqlite3
from unittest.mock import Mock
from core.entities.result import Result
from core.entities.test_case import Testcase


@pytest.mark.repo
@pytest.mark.unit
class TestResultRepo:
    """Test suite for ResultRepository"""
    
    def test_save_result(self, sample_submission, sample_assignment, testcase_repo, result_repo):
        """Test saving a new result"""
        # Create test case first
        testcase = Testcase(
            id=None,
            assignment_id=sample_assignment.get_id(),
            name="Test",
            stdin="input",
            descripion="Description",
            expected_out="output",
            timeout_ms=5000,
            memory_limit_mb=256,
            points=10,
            is_visible=True,
            sort_order=1,
            created_at=None
        )
        saved_testcase = testcase_repo.create(testcase)
        
        result = Result(
            id=None,
            submission_id=sample_submission.get_id(),
            test_case_id=saved_testcase.get_id(),
            passed=True,
            stdout="output",
            stderr="",
            runtime_ms=100,
            memory_kb=1024,
            exit_code=0,
            error_message=None,
            created_at=None
        )
        
        saved = result_repo.save_result(result)
        
        assert saved is not None
        assert saved.get_id() is not None
        assert saved.passed is True
    
    def test_get_by_id_returns_result(self, sample_submission, sample_assignment, testcase_repo, result_repo):
        """Test retrieving result by ID"""
        testcase = Testcase(
            id=None,
            assignment_id=sample_assignment.get_id(),
            name="Test",
            stdin="input",
            descripion="Description",
            expected_out="output",
            timeout_ms=5000,
            memory_limit_mb=256,
            points=10,
            is_visible=True,
            sort_order=1,
            created_at=None
        )
        saved_testcase = testcase_repo.create(testcase)
        
        result = Result(
            id=None,
            submission_id=sample_submission.get_id(),
            test_case_id=saved_testcase.get_id(),
            passed=False,
            stdout="",
            stderr="Error occurred",
            runtime_ms=50,
            memory_kb=512,
            exit_code=1,
            error_message="Runtime error",
            created_at=None
        )
        saved = result_repo.save_result(result)
        
        retrieved = result_repo.get_by_id(saved.get_id())
        
        assert retrieved is not None
        assert retrieved.passed is False
        assert retrieved.error_message == "Runtime error"

    def test_get_by_id_not_found(self, result_repo):
        """Line 21: get_by_id returns None for non-existent ID"""
        assert result_repo.get_by_id(9999) is None
    
    def test_find_by_submission(self, sample_submission, sample_assignment, testcase_repo, result_repo):
        """Test finding results by submission"""
        # Create test cases and results
        for i in range(3):
            testcase = Testcase(
                id=None,
                assignment_id=sample_assignment.get_id(),
                name=f"Test {i}",
                stdin="input",
                descripion="Description",
                expected_out="output",
                timeout_ms=5000,
                memory_limit_mb=256,
                points=10,
                is_visible=True,
                sort_order=i,
                created_at=None
            )
            saved_testcase = testcase_repo.create(testcase)
            
            result = Result(
                id=None,
                submission_id=sample_submission.get_id(),
                test_case_id=saved_testcase.get_id(),
                passed=True,
                stdout="output",
                stderr="",
                runtime_ms=100,
                memory_kb=1024,
                exit_code=0,
                error_message=None,
                created_at=None
            )
            result_repo.save_result(result)
        
        results = result_repo.find_by_submission(sample_submission.get_id())
        assert len(results) >= 3

    def test_save_result_error(self, result_repo, sample_submission):
        """Line 64-66: save_result handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        result_repo.db = mock_db
        result = Result(None, sample_submission.get_id(), 1, True, "o", "e", 1, 1, 0, None, None)
        assert result_repo.save_result(result) is None
        mock_db.rollback.assert_called_once()