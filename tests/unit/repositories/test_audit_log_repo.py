import pytest
import sqlite3
from unittest.mock import Mock
from core.entities.audit_log import AuditLog


@pytest.mark.repo
@pytest.mark.unit
class TestAuditLogRepo:
    """Test suite for AuditLogRepository"""
    
    def test_save_audit_log(self, sample_user, audit_log_repo):
        """Test saving a new audit log"""
        audit = AuditLog(
            id=None,
            actor_user_ID=sample_user.get_id(),
            action="CREATE",
            entityType="assignment",
            entity_Id=1,
            details="Created new assignment",
            ip_address="192.168.1.1",
            userAgent="Mozilla/5.0",
            created_at=None
        )
        
        saved = audit_log_repo.save(audit)
        
        assert saved is not None
        assert saved.get_id() is not None
        assert saved.action == "CREATE"
    
    def test_get_by_id_returns_audit_log(self, sample_user, audit_log_repo):
        """Test retrieving audit log by ID"""
        audit = AuditLog(
            id=None,
            actor_user_ID=sample_user.get_id(),
            action="UPDATE",
            entityType="course",
            entity_Id=2,
            details="Updated course details",
            ip_address="192.168.1.2",
            userAgent="Chrome/100.0",
            created_at=None
        )
        saved = audit_log_repo.save(audit)
        
        retrieved = audit_log_repo.get_by_id(saved.get_id())
        
        assert retrieved is not None
        assert retrieved.action == "UPDATE"

    def test_get_by_id_not_found(self, audit_log_repo):
        """Line 19: get_by_id returns None for non-existent ID"""
        assert audit_log_repo.get_by_id(9999) is None
    
    def test_list_by_user(self, sample_user, audit_log_repo):
        """Test listing audit logs by user"""
        for i in range(3):
            audit = AuditLog(
                id=None,
                actor_user_ID=sample_user.get_id(),
                action=f"ACTION_{i}",
                entityType="test",
                entity_Id=i,
                details=f"Details {i}",
                ip_address="192.168.1.1",
                userAgent="Browser",
                created_at=None
            )
            audit_log_repo.save(audit)
        
        logs = audit_log_repo.list_by_user(sample_user.get_id())
        assert len(logs) >= 3
    
    def test_list_recent(self, sample_user, audit_log_repo):
        """Test listing recent audit logs"""
        for i in range(5):
            audit = AuditLog(
                id=None,
                actor_user_ID=sample_user.get_id(),
                action="TEST",
                entityType="entity",
                entity_Id=i,
                details=f"Test {i}",
                ip_address="192.168.1.1",
                userAgent="Browser",
                created_at=None
            )
            audit_log_repo.save(audit)
        
        recent = audit_log_repo.list_recent(limit=3)
        assert len(recent) <= 3
    
    def test_delete_audit_log(self, sample_user, audit_log_repo):
        """Test deleting audit log"""
        audit = AuditLog(
            id=None,
            actor_user_ID=sample_user.get_id(),
            action="DELETE_TEST",
            entityType="test",
            entity_Id=99,
            details="To be deleted",
            ip_address="192.168.1.1",
            userAgent="Browser",
            created_at=None
        )
        saved = audit_log_repo.save(audit)
        
        result = audit_log_repo.delete(saved.get_id())
        
        assert result is True
        retrieved = audit_log_repo.get_by_id(saved.get_id())
        assert retrieved is None

    def test_save_error(self, audit_log_repo, sample_user):
        """Line 57-59: save handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        audit_log_repo.db = mock_db
        audit = AuditLog(None, sample_user.get_id(), "A", "E", 1, "D", "I", "U", None)
        assert audit_log_repo.save(audit) is None
        mock_db.rollback.assert_called_once()

    def test_delete_error(self, audit_log_repo):
        """Line 114-116: delete handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        audit_log_repo.db = mock_db
        assert audit_log_repo.delete(1) is False
        mock_db.rollback.assert_called_once()