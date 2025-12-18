import pytest
import os
from datetime import datetime as dt
from unittest.mock import Mock, MagicMock
from flask import Flask
from core.entities.user import User
from core.exceptions.auth_error import AuthError
from core.exceptions.validation_error import ValidationError


@pytest.fixture
def mock_services():
    """Create mock services for testing."""
    return {
        'auth_service': Mock(),
        'user_repo': Mock(),
        'admin_service': Mock(),
        'student_service': Mock(),
        'assignment_repo': Mock(),
        'instructor_service': Mock(),
        'submission_repo': Mock(),
        'course_repo': Mock(),
        'enrollment_repo': Mock(),
    }


@pytest.fixture
def app(mock_services):
    """Create a test Flask app with admin and related blueprints."""
    template_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/templates')
    static_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/static')
    
    app = Flask(__name__, 
                template_folder=os.path.abspath(template_dir),
                static_folder=os.path.abspath(static_dir))
    app.secret_key = 'test_secret'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    # Add csrf_token to template context
    @app.context_processor
    def inject_csrf_token():
        return {'csrf_token': lambda: ''}
    
    # Add current_user context processor (templates require this)
    @app.context_processor
    def inject_current_user():
        from flask import session
        if 'user_id' in session:
            user = mock_services['user_repo'].get_by_id(session['user_id'])
            return {'current_user': user}
        return {'current_user': None}
    
    # format_date filter
    def format_date(value, fmt='%b %d, %Y'):
        if value is None:
            return 'N/A'
        if isinstance(value, str):
            for parse_fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                try:
                    value = dt.strptime(value, parse_fmt)
                    break
                except ValueError:
                    continue
            else:
                return value
        return value.strftime(fmt)
    
    app.jinja_env.filters['format_date'] = format_date
    
    # Inject mock services
    app.extensions['services'] = mock_services
    
    # Stub index route
    @app.route('/')
    def index():
        return 'Home'
    
    # Register blueprints
    from web.routes.auth import auth_bp
    from web.routes.student import student_bp
    from web.routes.instructor import instructor_bp
    from web.routes.admin import admin_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    app.register_blueprint(admin_bp)  # admin_bp has its own url_prefix
    
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_session(client):
    """Set up an authenticated admin session."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'admin'
        sess['logged_in'] = True


@pytest.fixture
def mock_admin_user():
    """Create a mock admin user."""
    return User(1, "Test Admin", "admin@test.com", "hashed", "admin")


@pytest.mark.unit
class TestAdminRoutes:

    def test_dashboard_unauthenticated_redirects(self, client):
        """Test that unauthenticated access redirects to login."""
        response = client.get('/admin/dashboard')
        assert response.status_code == 302
        assert '/login' in response.location or 'auth' in response.location.lower()

    def test_dashboard_non_admin_role_redirects(self, client, mock_services):
        """Test that non-admin role cannot access admin dashboard."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'student'
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 302  # Redirected due to role check

    def test_dashboard_renders_for_admin(self, client, mock_services, admin_session):
        """Test that dashboard renders for authenticated admin."""
        response = client.get('/admin/dashboard')
        assert response.status_code == 200

    def test_manage_user_success(self, client, mock_services, admin_session, mock_admin_user):
        """Test managing user account successfully."""
        mock_services['user_repo'].get_by_id.return_value = mock_admin_user
        mock_services['admin_service'].manage_user_account.return_value = None
        
        response = client.post('/admin/users/2/manage', data={
            'action': 'deactivate'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        mock_services['admin_service'].manage_user_account.assert_called_once()

    def test_manage_user_auth_error(self, client, mock_services, admin_session, mock_admin_user):
        """Test managing user with auth error."""
        mock_services['user_repo'].get_by_id.return_value = mock_admin_user
        mock_services['admin_service'].manage_user_account.side_effect = AuthError("Not authorized")
        
        response = client.post('/admin/users/2/manage', data={
            'action': 'deactivate'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show error message
        assert b'Not authorized' in response.data or b'error' in response.data.lower()

    def test_generate_report(self, client, mock_services, admin_session, mock_admin_user):
        """Test generating a report."""
        mock_services['user_repo'].get_by_id.return_value = mock_admin_user
        mock_services['admin_service'].generate_report.return_value = {
            'title': 'User Report',
            'data': []
        }
        
        response = client.get('/admin/reports/users')
        assert response.status_code == 200

    def test_generate_report_validation_error(self, client, mock_services, admin_session, mock_admin_user):
        """Test report generation with validation error."""
        mock_services['user_repo'].get_by_id.return_value = mock_admin_user
        mock_services['admin_service'].generate_report.side_effect = ValidationError("Invalid report type")
        
        response = client.get('/admin/reports/invalid_type', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to dashboard with error

    def test_configure_system_setting(self, client, mock_services, admin_session, mock_admin_user):
        """Test configuring a system setting."""
        mock_services['user_repo'].get_by_id.return_value = mock_admin_user
        mock_services['admin_service'].configure_system_setting.return_value = None
        
        response = client.post('/admin/settings', data={
            'key': 'max_submission_size',
            'value': '10MB'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        mock_services['admin_service'].configure_system_setting.assert_called_once()

    def test_export_db_dump(self, client, mock_services, admin_session, mock_admin_user):
        """Test exporting database dump."""
        mock_services['user_repo'].get_by_id.return_value = mock_admin_user
        mock_services['admin_service'].export_db_dump.return_value = None
        
        response = client.post('/admin/db/export', data={
            'output_path': '/tmp/backup.sql'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        mock_services['admin_service'].export_db_dump.assert_called_once()

    def test_export_db_dump_validation_error(self, client, mock_services, admin_session, mock_admin_user):
        """Test database export with validation error."""
        mock_services['user_repo'].get_by_id.return_value = mock_admin_user
        mock_services['admin_service'].export_db_dump.side_effect = ValidationError("Invalid path")
        
        response = client.post('/admin/db/export', data={
            'output_path': '/invalid/path'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show error message
