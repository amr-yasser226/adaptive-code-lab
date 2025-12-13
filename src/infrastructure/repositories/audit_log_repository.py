from sqlalchemy.exc import SQLAlchemyError
from core.entities.audit_log import AuditLog

class AuditLog_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT
                id, actor_user_id, action, entity_type, entity_id,
                details, ip_address, user_agent, created_at
            FROM audit_logs
            WHERE id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return AuditLog(
            id=row.id,
            actor_user_ID=row.actor_user_id,
            action=row.action,
            entityType=row.entity_type,
            entity_Id=row.entity_id,
            details=row.details,
            ip_address=row.ip_address,
            userAgent=row.user_agent,
            created_at=row.created_at
        )

    def save(self, audit: AuditLog):
        try:
            self.db.begin_transaction()
            query = """
                INSERT INTO audit_logs (
                    actor_user_id, action, entity_type, entity_id,
                    details, ip_address, user_agent, created_at
                )
                VALUES (
                    :actor_user_id, :action, :entity_type, :entity_id,
                    :details, :ip_address, :user_agent, :created_at
                )
            """
            self.db.execute(query, {
                "actor_user_id": audit.get_actor_user_ID(),
                "action": audit.action,
                "entity_type": audit.entityType,
                "entity_id": audit.entity_Id,
                "details": audit.details,
                "ip_address": audit.ip_address,
                "user_agent": audit.userAgent,
                "created_at": audit.created_at
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone().id
            self.db.commit()
            return self.get_by_id(new_id)
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def list_by_user(self, actor_user_id: int):
        query = """
            SELECT *
            FROM audit_logs
            WHERE actor_user_id = :aid
            ORDER BY created_at DESC
        """
        result = self.db.execute(query, {"aid": actor_user_id})
        rows = result.fetchall()
        return [
            AuditLog(
                id=row.id,
                actor_user_ID=row.actor_user_id,
                action=row.action,
                entityType=row.entity_type,
                entity_Id=row.entity_id,
                details=row.details,
                ip_address=row.ip_address,
                userAgent=row.user_agent,
                created_at=row.created_at
            )
            for row in rows
        ]

    def list_recent(self, limit: int = 100):
        query = """
            SELECT *
            FROM audit_logs
            ORDER BY created_at DESC
            LIMIT :limit
        """
        result = self.db.execute(query, {"limit": limit})
        rows = result.fetchall()
        return [
            AuditLog(
                id=row.id,
                actor_user_ID=row.actor_user_id,
                action=row.action,
                entityType=row.entity_type,
                entity_Id=row.entity_id,
                details=row.details,
                ip_address=row.ip_address,
                userAgent=row.user_agent,
                created_at=row.created_at
            )
            for row in rows
        ]

    def delete(self, id: int):
        try:
            self.db.begin_transaction()
            self.db.execute("DELETE FROM audit_logs WHERE id = :id", {"id": id})
            self.db.commit()
            return True
        except SQLAlchemyError:
            self.db.rollback()
            return False

