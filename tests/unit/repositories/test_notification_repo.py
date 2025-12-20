import pytest
import sqlite3
from unittest.mock import Mock
from core.entities.notification import Notification


@pytest.mark.repo
@pytest.mark.unit
class TestNotificationRepo:
    """Test suite for Notification_repo"""
    
    def test_save_notification(self, sample_user, notification_repo):
        """Test saving a new notification"""
        notification = Notification(
            id=None,
            user_id=sample_user.get_id(),
            message="New assignment posted",
            type="info",
            is_read=False,
            created_at=None,
            read_at=None,
            link="/assignments/1"
        )
        
        saved = notification_repo.save_notification(notification)
        
        assert saved is not None
        assert saved.get_id() is not None
        assert saved.message == "New assignment posted"
    
    def test_get_by_id_returns_notification(self, sample_user, notification_repo):
        """Test retrieving notification by ID"""
        notification = Notification(
            id=None,
            user_id=sample_user.get_id(),
            message="Grade available",
            type="warning",
            is_read=False,
            created_at=None,
            read_at=None,
            link=None
        )
        saved = notification_repo.save_notification(notification)
        
        retrieved = notification_repo.get_by_id(saved.get_id())
        
        assert retrieved is not None
        assert retrieved.type == "warning"

    def test_get_by_id_not_found(self, notification_repo):
        """Line 19: get_by_id returns None for non-existent ID"""
        assert notification_repo.get_by_id(9999) is None
    
    def test_find_by_user(self, sample_user, notification_repo):
        """Test finding notifications by user"""
        for i in range(3):
            notification = Notification(
                id=None,
                user_id=sample_user.get_id(),
                message=f"Message {i}",
                type="info",
                is_read=False,
                created_at=None,
                read_at=None,
                link=None
            )
            notification_repo.save_notification(notification)
        
        notifications = notification_repo.find_by_user(sample_user.get_id())
        assert len(notifications) >= 3

    def test_save_error(self, notification_repo, sample_user):
        """Line 52-55: save_notification handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        notification_repo.db = mock_db
        notification = Notification(None, sample_user.get_id(), "Msg", "info", False, None, None, None)
        assert notification_repo.save_notification(notification) is None
        mock_db.rollback.assert_called_once()

    def test_delete_error(self, notification_repo):
        """Line 85-87: delete_by_id handles sqlite3.Error"""
        mock_db = Mock()
        mock_db.execute.side_effect = sqlite3.Error("Mock error")
        notification_repo.db = mock_db
        assert notification_repo.delete_by_id(1) is False
        mock_db.rollback.assert_called_once()
    
    def test_delete_by_id_success(self, sample_user, notification_repo):
        """Test successful deletion of notification"""
        notification = Notification(None, sample_user.get_id(), "To Delete", "info", False, None, None, None)
        saved = notification_repo.save_notification(notification)
        assert notification_repo.delete_by_id(saved.get_id()) is True
        assert notification_repo.get_by_id(saved.get_id()) is None