import pytest
import os
import sqlite3
import json
from unittest.mock import Mock, patch
from flask import Flask, session, Blueprint
from core.entities.user import User

@pytest.fixture
def mock_services():
    ms = {
        'remediation_service': Mock(),
        'user_repo': Mock(),
    }
    ms['remediation_service'].get_student_remediations.return_value = []
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
    
    from web.routes.remediation import remediation_bp
    app.register_blueprint(remediation_bp)
    
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
def student_session(client, mock_services):
    mock_user = User(1, "Student", "s@t.com", "p", "student")
    mock_services['user_repo'].get_by_id.return_value = mock_user
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'student'
    return mock_user

class TestRemediationRoutes:
    def test_list_remediations_success(self, client, student_session, mock_services):
        mock_services['remediation_service'].get_student_remediations.return_value = []
        response = client.get('/remediations', follow_redirects=True)
        assert response.status_code == 200
        assert b'remediations' in response.data or b'Remediations' in response.data

    def test_list_remediations_error(self, client, student_session, mock_services):
        mock_services['remediation_service'].get_student_remediations.side_effect = sqlite3.Error("DB fail")
        response = client.get('/remediations', follow_redirects=True)
        assert b'DB fail' in response.data

    def test_view_remediation_success(self, client, student_session, mock_services):
        rem = {
            'id': 1, 
            'is_completed': False, 
            'is_viewed': False,
            'remediation': {
                'resource_title': 'Rem 1',
                'resource_type': 'video',
                'difficulty_level': 'beginner',
                'failure_pattern': 'syntax_error',
                'resource_content': 'Content',
                'resource_url': 'http://link',
                'language': 'python'
            },
            'recommended_at': None,
            'viewed_at': None,
            'completed_at': None
        }
        mock_services['remediation_service'].get_student_remediations.return_value = [rem]
        response = client.get('/remediations/1')
        assert response.status_code == 200
        assert b'Rem 1' in response.data

    def test_view_remediation_not_found(self, client, student_session, mock_services):
        mock_services['remediation_service'].get_student_remediations.return_value = []
        response = client.get('/remediations/1', follow_redirects=True)
        assert b'Remediation not found' in response.data

    def test_view_remediation_mark_viewed_error(self, client, student_session, mock_services):
        mock_services['remediation_service'].mark_viewed.side_effect = Exception("error")
        response = client.get('/remediations/1', follow_redirects=True)
        assert b'error' in response.data

    def test_complete_remediation_success(self, client, student_session, mock_services):
        response = client.post('/remediations/1/complete', follow_redirects=True)
        assert b'Remediation marked as completed' in response.data
        mock_services['remediation_service'].mark_completed.assert_called_with(1, 1)

    def test_complete_remediation_error(self, client, student_session, mock_services):
        mock_services['remediation_service'].mark_completed.side_effect = Exception("fail")
        response = client.post('/remediations/1/complete', follow_redirects=True)
        assert b'fail' in response.data

    def test_api_list_remediations_success(self, client, student_session, mock_services):
        mock_services['remediation_service'].get_student_remediations.return_value = [{'id': 1}]
        response = client.get('/api/remediations')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['remediations']) == 1

    def test_api_list_remediations_error(self, client, student_session, mock_services):
        mock_services['remediation_service'].get_student_remediations.side_effect = Exception("err")
        response = client.get('/api/remediations')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False

    def test_api_mark_viewed_success(self, client, student_session, mock_services):
        response = client.post('/api/remediations/1/view')
        assert response.status_code == 200
        assert json.loads(response.data)['success'] is True

    def test_api_mark_viewed_error(self, client, student_session, mock_services):
        mock_services['remediation_service'].mark_viewed.side_effect = sqlite3.Error("DB error")
        response = client.post('/api/remediations/1/view')
        assert response.status_code == 400
        assert json.loads(response.data)['success'] is False

    def test_api_mark_completed_success(self, client, student_session, mock_services):
        response = client.post('/api/remediations/1/complete')
        assert response.status_code == 200
        assert json.loads(response.data)['success'] is True

    def test_api_mark_completed_error(self, client, student_session, mock_services):
        mock_services['remediation_service'].mark_completed.side_effect = Exception("failed")
        response = client.post('/api/remediations/1/complete')
        assert response.status_code == 400
        assert json.loads(response.data)['success'] is False
