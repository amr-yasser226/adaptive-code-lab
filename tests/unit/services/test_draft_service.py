import pytest
from unittest.mock import Mock
from core.services.draft_service import DraftService
from core.entities.draft import Draft

@pytest.fixture
def mock_draft_repo():
    return Mock()

@pytest.fixture
def draft_service(mock_draft_repo):
    return DraftService(mock_draft_repo)

class TestDraftService:
    """Test suite for DraftService"""

    def test_get_latest_draft(self, draft_service, mock_draft_repo):
        """Line 13: Successfully get latest draft"""
        mock_draft_repo.get_latest.return_value = Mock()
        result = draft_service.get_latest_draft(1, 1)
        assert result is not None
        mock_draft_repo.get_latest.assert_called_once_with(1, 1)

    def test_save_draft_success(self, draft_service, mock_draft_repo):
        """Lines 15-28: Successfully save a draft"""
        mock_draft_repo.create.return_value = True
        result = draft_service.save_draft(1, 1, "print('hi')")
        assert result is True
        mock_draft_repo.create.assert_called_once()
        args, _ = mock_draft_repo.create.call_args
        draft = args[0]
        assert draft.get_user_id() == 1
        assert draft.content == "print('hi')"

    def test_save_draft_failure_logging(self, draft_service, mock_draft_repo):
        """Line 27: Log warning when persistence fails"""
        mock_draft_repo.create.return_value = False
        result = draft_service.save_draft(1, 1, "code")
        assert result is False

    def test_save_draft_exception_handling(self, draft_service, mock_draft_repo):
        """Lines 30-31: Raise exception when repo crashes"""
        mock_draft_repo.create.side_effect = Exception("DB error")
        with pytest.raises(Exception, match="DB error"):
            draft_service.save_draft(1, 1, "code")
