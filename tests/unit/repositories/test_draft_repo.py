import pytest
from core.entities.draft import Draft
from infrastructure.repositories.draft_repository import DraftRepository

@pytest.mark.repo
@pytest.mark.unit
class TestDraftRepo:
    """Test suite for DraftRepository"""

    def test_create_draft_success(self, draft_repo, sample_user, sample_assignment):
        """Test creating a new draft successfully"""
        draft = Draft(
            id=None,
            user_id=sample_user.get_id(),
            assignment_id=sample_assignment.get_id(),
            content="print('hello')",
            language="python"
        )
        
        saved_draft = draft_repo.create(draft)
        
        assert saved_draft is not None
        assert saved_draft.get_id() is not None
        assert saved_draft.get_user_id() == sample_user.get_id()
        assert saved_draft.get_assignment_id() == sample_assignment.get_id()
        assert saved_draft.content == "print('hello')"
        assert saved_draft.language == "python"

    def test_create_draft_failure(self, draft_repo):
        """Test create fails with invalid data (sqlite3.Error)"""
        # passing something that will cause sqlite3 error (e.g. wrong type or missing required)
        draft = Draft(None, -1, -1, None) # Likely to fail if there are FKs or NOT NULL
        # But wait, local sqlite might not have FKs enabled by default in the setup.
        # However, we can mock the db to raise an error if needed, but let's try to trigger a real one.
        # Draft table has user_id and assignment_id.
        result = draft_repo.create(draft)
        # If the migration has NOT NULL constraints, it should return None on failure.
        assert result is None

    def test_get_by_id_returns_draft(self, draft_repo, sample_user, sample_assignment):
        """Test retrieving draft by ID"""
        draft = Draft(
            id=None,
            user_id=sample_user.get_id(),
            assignment_id=sample_assignment.get_id(),
            content="print('test')",
            language="python"
        )
        saved = draft_repo.create(draft)
        
        retrieved = draft_repo.get_by_id(saved.get_id())
        
        assert retrieved is not None
        assert retrieved.get_id() == saved.get_id()
        assert retrieved.content == "print('test')"

    def test_get_by_id_returns_none(self, draft_repo):
        """Test get_by_id returns None for non-existent ID"""
        assert draft_repo.get_by_id(9999) is None

    def test_get_latest_for_user_assignment(self, draft_repo, sample_user, sample_assignment):
        """Test retrieving the latest draft"""
        uid = sample_user.get_id()
        aid = sample_assignment.get_id()
        
        # Create two drafts
        draft1 = Draft(None, uid, aid, "content 1")
        draft2 = Draft(None, uid, aid, "content 2")
        
        draft_repo.create(draft1)
        import time
        time.sleep(1.1) # Ensure timestamp is different if precision is low
        draft_repo.create(draft2)
        
        latest = draft_repo.get_latest(uid, aid)
        
        assert latest is not None
        assert latest.content == "content 2"

    def test_get_latest_returns_none(self, draft_repo):
        """Test get_latest returns None when no drafts exist"""
        assert draft_repo.get_latest(999, 999) is None

    def test_delete_draft_success(self, draft_repo, sample_user, sample_assignment):
        """Test deleting a draft"""
        draft = Draft(None, sample_user.get_id(), sample_assignment.get_id(), "delete me")
        saved = draft_repo.create(draft)
        
        result = draft_repo.delete(saved.get_id())
        assert result is True
        assert draft_repo.get_by_id(saved.get_id()) is None

    def test_delete_draft_failure(self, draft_repo):
        """Test delete failure (e.g. repo level error)"""
        # Tricky to trigger sqlite3.Error on delete without mocking or DB locks.
        # But we want to hit line 65-66.
        # Let's try to use a mock for the db to trigger the error.
        from unittest.mock import Mock
        import sqlite3
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        error_repo = DraftRepository(mock_db)
        
        result = error_repo.delete(1)
        assert result is False
        mock_db.rollback.assert_called_once()
