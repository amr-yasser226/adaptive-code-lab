import pytest
import os
from flask import Flask, session
from unittest.mock import Mock


@pytest.fixture
def mock_services():
    """Create mock services."""
    services = {
        'user_repo': Mock(),
        'notification_service': Mock(),
    }
    
    mock_user = Mock()
    mock_user.get_id.return_value = 1
    mock_user.name = "Test User"
    mock_user.role = "student"
    services['user_repo'].get_by_id.return_value = mock_user
    
    mock_notification = Mock()
    mock_notification.get_id.return_value = 1
    mock_notification.message = "Test notification"
    mock_notification.is_read = False
    services['notification_service'].get_user_notifications.return_value = [mock_notification]
    services['notification_service'].get_unread_count.return_value = 5
    
    return services


@pytest.fixture
def app(mock_services):
    """Create Flask test app."""
    template_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/templates')
    
    app = Flask(__name__, template_folder=os.path.abspath(template_dir))
    app.secret_key = 'test_secret'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    def format_date(value, fmt='%b %d, %Y'):
        return value if isinstance(value, str) else 'N/A'
    
    app.jinja_env.filters['format_date'] = format_date
    
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=lambda: 'test-token')
    
    @app.context_processor
    def inject_current_user():
        user_id = session.get('user_id')
        if user_id:
            return dict(current_user=mock_services['user_repo'].get_by_id(user_id))
        return dict(current_user=None)
    
    app.extensions['services'] = mock_services
    
    from web.routes.notification import notification_bp
    from web.routes.auth import auth_bp
    
    @app.route('/')
    def index():
        return 'Home'
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(notification_bp)
    
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_session(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'student'
    return client


@pytest.mark.unit
class TestNotificationRoutes:
    
    def test_list_notifications_requires_login(self, client):
        """Test that listing notifications requires login."""
        response = client.get('/notifications/')
        assert response.status_code in [302, 401]
    
    def test_mark_read_requires_login(self, client):
        """Test marking as read requires login."""
        response = client.post('/notifications/1/read')
        assert response.status_code in [302, 401]
    
    def test_mark_unread_requires_login(self, client):
        """Test marking as unread requires login."""
        response = client.post('/notifications/1/unread')
        assert response.status_code in [302, 401]
    
    def test_delete_notification_requires_login(self, client):
        """Test deleting notification requires login."""
        response = client.post('/notifications/1/delete')
        assert response.status_code in [302, 401]
