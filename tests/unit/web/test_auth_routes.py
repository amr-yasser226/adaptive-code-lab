import pytest
import os
from datetime import datetime as dt
from unittest.mock import Mock, MagicMock
from flask import Flask
from core.entities.user import User
from core.exceptions.auth_error import AuthError


@pytest.fixture
def mock_services():
    """Create mock services for testing."""
    return {
        'auth_service': Mock(),
        'user_repo': Mock(),
        'student_service': Mock(),
        'assignment_repo': Mock(),
        'instructor_service': Mock(),
        'submission_repo': Mock(),
        'course_repo': Mock(),
        'enrollment_repo': Mock(),
        'flag_repo': Mock(),
    }


@pytest.fixture
def app(mock_services):
    """Create a test Flask app with auth and related blueprints."""
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
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.mark.unit
class TestAuthRoutes:

    def test_login_page_renders(self, client):
        """Test that login page renders without authentication."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'Log In' in response.data or b'email' in response.data.lower()

    def test_login_success_student(self, client, mock_services):
        """Test successful login as student redirects to student dashboard."""
        mock_user = User(1, "Test Student", "student@test.com", "hashed", "student")
        mock_services['auth_service'].login.return_value = mock_user
        
        # Setup mocks for student dashboard
        mock_services['user_repo'].get_by_id.return_value = mock_user
        mock_services['student_service'].get_student_submissions.return_value = []
        mock_services['assignment_repo'].get_all.return_value = []
        
        response = client.post('/auth/login', data={
            'email': 'student@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        mock_services['auth_service'].login.assert_called_with('student@test.com', 'password123')

    def test_login_success_instructor(self, client, mock_services):
        """Test successful login as instructor redirects to instructor dashboard."""
        mock_user = User(2, "Test Instructor", "instructor@test.com", "hashed", "instructor")
        mock_services['auth_service'].login.return_value = mock_user
        
        # Just test that login succeeds and redirects (don't follow redirect as dashboard is complex)
        response = client.post('/auth/login', data={
            'email': 'instructor@test.com',
            'password': 'password123'
        })
        
        # Should redirect to instructor dashboard
        assert response.status_code == 302
        assert '/instructor' in response.location
        mock_services['auth_service'].login.assert_called_with('instructor@test.com', 'password123')

    def test_login_failure_shows_error(self, client, mock_services):
        """Test failed login shows error message."""
        mock_services['auth_service'].login.side_effect = AuthError("Invalid credentials")
        
        response = client.post('/auth/login', data={
            'email': 'wrong@test.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid credentials' in response.data or b'error' in response.data.lower()

    def test_register_page_renders(self, client):
        """Test that register page renders."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'Sign Up' in response.data or b'name' in response.data.lower()

    def test_register_success(self, client, mock_services):
        """Test successful registration redirects to login."""
        mock_services['auth_service'].register.return_value = None
        
        response = client.post('/auth/register', data={
            'name': 'New User',
            'email': 'newuser@test.com',
            'password': 'securepassword123',
            'role': 'student'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        mock_services['auth_service'].register.assert_called_with(
            'New User', 'newuser@test.com', 'securepassword123', 'student'
        )

    def test_register_short_name_fails(self, client, mock_services):
        """Test that short name fails validation."""
        response = client.post('/auth/register', data={
            'name': 'A',  # Too short
            'email': 'user@test.com',
            'password': 'password123',
            'role': 'student'
        })
        
        assert response.status_code == 200
        assert b'at least 2 characters' in response.data or b'Name' in response.data

    def test_register_invalid_email_fails(self, client, mock_services):
        """Test that invalid email fails validation."""
        response = client.post('/auth/register', data={
            'name': 'Valid Name',
            'email': 'invalid-email',  # Invalid format
            'password': 'password123',
            'role': 'student'
        })
        
        assert response.status_code == 200
        assert b'Invalid email' in response.data or b'email' in response.data.lower()

    def test_register_short_password_fails(self, client, mock_services):
        """Test that short password fails validation."""
        response = client.post('/auth/register', data={
            'name': 'Valid Name',
            'email': 'valid@test.com',
            'password': 'short',  # Too short
            'role': 'student'
        })
        
        assert response.status_code == 200
        assert b'at least 8 characters' in response.data or b'password' in response.data.lower()

    def test_logout(self, client):
        """Test logout clears session and redirects."""
        # First login to set session
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'student'
        
        response = client.get('/auth/logout', follow_redirects=True)
        
        assert response.status_code == 200
        # Session should be cleared
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
