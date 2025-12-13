from sqlalchemy.exc import SQLAlchemyError
from core.entities.notification import Notification


class Notification_repo:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id: int):
        query = """
            SELECT
                n.id, n.user_id, n.message, n.type, n.is_read, n.created_at, n.read_at, n.link
            FROM notifications n
            WHERE n.id = :id
        """
        result = self.db.execute(query, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return Notification(
            id=row.id,
            user_id=row.user_id,
            message=row.message,
            type=row.type,
            is_read=row.is_read,
            created_at=row.created_at,
            read_at=row.read_at,
            link=row.link
        )

    def save_notification(self, notification: Notification):
        try:
            query = """
                INSERT INTO notifications (
                    user_id, message, type, is_read, read_at, link
                )
                VALUES (
                    :user_id, :message, :type, :is_read, :read_at, :link
                )
            """
            self.db.execute(query, {
                "user_id": notification.get_user_id(),
                "message": notification.message,
                "type": notification.type,
                "is_read": int(notification.is_read),
                "read_at": notification.read_at,
                "link": notification.link
            })
            new_id = self.db.execute("SELECT last_insert_rowid() as id").fetchone()[0]
            self.db.commit()
            return self.get_by_id(new_id)
        except Exception as e:
            self.db.rollback()
            print("Error saving notification:", e)
            return None

    def find_by_user(self, userId: int):
        query = """
            SELECT
                n.id, n.user_id, n.message, n.type, n.is_read, n.created_at, n.read_at, n.link
            FROM notifications n
            WHERE n.user_id = :user_id
            ORDER BY n.created_at DESC
        """
        result = self.db.execute(query, {"user_id": userId})
        notifications = []
        for row in result.fetchall():
            notifications.append(Notification(
                id=row.id,
                user_id=row.user_id,
                message=row.message,
                type=row.type,
                is_read=row.is_read,
                created_at=row.created_at,
                read_at=row.read_at,
                link=row.link
            ))
        return notifications
    def delete_by_id(self , id : int ):
        try : 
            query = "DELETE FROM notifications WHERE id =:id"
            self.db.execute(query, {"id": id})
            self.db.commit()
            return True 
        except SQLAlchemyError : 
            self.db.rollback()
            return False
            


