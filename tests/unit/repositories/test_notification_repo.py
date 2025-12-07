import pytest
from Backend.Model.Notification_model import Notification


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