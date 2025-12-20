import pytest
import os
import io
from unittest.mock import Mock, patch
from flask import Flask, session, Blueprint
from core.entities.user import User
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError

@pytest.fixture
def mock_services():
    return {
        'file_service': Mock(),
        'file_repo': Mock(),
        'user_repo': Mock(),
    }

@pytest.fixture
def app(mock_services):
    template_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/templates')
    static_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/static')
    
    app = Flask(__name__, 
                template_folder=os.path.abspath(template_dir),
                static_folder=os.path.abspath(static_dir))
    app.secret_key = 'test_secret'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    @app.context_processor
    def inject_csrf_token():
        return {'csrf_token': lambda: ''}
    
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
    
    from web.routes.file import files_bp
    app.register_blueprint(files_bp)
    
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

class TestFileRoutes:
    def test_list_files_success(self, client, user_session, mock_services):
        mock_services['file_service'].list_files.return_value = []
        response = client.get('/files/submission/1')
        assert response.status_code == 200
        assert b'Files' in response.data or b'No files found' in response.data

    def test_list_files_error(self, client, user_session, mock_services):
        mock_services['file_service'].list_files.side_effect = AuthError("Denied")
        response = client.get('/files/submission/1', follow_redirects=True)
        assert b'Denied' in response.data

    def test_list_files_db_error(self, client, user_session, mock_services):
        import sqlite3
        mock_services['file_service'].list_files.side_effect = sqlite3.Error("DB error")
        response = client.get('/files/submission/1', follow_redirects=True)
        assert b'DB error' in response.data

    def test_upload_file_success(self, client, user_session, mock_services):
        data = {
            'file': (io.BytesIO(b"hello world"), 'test.txt')
        }
        response = client.post('/files/submission/1/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert b'File uploaded successfully' in response.data
        mock_services['file_service'].upload_file.assert_called()

    def test_upload_file_no_file(self, client, user_session, mock_services):
        response = client.post('/files/submission/1/upload', data={}, follow_redirects=True)
        assert b'No file provided' in response.data

    def test_upload_file_error(self, client, user_session, mock_services):
        mock_services['file_service'].upload_file.side_effect = ValidationError("Too big")
        data = {'file': (io.BytesIO(b"X"), 'test.txt')}
        response = client.post('/files/submission/1/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert b'Too big' in response.data

    def test_upload_file_db_error(self, client, user_session, mock_services):
        import sqlite3
        mock_services['file_service'].upload_file.side_effect = sqlite3.Error("DB error")
        data = {'file': (io.BytesIO(b"X"), 'test.txt')}
        response = client.post('/files/submission/1/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert b'DB error' in response.data

    def test_download_file_success_url(self, client, user_session, mock_services):
        mock_file = Mock()
        mock_file.storage_url = "http://example.com/file"
        mock_services['file_repo'].get_by_id.return_value = mock_file
        
        response = client.get('/files/1/download')
        assert response.status_code == 302
        assert response.location == "http://example.com/file"

    @patch('web.routes.file.os.path.isabs')
    @patch('web.routes.file.os.path.exists')
    @patch('web.routes.file.send_file')
    def test_download_file_success_local_abs(self, mock_send_file, mock_exists, mock_isabs, client, user_session, mock_services):
        mock_isabs.return_value = True
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.storage_url = None
        mock_file.path = "/abs/path/test.txt"
        mock_file.content_type = "text/plain"
        mock_file.file_name = "test.txt"
        mock_services['file_repo'].get_by_id.return_value = mock_file
        
        from flask import Response
        mock_send_file.return_value = Response("file content", 200)
        
        response = client.get('/files/1/download', follow_redirects=True)
        assert b'file content' in response.data
        assert response.status_code == 200
        mock_send_file.assert_called()

    def test_download_file_not_found(self, client, user_session, mock_services):
        mock_services['file_repo'].get_by_id.return_value = None
        response = client.get('/files/1/download', follow_redirects=True)
        assert b'File not found' in response.data

    def test_download_file_error(self, client, user_session, mock_services):
        import sqlite3
        mock_services['file_repo'].get_by_id.side_effect = sqlite3.Error("DB Fail")
        response = client.get('/files/1/download', follow_redirects=True)
        assert b'DB Fail' in response.data

    @patch('web.routes.file.os.path.isabs')
    @patch('web.routes.file.os.path.exists')
    @patch('web.routes.file.send_file')
    def test_download_file_success_local_candidate(self, mock_send_file, mock_exists, mock_isabs, client, user_session, mock_services):
        # Mock isabs to return False for relative path
        mock_isabs.return_value = False
        mock_exists.return_value = True
        mock_file = Mock()
        mock_file.storage_url = None
        mock_file.path = "relative/path/test.txt"
        mock_file.content_type = "text/plain"
        mock_file.file_name = "test.txt"
        mock_services['file_repo'].get_by_id.return_value = mock_file
        
        from flask import Response
        mock_send_file.return_value = Response("file content", 200)
        
        response = client.get('/files/1/download', follow_redirects=True)
        assert b'file content' in response.data
        assert response.status_code == 200

    @patch('web.routes.file.os.path.exists')
    def test_download_file_not_available(self, mock_exists, client, user_session, mock_services):
        mock_exists.return_value = False
        mock_file = Mock()
        mock_file.storage_url = None
        mock_file.path = "relative/path/test.txt"
        mock_services['file_repo'].get_by_id.return_value = mock_file
        
        response = client.get('/files/1/download', follow_redirects=True)
        assert b'File is not available for download' in response.data

    @patch('web.routes.file.hashlib.sha256')
    def test_upload_file_read_error(self, mock_sha, client, user_session, mock_services):
        mock_sha.side_effect = Exception("Read error")
        data = {'file': (io.BytesIO(b"abc"), 'test.txt')}
        response = client.post('/files/submission/1/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert b'Failed to read uploaded file' in response.data

    def test_delete_file_success(self, client, user_session, mock_services):
        response = client.post('/files/1/delete', follow_redirects=True)
        assert b'File deleted successfully' in response.data
        mock_services['file_service'].delete_file.assert_called_with(user=user_session, file_id=1)

    def test_delete_file_error(self, client, user_session, mock_services):
        mock_services['file_service'].delete_file.side_effect = ValidationError("Cant delete")
        response = client.post('/files/1/delete', follow_redirects=True)
        assert b'Cant delete' in response.data

    def test_delete_file_db_error(self, client, user_session, mock_services):
        import sqlite3
        mock_services['file_service'].delete_file.side_effect = sqlite3.Error("DB error")
        response = client.post('/files/1/delete', follow_redirects=True)
        assert b'DB error' in response.data
