import pytest
from unittest.mock import Mock
from core.services.hint_service import HintService


@pytest.fixture
def mock_hint_repo():
    return Mock()


@pytest.fixture
def mock_submission_repo():
    return Mock()


@pytest.fixture
def mock_ai_client():
    client = Mock()
    client.generate_hint.return_value = {
        "model": "gpt-4",
        "confidence": 0.85,
        "text": "Try checking your loop condition"
    }
    return client


@pytest.fixture
def hint_service(mock_hint_repo, mock_submission_repo, mock_ai_client):
    return HintService(mock_hint_repo, mock_submission_repo, mock_ai_client)


class TestHintService:
    """Test suite for HintService"""

    def test_generate_hint_success(self, hint_service, mock_submission_repo,
                                    mock_ai_client, mock_hint_repo):
        """Test successful hint generation"""
        mock_submission_repo.get_by_id.return_value = Mock()
        mock_hint_repo.create.return_value = Mock()

        result = hint_service.generate_hint(1)

        mock_ai_client.generate_hint.assert_called_once_with(submission_id=1)
        mock_hint_repo.create.assert_called_once()

    def test_generate_hint_submission_not_found(self, hint_service, mock_submission_repo):
        """Submission not found raises Exception"""
        mock_submission_repo.get_by_id.return_value = None

        with pytest.raises(Exception, match="Submission not found"):
            hint_service.generate_hint(999)

    def test_generate_hint_creates_correct_entity(self, hint_service, mock_submission_repo,
                                                   mock_ai_client, mock_hint_repo):
        """Generated hint has correct attributes from AI response"""
        mock_submission_repo.get_by_id.return_value = Mock()
        mock_hint_repo.create.return_value = Mock()

        hint_service.generate_hint(1)

        args, _ = mock_hint_repo.create.call_args
        hint = args[0]
        assert hint.model_used == "gpt-4"
        assert hint.confidence == 0.85
        assert hint.hint_text == "Try checking your loop condition"
        assert hint.is_helpful is False

    def test_mark_hint_helpful(self, hint_service, mock_hint_repo):
        """Test marking hint as helpful"""
        hint = Mock()
        mock_hint_repo.get_by_id.return_value = hint
        mock_hint_repo.update.return_value = hint

        result = hint_service.mark_hint_helpful(1)

        hint.mark_helpful.assert_called_once()
        mock_hint_repo.update.assert_called_once()

    def test_mark_hint_helpful_not_found(self, hint_service, mock_hint_repo):
        """Hint not found raises Exception"""
        mock_hint_repo.get_by_id.return_value = None

        with pytest.raises(Exception, match="Hint not found"):
            hint_service.mark_hint_helpful(999)

    def test_mark_hint_not_helpful(self, hint_service, mock_hint_repo):
        """Test marking hint as not helpful"""
        hint = Mock()
        mock_hint_repo.get_by_id.return_value = hint
        mock_hint_repo.update.return_value = hint

        result = hint_service.mark_hint_not_helpful(1)

        hint.mark_not_helpful.assert_called_once()
        mock_hint_repo.update.assert_called_once()

    def test_list_hints_for_submission(self, hint_service, mock_hint_repo):
        """Test listing hints for submission"""
        hints = [Mock(), Mock()]
        mock_hint_repo.list_by_submission.return_value = hints

        result = hint_service.list_hints_for_submission(1)

        mock_hint_repo.list_by_submission.assert_called_once_with(1)
        assert result == hints
