import pytest
import sqlite3
from unittest.mock import Mock
from core.entities.test_case import Testcase


@pytest.mark.repo
@pytest.mark.unit
class TestTestcaseRepo:
    """Test suite for Testcase_repo"""
    
    def test_create_testcase(self, sample_assignment, testcase_repo):
        """Test creating a new test case"""
        testcase = Testcase(
            id=None,
            assignment_id=sample_assignment.get_id(),
            name="Test Case 1",
            stdin="5\n10\n",
            descripion="Test addition",
            expected_out="15\n",
            timeout_ms=5000,
            memory_limit_mb=256,
            points=10,
            is_visible=True,
            sort_order=1,
            created_at=None
        )
        
        saved = testcase_repo.create(testcase)
        
        assert saved is not None
        assert saved.get_id() is not None
        assert saved.name == "Test Case 1"
    
    def test_get_by_id_returns_testcase(self, sample_assignment, testcase_repo):
        """Test retrieving test case by ID"""
        testcase = Testcase(
            id=None,
            assignment_id=sample_assignment.get_id(),
            name="Test Case 2",
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
        saved = testcase_repo.create(testcase)
        
        retrieved = testcase_repo.get_by_id(saved.get_id())
        
        assert retrieved is not None
        assert retrieved.name == "Test Case 2"

    def test_get_by_id_not_found(self, testcase_repo):
        """Line 20: get_by_id returns None for non-existent ID"""
        assert testcase_repo.get_by_id(9999) is None
    
    def test_update_testcase(self, sample_assignment, testcase_repo):
        """Test updating test case"""
        testcase = Testcase(
            id=None,
            assignment_id=sample_assignment.get_id(),
            name="Original",
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
        saved = testcase_repo.create(testcase)
        
        saved.name = "Updated Test Case"
        saved.points = 20
        updated = testcase_repo.update(saved)
        
        assert updated.name == "Updated Test Case"
        assert updated.points == 20
    
    def test_delete_testcase(self, sample_assignment, testcase_repo):
        """Test deleting test case"""
        testcase = Testcase(
            id=None,
            assignment_id=sample_assignment.get_id(),
            name="To Delete",
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
        saved = testcase_repo.create(testcase)
        
        result = testcase_repo.delete(saved.get_id())
        
        assert result is True
        retrieved = testcase_repo.get_by_id(saved.get_id())
        assert retrieved is None

    def test_create_error(self, testcase_repo, sample_assignment):
        """Line 66-68: create handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        testcase_repo.db = mock_db
        testcase = Testcase(None, sample_assignment.get_id(), "n", "i", "d", "e", 1, 1, 1, True, 1, None)
        assert testcase_repo.create(testcase) is None
        mock_db.rollback.assert_called_once()

    def test_update_error(self, testcase_repo, sample_assignment):
        """Line 100-102: update handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        testcase_repo.db = mock_db
        testcase = Testcase(1, sample_assignment.get_id(), "n", "i", "d", "e", 1, 1, 1, True, 1, None)
        assert testcase_repo.update(testcase) is None
        mock_db.rollback.assert_called_once()

    def test_delete_error(self, testcase_repo):
        """Line 109-111: delete handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        testcase_repo.db = mock_db
        assert testcase_repo.delete(1) is False
        mock_db.rollback.assert_called_once()
    
    def test_list_by_assignment(self, sample_assignment, testcase_repo):
        """Test listing test cases by assignment"""
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
            testcase_repo.create(testcase)
        
        testcases = testcase_repo.list_by_assignment(sample_assignment.get_id())
        assert len(testcases) >= 3
