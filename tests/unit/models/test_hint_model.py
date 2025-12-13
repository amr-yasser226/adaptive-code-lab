import pytest
from datetime import datetime
from core.entities.hint import Hint


class TestHint:
    """Test suite for Hint entity"""

    def test_init(self):
        """Test Hint initialization"""
        now = datetime.now()
        hint = Hint(
            id=1,
            submission_id=10,
            model_used="gpt-4",
            confidence=0.85,
            hint_text="Try checking the loop condition",
            is_helpful=False,
            feedback=None,
            created_at=now
        )

        assert hint.get_id() == 1
        assert hint.get_submission_id() == 10
        assert hint.model_used == "gpt-4"
        assert hint.confidence == 0.85
        assert hint.hint_text == "Try checking the loop condition"
        assert hint.is_helpful is False

    def test_get_id(self):
        """Test get_id getter"""
        hint = Hint(
            id=42, submission_id=1, model_used="v1",
            confidence=0.5, hint_text="tip", is_helpful=False,
            feedback=None, created_at=datetime.now()
        )
        assert hint.get_id() == 42

    def test_get_submission_id(self):
        """Test get_submission_id getter"""
        hint = Hint(
            id=1, submission_id=99, model_used="v1",
            confidence=0.5, hint_text="tip", is_helpful=False,
            feedback=None, created_at=datetime.now()
        )
        assert hint.get_submission_id() == 99

    def test_is_helpful_converted_to_bool(self):
        """Test is_helpful is converted to boolean"""
        hint = Hint(
            id=1, submission_id=1, model_used="v1",
            confidence=0.5, hint_text="tip", is_helpful=1,
            feedback=None, created_at=datetime.now()
        )
        assert hint.is_helpful is True

    def test_mark_helpful(self):
        """Test mark_helpful method"""
        hint = Hint(
            id=1, submission_id=1, model_used="v1",
            confidence=0.5, hint_text="tip", is_helpful=False,
            feedback=None, created_at=datetime.now()
        )
        assert hint.is_helpful is False
        
        hint.mark_helpful()
        
        assert hint.is_helpful is True

    def test_mark_not_helpful(self):
        """Test mark_not_helpful method"""
        hint = Hint(
            id=1, submission_id=1, model_used="v1",
            confidence=0.5, hint_text="tip", is_helpful=True,
            feedback=None, created_at=datetime.now()
        )
        assert hint.is_helpful is True
        
        hint.mark_not_helpful()
        
        assert hint.is_helpful is False
