import pytest
from datetime import datetime
from core.entities.audit_log import AuditLog


class TestAuditLog:
    """Test suite for AuditLog entity"""

    def test_init(self):
        """Test AuditLog initialization"""
        audit = AuditLog(
            id=1,
            actor_user_ID=10,
            action="CREATE",
            entityType="assignment",
            entity_Id=5,
            details="Created assignment",
            ip_address="192.168.1.1",
            userAgent="Mozilla/5.0",
            created_at=datetime.now()
        )

        assert audit.get_id() == 1
        assert audit.get_actor_user_ID() == 10
        assert audit.action == "CREATE"
        assert audit.entityType == "assignment"
        assert audit.entity_Id == 5

    def test_init_minimal(self):
        """Test AuditLog with minimal parameters"""
        audit = AuditLog(
            id=1,
            actor_user_ID=10,
            action="LOGIN"
        )

        assert audit.get_id() == 1
        assert audit.action == "LOGIN"
        assert audit.entityType is None
        assert audit.details is None

    def test_get_id(self):
        """Test get_id getter"""
        audit = AuditLog(id=42, actor_user_ID=1, action="TEST")
        assert audit.get_id() == 42

    def test_get_actor_user_id(self):
        """Test get_actor_user_ID getter"""
        audit = AuditLog(id=1, actor_user_ID=99, action="TEST")
        assert audit.get_actor_user_ID() == 99

    def test_public_attributes(self):
        """Test public attributes are accessible"""
        now = datetime.now()
        audit = AuditLog(
            id=1,
            actor_user_ID=1,
            action="UPDATE",
            entityType="course",
            entity_Id=10,
            details="Updated course",
            ip_address="10.0.0.1",
            userAgent="Chrome",
            created_at=now
        )

        assert audit.action == "UPDATE"
        assert audit.entityType == "course"
        assert audit.entity_Id == 10
        assert audit.details == "Updated course"
        assert audit.ip_address == "10.0.0.1"
        assert audit.userAgent == "Chrome"
        assert audit.created_at == now
