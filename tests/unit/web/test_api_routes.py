import pytest
import os
from flask import Flask, session
from unittest.mock import Mock, patch


@pytest.fixture
def mock_services():
    """Create mock services."""
    services = {
        'user_repo': Mock(),
        'assignment_repo': Mock(),
        'test_case_service': Mock(),
        'sandbox_service': Mock(),
    }
    
    mock_user = Mock()
    mock_user.get_id.return_value = 1
    mock_user.name = "Test User"
    mock_user.role = "student"
    services['user_repo'].get_by_id.return_value = mock_user
    
    mock_assignment = Mock()
    mock_assignment.get_id.return_value = 1
    mock_assignment.title = "Test Assignment"
    services['assignment_repo'].get_by_id.return_value = mock_assignment
    
    services['test_case_service'].list_test_cases.return_value = []
    
    services['sandbox_service'].execute_code.return_value = {
        'success': True,
        'stdout': 'Hello',
        'stderr': '',
        'exit_code': 0,
        'runtime_ms': 100,
        'timed_out': False
    }
    services['sandbox_service'].groq_client = None
    
    return services


@pytest.fixture
def app(mock_services):
    """Create Flask test app."""
    app = Flask(__name__)
    app.secret_key = 'test_secret'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    app.extensions['services'] = mock_services
    
    from web.routes.api import api_bp
    from web.routes.auth import auth_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp)
    
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
class TestAPIRoutes:
    
    def test_get_languages_public(self, client):
        """Test languages endpoint is public."""
        response = client.get('/api/languages')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'languages' in data
        assert len(data['languages']) == 5
    
    def test_test_code_requires_login(self, client):
        """Test code execution requires login."""
        response = client.post('/api/test-code', json={
            'code': 'print("hello")',
            'language': 'python'
        })
        assert response.status_code in [302, 401]
    
    def test_test_code_authenticated(self, auth_session, mock_services):
        """Test code execution when authenticated."""
        response = auth_session.post('/api/test-code', 
            json={
                'code': 'print("hello")',
                'language': 'python',
                'assignment_id': 1
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        mock_services['sandbox_service'].execute_code.assert_called()
    
    def test_get_hint_requires_login(self, client):
        """Test hint endpoint requires login."""
        response = client.post('/api/hint', json={
            'code': 'prnt("hello")',
            'error': 'NameError'
        })
        assert response.status_code in [302, 401]
    
    def test_get_test_cases_requires_login(self, client):
        """Test getting test cases requires login."""
        response = client.get('/api/assignment/1/test-cases')
        assert response.status_code in [302, 401]
    
    def test_get_test_cases_authenticated(self, auth_session, mock_services):
        """Test getting test cases when authenticated."""
        response = auth_session.get('/api/assignment/1/test-cases')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'test_cases' in data
