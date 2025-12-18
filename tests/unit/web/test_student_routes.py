import pytest
import os
from datetime import datetime as dt
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, session
from core.entities.user import User
from core.entities.student import Student
from core.entities.assignment import Assignment
from core.entities.submission import Submission


@pytest.fixture
def mock_services():
    """Create mock services that will be injected into the app."""
    mock_user_repo = Mock()
    mock_student_service = Mock()
    mock_assignment_repo = Mock()
    mock_submission_repo = Mock()
    mock_result_repo = Mock()
    mock_auth_service = Mock()
    
    return {
        'user_repo': mock_user_repo,
        'student_service': mock_student_service,
        'assignment_repo': mock_assignment_repo,
        'submission_repo': mock_submission_repo,
        'result_repo': mock_result_repo,
        'auth_service': mock_auth_service,
    }


@pytest.fixture
def app(mock_services):
    """Create a minimal app with the blueprint, templates, and mocked services."""
    template_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/templates')
    static_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/static')
    
    app = Flask(__name__, 
                template_folder=os.path.abspath(template_dir),
                static_folder=os.path.abspath(static_dir))
    app.secret_key = 'test_secret'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['TESTING'] = True
    
    # Add csrf_token to template context (templates expect it)
    @app.context_processor
    def inject_csrf_token():
        return {'csrf_token': lambda: ''}
    
    # Register the format_date filter (same as in app.py)
    def format_date(value, fmt='%b %d, %Y'):
        """Safely format a date value (string or datetime) to a string."""
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
    
    # Inject mocked services into app extensions (this is how get_service retrieves them)
    app.extensions['services'] = mock_services
    
    # Add stub index route (templates reference url_for('index'))
    @app.route('/')
    def index():
        return 'Home'
    
    # Register blueprints needed by templates
    from web.routes.student import student_bp
    from web.routes.auth import auth_bp
    from web.routes.instructor import instructor_bp
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_session(client):
    """Set up an authenticated session."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'student'
        sess['logged_in'] = True


@pytest.mark.unit
class TestStudentRoutes:

    def test_dashboard_access(self, client, mock_services, auth_session):
        """Test that dashboard renders correctly for authenticated student."""
        # Setup mock data
        mock_services['user_repo'].get_by_id.return_value = User(
            1, "Test Student", "test@test.com", "pwd", "student"
        )
        mock_services['student_service'].get_student_submissions.return_value = []
        mock_services['assignment_repo'].get_all.return_value = []

        response = client.get('/student/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Assignment' in response.data

    def test_assignments_view(self, client, mock_services, auth_session):
        """Test that assignments page renders with mock data."""
        # Corrected Assignment init with all required fields
        mock_assignment = Assignment(
            1, 101, "A1", "Description", None, None, 100, True, True, 0, None, None
        )
        mock_services['assignment_repo'].get_all.return_value = [mock_assignment]
        mock_services['student_service'].get_student_submissions.return_value = []

        response = client.get('/student/assignments')
        assert response.status_code == 200
        assert b'A1' in response.data

    def test_submit_assignment_post(self, client, mock_services, auth_session):
        """Test submitting code for an assignment."""
        assignment = Assignment(
            1, 101, "A1", "Description", None, None, 100, True, True, 0, None, None
        )
        mock_services['assignment_repo'].get_by_id.return_value = assignment
        mock_services['student_service'].submit_assignment.return_value = Mock()
        
        # Setup mocks for dashboard redirect
        mock_services['user_repo'].get_by_id.return_value = User(
            1, "Test Student", "test@test.com", "pwd", "student"
        )
        mock_services['student_service'].get_student_submissions.return_value = []
        mock_services['assignment_repo'].get_all.return_value = []

        response = client.post(
            '/student/submit/1', 
            data={'code': 'print("hello")'}, 
            follow_redirects=True
        )
        
        assert response.status_code == 200
        mock_services['student_service'].submit_assignment.assert_called_with(1, '1', 'print("hello")')
        assert b'Code submitted successfully' in response.data

    def test_profile_view(self, client, mock_services, auth_session):
        """Test that profile page renders correctly."""
        mock_student = Student(
            1, "Student Name", "s@test.com", "pwd", None, None, "S123", "CS", 1
        )
        mock_services['student_service'].get_student.return_value = mock_student
        mock_services['student_service'].get_student_submissions.return_value = []

        response = client.get('/student/profile')
        assert response.status_code == 200
        assert b'Student Name' in response.data
        # Verify stub form rendering
        assert b'type="password"' in response.data

    def test_unauthenticated_access_redirects(self, client, mock_services):
        """Test that unauthenticated users are redirected to login."""
        response = client.get('/student/dashboard')
        assert response.status_code == 302  # Redirect
        assert '/login' in response.location or 'auth' in response.location.lower()
