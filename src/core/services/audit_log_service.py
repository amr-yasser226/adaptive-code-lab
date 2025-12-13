from datetime import datetime
from core.entities.audit_log import AuditLog


class AuditLogService:
    def __init__(self, audit_repo):
        self.audit_repo = audit_repo

    # --------------------------------------------------
    # CORE LOGGING METHOD
    # --------------------------------------------------
    def log(
        self,
        actor_user_id: int,
        action: str,
        entity_type: str = None,
        entity_id: int = None,
        details: str = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        audit = AuditLog(
            id=None,
            actor_user_ID=actor_user_id,
            action=action,
            entityType=entity_type,
            entity_Id=entity_id,
            details=details,
            ip_address=ip_address,
            userAgent=user_agent,
            created_at=datetime.utcnow()
        )

        return self.audit_repo.save(audit)

    # --------------------------------------------------
    # READ METHODS
    # --------------------------------------------------
    def get_by_id(self, audit_id: int):
        return self.audit_repo.get_by_id(audit_id)

    def list_by_user(self, user_id: int):
        return self.audit_repo.list_by_user(user_id)

    def list_recent(self, limit: int = 100):
        return self.audit_repo.list_recent(limit)

    # --------------------------------------------------
    # OPTIONAL: ADMIN CLEANUP
    # --------------------------------------------------
    def delete(self, audit_id: int):
        return self.audit_repo.delete(audit_id)
