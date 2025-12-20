import pytest
import sqlite3
from unittest.mock import Mock
from core.entities.hint import Hint


@pytest.mark.repo
@pytest.mark.unit
class TestHintRepo:
    """Test suite for HintRepository"""
    
    def test_create_hint(self, sample_submission, hint_repo):
        """Test creating a new hint"""
        hint = Hint(
            id=None,
            submission_id=sample_submission.get_id(),
            model_used="gpt-4",
            confidence=0.85,
            hint_text="Try checking your loop condition",
            is_helpful=False,
            feedback=None,
            created_at=None
        )
        
        saved = hint_repo.create(hint)
        
        assert saved is not None
        assert saved.get_id() is not None
        assert saved.hint_text == "Try checking your loop condition"
    
    def test_get_by_id_returns_hint(self, sample_submission, hint_repo):
        """Test retrieving hint by ID"""
        hint = Hint(
            id=None,
            submission_id=sample_submission.get_id(),
            model_used="gpt-4",
            confidence=0.90,
            hint_text="Consider edge cases",
            is_helpful=False,
            feedback=None,
            created_at=None
        )
        saved = hint_repo.create(hint)
        
        retrieved = hint_repo.get_by_id(saved.get_id())
        
        assert retrieved is not None
        assert retrieved.confidence == 0.90

    def test_get_by_id_not_found(self, hint_repo):
        """Line 19: get_by_id returns None for non-existent ID"""
        assert hint_repo.get_by_id(9999) is None
    
    def test_update_hint(self, sample_submission, hint_repo):
        """Test updating hint"""
        hint = Hint(
            id=None,
            submission_id=sample_submission.get_id(),
            model_used="gpt-4",
            confidence=0.80,
            hint_text="Original hint",
            is_helpful=False,
            feedback=None,
            created_at=None
        )
        saved = hint_repo.create(hint)
        
        saved.hint_text = "Updated hint"
        updated = hint_repo.update(saved)
        
        assert updated.hint_text == "Updated hint"
    
    def test_delete_hint(self, sample_submission, hint_repo):
        """Test deleting hint"""
        hint = Hint(
            id=None,
            submission_id=sample_submission.get_id(),
            model_used="gpt-4",
            confidence=0.80,
            hint_text="To delete",
            is_helpful=False,
            feedback=None,
            created_at=None
        )
        saved = hint_repo.create(hint)
        
        result = hint_repo.delete(saved.get_id())
        
        assert result is True
    
    def test_list_by_submission(self, sample_submission, hint_repo):
        """Test listing hints by submission"""
        for i in range(3):
            hint = Hint(
                id=None,
                submission_id=sample_submission.get_id(),
                model_used="gpt-4",
                confidence=0.80 + i*0.05,
                hint_text=f"Hint {i}",
                is_helpful=False,
                feedback=None,
                created_at=None
            )
            hint_repo.create(hint)
        
        hints = hint_repo.list_by_submission(sample_submission.get_id())
        assert len(hints) >= 3
    
    def test_mark_helpful(self, sample_submission, hint_repo):
        """Test marking hint as helpful"""
        hint = Hint(
            id=None,
            submission_id=sample_submission.get_id(),
            model_used="gpt-4",
            confidence=0.80,
            hint_text="Helpful hint",
            is_helpful=False,
            feedback=None,
            created_at=None
        )
        saved = hint_repo.create(hint)
        
        marked = hint_repo.mark_helpful(saved.get_id())
        
        assert marked.is_helpful is True
    
    def test_mark_not_helpful(self, sample_submission, hint_repo):
        """Test marking hint as not helpful"""
        hint = Hint(
            id=None,
            submission_id=sample_submission.get_id(),
            model_used="gpt-4",
            confidence=0.80,
            hint_text="Not helpful hint",
            is_helpful=True,
            feedback=None,
            created_at=None
        )
        saved = hint_repo.create(hint)
        
        marked = hint_repo.mark_not_helpful(saved.get_id())
        
        assert marked.is_helpful is False

    def test_create_error(self, hint_repo, sample_submission):
        """Line 55-57: create handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        hint_repo.db = mock_db
        hint = Hint(None, sample_submission.get_id(), "m", 0.5, "t", False, None, None)
        assert hint_repo.create(hint) is None
        mock_db.rollback.assert_called_once()

    def test_update_error(self, hint_repo, sample_submission):
        """Line 81-83: update handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        hint_repo.db = mock_db
        hint = Hint(1, sample_submission.get_id(), "m", 0.5, "t", False, None, None)
        assert hint_repo.update(hint) is None
        mock_db.rollback.assert_called_once()

    def test_delete_error(self, hint_repo):
        """Line 90-92: delete handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        hint_repo.db = mock_db
        assert hint_repo.delete(1) is False
        mock_db.rollback.assert_called_once()

    def test_mark_helpful_error(self, hint_repo):
        """Line 122-124: mark_helpful handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        hint_repo.db = mock_db
        assert hint_repo.mark_helpful(1) is None
        mock_db.rollback.assert_called_once()

    def test_mark_not_helpful_error(self, hint_repo):
        """Line 131-133: mark_not_helpful handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        hint_repo.db = mock_db
        assert hint_repo.mark_not_helpful(1) is None
        mock_db.rollback.assert_called_once()