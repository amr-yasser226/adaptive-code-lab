import pytest
from core.entities.hint import Hint


@pytest.mark.repo
@pytest.mark.unit
class TestHintRepo:
    """Test suite for Hint_repo"""
    
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