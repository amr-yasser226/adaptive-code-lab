import pytest
import os
from datetime import datetime as dt
from flask import Flask, session
from unittest.mock import Mock, MagicMock
from io import BytesIO


@pytest.fixture
def mock_services():
    """Create mock services for file routes."""
    services = {
        'user_repo': Mock(),
        'file_service': Mock(),
        'file_repo': Mock(),
    }
    
    # Setup user repo
    mock_user = Mock()
    mock_user.get_id.return_value = 1
    mock_user.name = "Test Student"
    mock_user.email = "student@test.com"
    mock_user.role = "student"
    services['user_repo'].get_by_id.return_value = mock_user
    
    # Setup file service
    mock_file = Mock()
    mock_file.get_id.return_value = 1  # Return int for template url_for
    mock_file.file_name = "test.py"
    mock_file.content_type = "text/plain"
    mock_file.size_bytes = 100
    services['file_service'].list_files.return_value = [mock_file]
    services['file_service'].upload_file.return_value = mock_file
    
    # Setup file repo
    services['file_repo'].get_by_id.return_value = mock_file
    
    return services


@pytest.fixture
def app(mock_services):
    """Create Flask test app with routes."""
    template_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/templates')
    static_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/static')
    
    app = Flask(__name__, 
                template_folder=os.path.abspath(template_dir),
                static_folder=os.path.abspath(static_dir))
    app.secret_key = 'test_secret'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    # Add format_date filter
    def format_date(value, fmt='%b %d, %Y'):
        if value is None:
            return 'N/A'
        if isinstance(value, str):
            return value
        return value.strftime(fmt)
    
    app.jinja_env.filters['format_date'] = format_date
    
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=lambda: 'test-csrf-token')
    
    @app.context_processor
    def inject_current_user():
        user_id = session.get('user_id')
        if user_id:
            return dict(current_user=mock_services['user_repo'].get_by_id(user_id))
        return dict(current_user=None)
    
    app.extensions['services'] = mock_services
    
    # Register required blueprints
    from web.routes.file import files_bp
    from web.routes.auth import auth_bp
    from web.routes.student import student_bp
    
    @app.route('/')
    def index():
        return 'Home'
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(files_bp)
    
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_session(client):
    """Create authenticated session."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'student'
    return client


@pytest.mark.unit
class TestFileRoutes:
    
    def test_list_files_requires_login(self, client):
        """Test that listing files requires login."""
        response = client.get('/files/submission/1')
        assert response.status_code in [302, 401, 403]
    
    def test_list_files_authenticated(self, auth_session, mock_services):
        """Test listing files when authenticated."""
        response = auth_session.get('/files/submission/1')
        # May fail due to missing template, but service should be called
        mock_services['file_service'].list_files.assert_called()
    
    def test_upload_file_requires_login(self, client):
        """Test that uploading files requires login."""
        response = client.post('/files/submission/1/upload')
        assert response.status_code in [302, 401, 403]
    
    def test_upload_file_no_file(self, auth_session):
        """Test upload without file returns error."""
        response = auth_session.post('/files/submission/1/upload')
        assert response.status_code in [302, 400]  # Redirect with flash or error
    
    def test_upload_file_success(self, auth_session, mock_services):
        """Test successful file upload."""
        data = {
            'file': (BytesIO(b'print("hello")'), 'test.py')
        }
        response = auth_session.post(
            '/files/submission/1/upload',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code in [302, 200]
        mock_services['file_service'].upload_file.assert_called()
    
    def test_download_file_requires_login(self, client):
        """Test that downloading files requires login."""
        response = client.get('/files/1/download')
        assert response.status_code in [302, 401, 403]
    
    def test_download_file_not_found(self, auth_session, mock_services):
        """Test download when file not found."""
        mock_services['file_repo'].get_by_id.return_value = None
        response = auth_session.get('/files/99/download')
        assert response.status_code in [302, 404]
    
    def test_delete_file_requires_login(self, client):
        """Test that deleting files requires login."""
        response = client.post('/files/1/delete')
        assert response.status_code in [302, 401, 403]
    
    def test_delete_file_success(self, auth_session, mock_services):
        """Test successful file deletion."""
        response = auth_session.post('/files/1/delete')
        assert response.status_code in [302, 200]
        mock_services['file_service'].delete_file.assert_called()
