import pytest
import os
from datetime import datetime as dt
from flask import Flask, session
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_services():
    """Create mock services for remediation routes."""
    services = {
        'user_repo': Mock(),
        'remediation_service': Mock(),
    }
    
    # Setup user repo
    mock_user = Mock()
    mock_user.get_id.return_value = 1
    mock_user.name = "Test Student"
    mock_user.email = "student@test.com"
    mock_user.role = "student"
    services['user_repo'].get_by_id.return_value = mock_user
    
    # Setup remediation service
    services['remediation_service'].get_student_remediations.return_value = [
        {
            'id': 1,
            'remediation': {
                'id': 1,
                'failure_pattern': 'syntax_error',
                'resource_title': 'Python Syntax Basics',
                'resource_type': 'article',
                'resource_url': 'https://docs.python.org',
                'resource_content': 'Learn Python syntax',
                'difficulty_level': 'beginner',
                'language': 'python'
            },
            'submission_id': 100,
            'is_viewed': False,
            'is_completed': False,
            'recommended_at': '2024-01-15',
            'viewed_at': None,
            'completed_at': None
        }
    ]
    
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
    
    # Add CSRF token context processor
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=lambda: 'test-csrf-token')
    
    # Add current_user context processor
    @app.context_processor
    def inject_current_user():
        user_id = session.get('user_id')
        if user_id:
            return dict(current_user=mock_services['user_repo'].get_by_id(user_id))
        return dict(current_user=None)
    
    app.extensions['services'] = mock_services
    
    # Register required blueprints
    from web.routes.remediation import remediation_bp
    from web.routes.student import student_bp
    from web.routes.auth import auth_bp
    
    @app.route('/')
    def index():
        return 'Home'
    
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(remediation_bp, url_prefix='/student')
    
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
class TestRemediationRoutes:
    
    def test_list_remediations_requires_login(self, client):
        """Test that listing remediations requires login."""
        response = client.get('/student/remediations')
        assert response.status_code in [302, 401, 403]
    
    def test_list_remediations_success(self, auth_session, mock_services):
        """Test listing remediations successfully."""
        response = auth_session.get('/student/remediations')
        
        # Should return 200 or render template
        assert response.status_code == 200
        mock_services['remediation_service'].get_student_remediations.assert_called()
    
    def test_list_remediations_pending_filter(self, auth_session, mock_services):
        """Test filtering by pending remediations."""
        response = auth_session.get('/student/remediations?pending=true')
        
        assert response.status_code == 200
        mock_services['remediation_service'].get_student_remediations.assert_called_with(1, True)
    
    def test_view_remediation_marks_as_viewed(self, auth_session, mock_services):
        """Test viewing a remediation marks it as viewed."""
        response = auth_session.get('/student/remediations/1')
        
        # Should call mark_viewed
        mock_services['remediation_service'].mark_viewed.assert_called_with(1, 1)
    
    def test_complete_remediation_success(self, auth_session, mock_services):
        """Test completing a remediation."""
        response = auth_session.post('/student/remediations/1/complete')
        
        # Should redirect after completion
        assert response.status_code in [302, 200]
        mock_services['remediation_service'].mark_completed.assert_called_with(1, 1)
    
    def test_api_list_remediations(self, auth_session, mock_services):
        """Test API endpoint for listing remediations."""
        response = auth_session.get('/student/api/remediations')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'remediations' in data
    
    def test_api_mark_viewed(self, auth_session, mock_services):
        """Test API endpoint for marking viewed."""
        response = auth_session.post('/student/api/remediations/1/view')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_api_mark_completed(self, auth_session, mock_services):
        """Test API endpoint for marking completed."""
        response = auth_session.post('/student/api/remediations/1/complete')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
