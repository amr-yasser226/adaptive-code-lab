import pytest
from unittest.mock import Mock
from core.services.audit_log_service import AuditLogService


@pytest.fixture
def mock_audit_repo():
    return Mock()


@pytest.fixture
def audit_log_service(mock_audit_repo):
    return AuditLogService(mock_audit_repo)


class TestAuditLogService:
    """Test suite for AuditLogService"""

    def test_log_creates_audit_entry(self, audit_log_service, mock_audit_repo):
        """Test creating a new audit log entry"""
        mock_audit_repo.save.return_value = Mock()

        result = audit_log_service.log(
            actor_user_id=1,
            action="CREATE",
            entity_type="assignment",
            entity_id=10,
            details="Created assignment",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )

        mock_audit_repo.save.assert_called_once()
        args, _ = mock_audit_repo.save.call_args
        audit = args[0]
        assert audit.get_actor_user_ID() == 1
        assert audit.action == "CREATE"
        assert audit.entityType == "assignment"
        assert audit.entity_Id == 10

    def test_log_minimal_params(self, audit_log_service, mock_audit_repo):
        """Test creating audit log with minimal parameters"""
        mock_audit_repo.save.return_value = Mock()

        result = audit_log_service.log(
            actor_user_id=1,
            action="LOGIN"
        )

        mock_audit_repo.save.assert_called_once()

    def test_get_by_id(self, audit_log_service, mock_audit_repo):
        """Test retrieving audit log by ID"""
        expected = Mock()
        mock_audit_repo.get_by_id.return_value = expected

        result = audit_log_service.get_by_id(1)

        mock_audit_repo.get_by_id.assert_called_once_with(1)
        assert result == expected

    def test_list_by_user(self, audit_log_service, mock_audit_repo):
        """Test listing audit logs by user"""
        logs = [Mock(), Mock()]
        mock_audit_repo.list_by_user.return_value = logs

        result = audit_log_service.list_by_user(1)

        mock_audit_repo.list_by_user.assert_called_once_with(1)
        assert result == logs

    def test_list_recent(self, audit_log_service, mock_audit_repo):
        """Test listing recent audit logs"""
        logs = [Mock(), Mock(), Mock()]
        mock_audit_repo.list_recent.return_value = logs

        result = audit_log_service.list_recent(limit=50)

        mock_audit_repo.list_recent.assert_called_once_with(50)
        assert result == logs

    def test_list_recent_default_limit(self, audit_log_service, mock_audit_repo):
        """Test listing recent audit logs with default limit"""
        mock_audit_repo.list_recent.return_value = []

        audit_log_service.list_recent()

        mock_audit_repo.list_recent.assert_called_once_with(100)

    def test_delete(self, audit_log_service, mock_audit_repo):
        """Test deleting an audit log"""
        mock_audit_repo.delete.return_value = True

        result = audit_log_service.delete(1)

        mock_audit_repo.delete.assert_called_once_with(1)
        assert result is True
