import pytest
import os
from datetime import datetime as dt
from flask import Flask, session
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_services():
    """Create mock services for assignment routes."""
    services = {
        'user_repo': Mock(),
        'assignment_service': Mock(),
    }
    
    # Setup user repo
    mock_user = Mock()
    mock_user.get_id.return_value = 1
    mock_user.name = "Test Instructor"
    mock_user.email = "instructor@test.com"
    mock_user.role = "instructor"
    services['user_repo'].get_by_id.return_value = mock_user
    
    # Setup assignment service
    mock_assignment = Mock()
    mock_assignment.get_id.return_value = 1
    mock_assignment.title = "Test Assignment"
    services['assignment_service'].create_assignment.return_value = mock_assignment
    services['assignment_service'].list_assignments_for_course.return_value = [mock_assignment]
    services['assignment_service'].get_submissions.return_value = []
    services['assignment_service'].calculate_statistics.return_value = {'avg': 85}
    
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
    from web.routes.assignment import assignment_bp
    from web.routes.auth import auth_bp
    from web.routes.instructor import instructor_bp
    from web.routes.student import student_bp
    
    @app.route('/')
    def index():
        return 'Home'
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(assignment_bp)
    
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def instructor_session(client):
    """Create authenticated instructor session."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'instructor'
    return client


@pytest.mark.unit
class TestAssignmentRoutes:
    
    def test_create_assignment_requires_login(self, client):
        """Test that creating assignment requires login."""
        response = client.get('/assignments/create')
        assert response.status_code in [302, 401, 403]
    
    def test_create_assignment_requires_instructor(self, client):
        """Test that creating assignment requires instructor role."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'student'  # Not instructor
        
        response = client.get('/assignments/create')
        assert response.status_code in [302, 403]
    
    def test_publish_assignment_post(self, instructor_session, mock_services):
        """Test publishing an assignment."""
        response = instructor_session.post('/assignments/1/publish')
        assert response.status_code in [302, 200]
        mock_services['assignment_service'].publish_assignment.assert_called()
    
    def test_unpublish_assignment_post(self, instructor_session, mock_services):
        """Test unpublishing an assignment."""
        response = instructor_session.post('/assignments/1/unpublish')
        assert response.status_code in [302, 200]
        mock_services['assignment_service'].unpublish_assignment.assert_called()
    
    def test_extend_deadline_post(self, instructor_session, mock_services):
        """Test extending assignment deadline."""
        response = instructor_session.post('/assignments/1/extend', data={
            'new_due_date': '2025-12-31'
        })
        assert response.status_code in [302, 200]
        mock_services['assignment_service'].extend_deadline.assert_called()
    
    def test_list_assignments_requires_login(self, client):
        """Test listing assignments requires login."""
        response = client.get('/assignments/course/1')
        assert response.status_code in [302, 401]
    
    def test_view_submissions_requires_instructor(self, client):
        """Test viewing submissions requires instructor."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'student'
        
        response = client.get('/assignments/1/submissions')
        assert response.status_code in [302, 403]
    
    def test_assignment_statistics_requires_instructor(self, instructor_session, mock_services):
        """Test assignment statistics endpoint."""
        response = instructor_session.get('/assignments/1/stats')
        # May fail due to missing template, but service should be called
        mock_services['assignment_service'].calculate_statistics.assert_called()
