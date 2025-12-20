import pytest
from unittest.mock import Mock
from core.services.notification_service import NotificationService
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_notification_repo():
    return Mock()


@pytest.fixture
def notification_service(mock_notification_repo):
    return NotificationService(mock_notification_repo)


@pytest.fixture
def user():
    u = Mock()
    u.get_id.return_value = 1
    return u


class TestNotificationService:
    """Test suite for NotificationService"""

    def test_notify_creates_notification(self, notification_service, mock_notification_repo):
        """Test creating a notification"""
        mock_notification_repo.save_notification.return_value = Mock()

        result = notification_service.notify(
            user_id=1,
            message="New submission graded",
            type="info",
            link="/submissions/1"
        )

        mock_notification_repo.save_notification.assert_called_once()
        args, _ = mock_notification_repo.save_notification.call_args
        notif = args[0]
        assert notif.get_user_id() == 1
        assert notif.message == "New submission graded"

    def test_get_user_notifications(self, notification_service, user, mock_notification_repo):
        """Test getting user notifications"""
        notifs = [Mock(), Mock()]
        mock_notification_repo.find_by_user.return_value = notifs

        result = notification_service.get_user_notifications(user)

        mock_notification_repo.find_by_user.assert_called_once_with(1)
        assert result == notifs

    def test_get_user_notifications_only_unread(self, notification_service, user, mock_notification_repo):
        """Test getting only unread notifications"""
        read_notif = Mock()
        read_notif.is_read = True
        unread_notif = Mock()
        unread_notif.is_read = False
        mock_notification_repo.find_by_user.return_value = [read_notif, unread_notif]

        result = notification_service.get_user_notifications(user, only_unread=True)

        assert len(result) == 1
        assert result[0] == unread_notif

    def test_mark_as_read_success(self, notification_service, user, mock_notification_repo):
        """Test marking notification as read"""
        notif = Mock()
        notif.get_user_id.return_value = 1
        mock_notification_repo.get_by_id.return_value = notif
        mock_notification_repo.save_notification.return_value = notif

        result = notification_service.mark_as_read(user, 1)

        notif.mark_as_read.assert_called_once()
        mock_notification_repo.save_notification.assert_called_once()

    def test_mark_as_read_not_found(self, notification_service, user, mock_notification_repo):
        """Notification not found raises ValidationError"""
        mock_notification_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Notification not found"):
            notification_service.mark_as_read(user, 999)

    def test_mark_as_read_not_owner(self, notification_service, user, mock_notification_repo):
        """Cannot mark another user's notification"""
        notif = Mock()
        notif.get_user_id.return_value = 999
        mock_notification_repo.get_by_id.return_value = notif

        with pytest.raises(AuthError, match="You cannot modify this notification"):
            notification_service.mark_as_read(user, 1)

    def test_mark_as_unread_success(self, notification_service, user, mock_notification_repo):
        """Test marking notification as unread"""
        notif = Mock()
        notif.get_user_id.return_value = 1
        mock_notification_repo.get_by_id.return_value = notif
        mock_notification_repo.save_notification.return_value = notif

        result = notification_service.mark_as_unread(user, 1)

        notif.mark_as_unread.assert_called_once()

    def test_delete_success(self, notification_service, user, mock_notification_repo):
        """Test deleting a notification"""
        notif = Mock()
        notif.get_user_id.return_value = 1
        mock_notification_repo.get_by_id.return_value = notif
        mock_notification_repo.delete_by_id.return_value = True

        result = notification_service.delete(user, 1)

        mock_notification_repo.delete_by_id.assert_called_once_with(1)

    def test_delete_not_found(self, notification_service, user, mock_notification_repo):
        """Delete notification not found raises ValidationError"""
        mock_notification_repo.get_by_id.return_value = None

        with pytest.raises(ValidationError, match="Notification not found"):
            notification_service.delete(user, 999)

    def test_delete_not_owner(self, notification_service, user, mock_notification_repo):
        """Cannot delete another user's notification"""
        notif = Mock()
        notif.get_user_id.return_value = 999
        mock_notification_repo.get_by_id.return_value = notif

        with pytest.raises(AuthError, match="You cannot delete this notification"):
            notification_service.delete(user, 1)

    def test_mark_as_unread_not_found(self, notification_service, user, mock_notification_repo):
        """Line 46: ValidationError when notification to mark as unread is not found"""
        mock_notification_repo.get_by_id.return_value = None
        with pytest.raises(ValidationError, match="Notification not found"):
            notification_service.mark_as_unread(user, 999)

    def test_mark_as_unread_not_owner(self, notification_service, user, mock_notification_repo):
        """Line 49: AuthError when marking another user's notification as unread"""
        notif = Mock()
        notif.get_user_id.return_value = 999
        mock_notification_repo.get_by_id.return_value = notif
        with pytest.raises(AuthError, match="You cannot modify this notification"):
            notification_service.mark_as_unread(user, 1)
