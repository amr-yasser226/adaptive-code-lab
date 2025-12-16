from datetime import datetime
from core.entities.notification import Notification
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


class NotificationService:
    def __init__(self, notification_repo):
        self.notification_repo = notification_repo

    def notify(self, user_id, message, type="info", link=None):
        notification = Notification(
            id=None,
            user_id=user_id,
            message=message,
            type=type,
            is_read=False,
            created_at=datetime.now(),
            read_at=None,
            link=link
        )
        return self.notification_repo.save_notification(notification)
    
    def get_user_notifications(self, user, only_unread=False):
        notifications = self.notification_repo.find_by_user(user.get_id())

        if only_unread:
            notifications = [n for n in notifications if not n.is_read]

        return notifications

    def mark_as_read(self, user, notification_id):
        notification = self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise ValidationError("Notification not found")

        if notification.get_user_id() != user.get_id():
            raise AuthError("You cannot modify this notification")

        notification.mark_as_read(datetime.now())
        return self.notification_repo.save_notification(notification)

    def mark_as_unread(self, user, notification_id):
        notification = self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise ValidationError("Notification not found")

        if notification.get_user_id() != user.get_id():
            raise AuthError("You cannot modify this notification")

        notification.mark_as_unread()
        return self.notification_repo.save_notification(notification)


    def delete(self, user, notification_id):
        notification = self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise ValidationError("Notification not found")

        if notification.get_user_id() != user.get_id():
            raise AuthError("You cannot delete this notification")

        return self.notification_repo.delete_by_id(notification_id)
