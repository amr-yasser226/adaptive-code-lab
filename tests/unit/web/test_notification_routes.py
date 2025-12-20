import pytest
import os
import sqlite3
from unittest.mock import Mock, patch
from flask import Flask, session, Blueprint
from core.entities.user import User
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError

@pytest.fixture
def mock_services():
    ms = {
        'notification_service': Mock(),
        'user_repo': Mock(),
    }
    ms['notification_service'].get_user_notifications.return_value = []
    return ms

@pytest.fixture
def app(mock_services):
    template_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/templates')
    app = Flask(__name__, template_folder=os.path.abspath(template_dir))
    app.secret_key = 'test_secret'
    app.config['TESTING'] = True
    
    @app.context_processor
    def inject_current_user():
        if 'user_id' in session:
            user = mock_services['user_repo'].get_by_id(session['user_id'])
            return {'current_user': user}
        return {'current_user': None}

    def format_date(value, fmt='%b %d, %Y'):
        if value is None: return 'N/A'
        return value.strftime(fmt) if hasattr(value, 'strftime') else str(value)
    
    app.jinja_env.filters['format_date'] = format_date
        
    app.extensions['services'] = mock_services
    
    from web.routes.notification import notification_bp
    app.register_blueprint(notification_bp)
    
    student_bp = Blueprint('student', __name__)
    @student_bp.route('/dashboard')
    def dashboard(): return 'Student Dash'
    @student_bp.route('/assignments')
    def assignments(): return 'Assignments'
    @student_bp.route('/profile')
    def profile(): return 'Profile'
    app.register_blueprint(student_bp, url_prefix='/student')
    
    auth_bp = Blueprint('auth', __name__)
    @auth_bp.route('/login')
    def login(): return 'Login'
    @auth_bp.route('/logout')
    def logout(): return 'Logout'
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    @app.route('/')
    def index():
        from flask import get_flashed_messages
        return f"Index {' '.join(get_flashed_messages())}"
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_session(client, mock_services):
    mock_user = User(1, "User", "u@t.com", "p", "student")
    mock_services['user_repo'].get_by_id.return_value = mock_user
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'student'
    return mock_user

class TestNotificationRoutes:
    def test_list_notifications_success(self, client, user_session, mock_services):
        mock_services['notification_service'].get_user_notifications.return_value = []
        response = client.get('/notifications/')
        assert response.status_code == 200
        assert b'notifications' in response.data or b'Notifications' in response.data

    def test_list_notifications_unread_filter(self, client, user_session, mock_services):
        mock_services['notification_service'].get_user_notifications.return_value = []
        response = client.get('/notifications/?unread=1')
        assert response.status_code == 200
        mock_services['notification_service'].get_user_notifications.assert_called_with(
            user=user_session,
            only_unread=True
        )

    def test_list_notifications_auth_error(self, client, user_session, mock_services):
        mock_services['notification_service'].get_user_notifications.side_effect = AuthError("Denied")
        response = client.get('/notifications/', follow_redirects=True)
        assert b'Denied' in response.data

    def test_list_notifications_db_error(self, client, user_session, mock_services):
        mock_services['notification_service'].get_user_notifications.side_effect = sqlite3.Error("DB fail")
        response = client.get('/notifications/', follow_redirects=True)
        assert b'DB fail' in response.data

    def test_mark_as_read_success(self, client, user_session, mock_services):
        response = client.post('/notifications/1/read')
        assert response.status_code == 302
        # Redirect to notification list by default if no referrer
        assert '/notifications/' in response.location 
        mock_services['notification_service'].mark_as_read.assert_called_with(
            user=user_session,
            notification_id=1
        )

    def test_mark_as_read_error(self, client, user_session, mock_services):
        mock_services['notification_service'].mark_as_read.side_effect = ValidationError("Invalid ID")
        response = client.post('/notifications/1/read', follow_redirects=True)
        assert b'Invalid ID' in response.data

    def test_mark_as_read_db_error(self, client, user_session, mock_services):
        mock_services['notification_service'].mark_as_read.side_effect = sqlite3.Error("DB Error")
        response = client.post('/notifications/1/read', follow_redirects=True)
        assert b'DB Error' in response.data

    def test_mark_as_unread_success(self, client, user_session, mock_services):
        response = client.post('/notifications/1/unread')
        assert response.status_code == 302
        mock_services['notification_service'].mark_as_unread.assert_called_with(
            user=user_session,
            notification_id=1
        )

    def test_mark_as_unread_error(self, client, user_session, mock_services):
        mock_services['notification_service'].mark_as_unread.side_effect = AuthError("Wrong user")
        response = client.post('/notifications/1/unread', follow_redirects=True)
        assert b'Wrong user' in response.data

    def test_delete_notification_success(self, client, user_session, mock_services):
        response = client.post('/notifications/1/delete')
        assert response.status_code == 302
        mock_services['notification_service'].delete.assert_called_with(
            user=user_session,
            notification_id=1
        )

    def test_delete_notification_error(self, client, user_session, mock_services):
        mock_services['notification_service'].delete.side_effect = ValidationError("Not found")
        response = client.post('/notifications/1/delete', follow_redirects=True)
        assert b'Not found' in response.data
