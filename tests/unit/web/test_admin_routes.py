import pytest
import os
import sqlite3
from unittest.mock import Mock, MagicMock, patch
from flask import Flask
from core.entities.user import User

@pytest.fixture
def mock_services():
    return {
        'admin_service': Mock(),
        'auth_service': Mock(),
        'user_repo': Mock(),
    }

@pytest.fixture
def app(mock_services):
    template_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/templates')
    app = Flask(__name__, template_folder=os.path.abspath(template_dir))
    app.secret_key = 'test'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    @app.context_processor
    def inject_csrf_token():
        return {'csrf_token': lambda: ''}
    
    @app.route('/')
    def index():
        return 'Home'
    
    @app.route('/auth/login')
    def login_mock():
        return 'Login Page'
    
    app.extensions['services'] = mock_services
    
    from web.routes.admin import admin_bp
    from web.routes.auth import auth_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_session(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'admin'
        sess['logged_in'] = True

@pytest.fixture
def mock_admin_user():
    return User(1, "Admin", "a@t.com", "p", "admin")

@pytest.mark.unit
class TestAdminRoutes:
    @patch('web.routes.admin.get_current_user')
    @patch('web.routes.admin.render_template')
    def test_dashboard_renders(self, mock_render, mock_get_current, client, admin_session, mock_admin_user):
        mock_get_current.return_value = mock_admin_user
        mock_render.return_value = "Dashboard Content"
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'Dashboard Content' in response.data

    @patch('web.routes.admin.get_current_user')
    def test_manage_user_account_success(self, mock_get_current, client, mock_services, admin_session, mock_admin_user):
        mock_get_current.return_value = mock_admin_user
        mock_services['admin_service'].manage_user_account.return_value = None
        response = client.post('/admin/users/2/manage', data={'action': 'suspend'}, follow_redirects=True)
        # If it redirected to index, status_code would be 200 with 'Home' data
        assert response.data != b'Home'
        assert b'updated successfully' in response.data
        mock_services['admin_service'].manage_user_account.assert_called()

    @patch('web.routes.admin.get_current_user')
    @patch('web.routes.admin.render_template')
    def test_generate_report_success(self, mock_render, mock_get_current, client, mock_services, admin_session, mock_admin_user):
        mock_get_current.return_value = mock_admin_user
        mock_render.return_value = "Report Content"
        mock_services['admin_service'].generate_report.return_value = {'data': 'test'}
        response = client.get('/admin/reports/users')
        assert response.status_code == 200
        assert b'Report Content' in response.data

    @patch('web.routes.admin.get_current_user')
    def test_configure_system_setting(self, mock_get_current, client, mock_services, admin_session, mock_admin_user):
        mock_get_current.return_value = mock_admin_user
        response = client.post('/admin/settings', data={'key': 'k', 'value': 'v'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'updated successfully' in response.data
        mock_services['admin_service'].configure_system_setting.assert_called()

    @patch('web.routes.admin.get_current_user')
    def test_export_db_dump(self, mock_get_current, client, mock_services, admin_session, mock_admin_user):
        mock_get_current.return_value = mock_admin_user
        response = client.post('/admin/db/export', data={'output_path': '/tmp/dump'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'exported successfully' in response.data
        mock_services['admin_service'].export_db_dump.assert_called()

    @patch('web.routes.admin.get_current_user')
    def test_admin_errors(self, mock_get_current, client, mock_services, admin_session, mock_admin_user):
        mock_get_current.return_value = mock_admin_user
        from core.exceptions.auth_error import AuthError
        from core.exceptions.validation_error import ValidationError
        
        # Manage user error
        mock_services['admin_service'].manage_user_account.side_effect = AuthError("Unauthorized")
        response = client.post('/admin/users/2/manage', data={'action': 'suspend'}, follow_redirects=True)
        assert b'Unauthorized' in response.data
        
        # Generate report error
        mock_services['admin_service'].generate_report.side_effect = ValidationError("Invalid type")
        response = client.get('/admin/reports/invalid', follow_redirects=True)
        assert b'Invalid type' in response.data
        
        # Settings error
        mock_services['admin_service'].configure_system_setting.side_effect = ValidationError("Bad key")
        response = client.post('/admin/settings', data={'key': 'k', 'value': 'v'}, follow_redirects=True)
        assert b'Bad key' in response.data
        
        # Export error
        mock_services['admin_service'].export_db_dump.side_effect = ValidationError("Bad path")
        response = client.post('/admin/db/export', data={'output_path': 'X'}, follow_redirects=True)
        assert b'Bad path' in response.data
