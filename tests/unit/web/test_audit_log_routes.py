import pytest
import os
import sqlite3
from unittest.mock import Mock, patch
from flask import Flask, session, Blueprint
from core.entities.user import User

@pytest.fixture
def mock_services():
    ms = {
        'audit_service': Mock(),
        'user_repo': Mock(),
        'notification_service': Mock(),
        'enrollment_service': Mock(),
    }
    ms['audit_service'].list_recent.return_value = []
    ms['audit_service'].list_by_user.return_value = []
    ms['audit_service'].get_by_id.return_value = None
    ms['notification_service'].get_user_notifications.return_value = []
    ms['enrollment_service'].get_student_enrollments.return_value = []
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
            return {'current_user': user, 'csrf_token': lambda: 'mock_token'}
        return {'current_user': None, 'csrf_token': lambda: 'mock_token'}

    def format_date(value, fmt='%b %d, %Y'):
        if value is None: return 'N/A'
        return value.strftime(fmt) if hasattr(value, 'strftime') else str(value)
    app.jinja_env.filters['format_date'] = format_date
        
    app.extensions['services'] = mock_services
    
    from web.routes.audit_log import audit_bp
    app.register_blueprint(audit_bp)
    
    admin_bp = Blueprint('admin', __name__)
    @admin_bp.route('/dashboard')
    def dashboard(): 
        from flask import get_flashed_messages
        return f"Admin Dash {' '.join(get_flashed_messages())}"
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    instructor_bp = Blueprint('instructor', __name__)
    @instructor_bp.route('/dashboard')
    def dashboard_instructor(): return 'Instructor Dash'
    @instructor_bp.route('/analytics')
    def analytics(): return 'Analytics'
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    
    student_bp = Blueprint('student', __name__)
    @student_bp.route('/dashboard')
    def dashboard_student(): return 'Student Dash'
    @student_bp.route('/assignments')
    def assignments(): return 'Assignments'
    @student_bp.route('/profile')
    def profile(): return 'Profile'
    # Alias dashboard for url_for('student.dashboard')
    @student_bp.route('/dashboard-real')
    def dashboard(): return 'Real Student Dash'
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
def admin_session(client, mock_services):
    mock_user = User(1, "Admin", "a@t.com", "p", "admin")
    mock_services['user_repo'].get_by_id.return_value = mock_user
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'admin'
    return mock_user

class TestAuditLogRoutes:
    def test_recent_audit_success(self, client, admin_session, mock_services):
        mock_services['audit_service'].list_recent.return_value = []
        response = client.get('/audit/', follow_redirects=True)
        assert response.status_code == 200
        assert b'Audit' in response.data or b'audit' in response.data

    def test_recent_audit_error(self, client, admin_session, mock_services):
        mock_services['audit_service'].list_recent.side_effect = sqlite3.Error("DB fail")
        response = client.get('/audit/', follow_redirects=True)
        assert b'DB fail' in response.data

    def test_audit_by_user_success(self, client, admin_session, mock_services):
        mock_services['audit_service'].list_by_user.return_value = []
        response = client.get('/audit/user/1', follow_redirects=True)
        assert response.status_code == 200

    def test_audit_by_user_error(self, client, admin_session, mock_services):
        mock_services['audit_service'].list_by_user.side_effect = Exception("fail")
        response = client.get('/audit/user/1', follow_redirects=True)
        assert b'fail' in response.data

    def test_audit_detail_success(self, client, admin_session, mock_services):
        mock_services['audit_service'].get_by_id.return_value = {'id': 1, 'action': 'login'}
        response = client.get('/audit/1', follow_redirects=True)
        assert response.status_code == 200

    def test_audit_detail_not_found(self, client, admin_session, mock_services):
        mock_services['audit_service'].get_by_id.return_value = None
        response = client.get('/audit/1', follow_redirects=True)
        assert b'Audit entry not found' in response.data

    def test_audit_detail_error(self, client, admin_session, mock_services):
        mock_services['audit_service'].get_by_id.side_effect = sqlite3.Error("fail")
        response = client.get('/audit/1', follow_redirects=True)
        assert b'fail' in response.data

    def test_delete_audit_success(self, client, admin_session, mock_services):
        mock_services['audit_service'].delete.return_value = True
        response = client.post('/audit/1/delete', follow_redirects=True)
        assert b'Audit entry deleted' in response.data

    def test_delete_audit_fail(self, client, admin_session, mock_services):
        mock_services['audit_service'].delete.return_value = False
        response = client.post('/audit/1/delete', follow_redirects=True)
        assert b'Failed to delete audit entry' in response.data

    def test_delete_audit_error(self, client, admin_session, mock_services):
        mock_services['audit_service'].delete.side_effect = Exception("error")
        response = client.post('/audit/1/delete', follow_redirects=True)
        assert b'error' in response.data
