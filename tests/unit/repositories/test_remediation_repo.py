import pytest
import sqlite3
from unittest.mock import Mock
from datetime import datetime
from core.entities.remediation import Remediation, StudentRemediation


@pytest.mark.repo
@pytest.mark.unit
class TestRemediationRepo:
    """Test suite for RemediationRepository"""
    
    def test_create_and_get_remediation(self, remediation_repo):
        """Test creating and retrieving remediation by ID"""
        rem = Remediation(
            id=None,
            failure_pattern="test_pattern",
            resource_title="Test Resource",
            resource_type="article",
            resource_url="http://example.com",
            resource_content="Some content",
            difficulty_level="beginner",
            language="python"
        )
        
        saved = remediation_repo.create(rem)
        assert saved.get_id() is not None
        assert saved.failure_pattern == "test_pattern"
        
        retrieved = remediation_repo.get_by_id(saved.get_id())
        assert retrieved is not None
        assert retrieved.resource_title == "Test Resource"

    def test_get_by_id_not_found(self, remediation_repo):
        """Line 12: _row_to_remediation returns None for empty row"""
        assert remediation_repo.get_by_id(9999) is None

    def test_find_by_pattern(self, remediation_repo):
        """Test finding remediations by failure pattern"""
        rem = Remediation(
            id=None,
            failure_pattern="unique_pattern",
            resource_title="Unique Resource",
            resource_type="article"
        )
        remediation_repo.create(rem)
        
        results = remediation_repo.find_by_pattern("unique_pattern")
        assert len(results) >= 1
        assert any(r.resource_title == "Unique Resource" for r in results)

    def test_get_all(self, remediation_repo):
        """Test retrieving all remediations"""
        initial_count = len(remediation_repo.get_all())
        
        rem = Remediation(
            id=None,
            failure_pattern="another_pattern",
            resource_title="Another Resource",
            resource_type="article"
        )
        remediation_repo.create(rem)
        
        all_rems = remediation_repo.get_all()
        assert len(all_rems) == initial_count + 1

    def test_create_error(self, remediation_repo):
        """Line 79-81: create handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        remediation_repo.db = mock_db
        rem = Remediation(None, "p", "t")
        with pytest.raises(sqlite3.Error):
            remediation_repo.create(rem)
        mock_db.rollback.assert_called_once()

    def test_student_remediation_ops(self, remediation_repo, sample_student, sample_submission):
        """Test complete student remediation lifecycle"""
        # Create a remediation first
        rem = Remediation(
            id=None,
            failure_pattern="logic_error",
            resource_title="Logic Help",
            resource_type="article"
        )
        saved_rem = remediation_repo.create(rem)
        
        # Create student remediation
        sr = StudentRemediation(
            id=None,
            student_id=sample_student.get_id(),
            remediation_id=saved_rem.get_id(),
            submission_id=sample_submission.get_id()
        )
        
        saved_sr = remediation_repo.create_student_remediation(sr)
        assert saved_sr.get_id() is not None
        assert saved_sr.is_viewed is False
        
        # Get by specific student/remediation
        retrieved_sr = remediation_repo.get_student_remediation(
            sample_student.get_id(), saved_rem.get_id()
        )
        assert retrieved_sr is not None
        assert retrieved_sr.get_id() == saved_sr.get_id()
        
        # Update
        saved_sr.mark_viewed()
        updated_sr = remediation_repo.update_student_remediation(saved_sr)
        assert updated_sr.is_viewed is True
        assert updated_sr.viewed_at is not None
        
        # List student remediations
        student_rems = remediation_repo.list_student_remediations(sample_student.get_id())
        assert len(student_rems) >= 1
        
        # List only pending
        pending = remediation_repo.list_student_remediations(sample_student.get_id(), only_pending=True)
        assert any(p.get_id() == updated_sr.get_id() for p in pending)
        
        updated_sr.mark_completed()
        remediation_repo.update_student_remediation(updated_sr)
        
        pending_after = remediation_repo.list_student_remediations(sample_student.get_id(), only_pending=True)
        assert not any(p.get_id() == updated_sr.get_id() for p in pending_after)

    def test_create_student_remediation_error(self, remediation_repo, sample_student):
        """Line 124-126: create_student_remediation handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        remediation_repo.db = mock_db
        sr = StudentRemediation(None, sample_student.get_id(), 1)
        with pytest.raises(sqlite3.Error):
            remediation_repo.create_student_remediation(sr)
        mock_db.rollback.assert_called_once()

    def test_update_student_remediation_error(self, remediation_repo, sample_student):
        """Line 143-145: update_student_remediation handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        remediation_repo.db = mock_db
        sr = StudentRemediation(1, sample_student.get_id(), 1)
        with pytest.raises(sqlite3.Error):
            remediation_repo.update_student_remediation(sr)
        mock_db.rollback.assert_called_once()

    def test_get_student_remediation_not_found(self, remediation_repo):
        """Line 27: _row_to_student_remediation returns None for empty row"""
        assert remediation_repo.get_student_remediation(999, 999) is None
