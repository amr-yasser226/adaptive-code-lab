import pytest
import os
from unittest.mock import Mock, MagicMock
from flask import Flask, session, Blueprint
from core.entities.user import User
from core.entities.assignment import Assignment
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError

@pytest.fixture
def mock_services():
    return {
        'assignment_service': Mock(),
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
    
    from web.routes.assignment import assignment_bp
    app.register_blueprint(assignment_bp)
    
    # Instructor Blueprint
    instructor_bp = Blueprint('instructor', __name__)
    @instructor_bp.route('/dashboard')
    def dashboard():
        from flask import get_flashed_messages
        return f"Dashboard {' '.join(get_flashed_messages())}"
    @instructor_bp.route('/analytics')
    def analytics(): return 'Analytics'
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    
    # Student Blueprint
    student_bp = Blueprint('student', __name__)
    @student_bp.route('/dashboard')
    def sdash(): return 'Student Dash'
    @student_bp.route('/assignments')
    def sass(): return 'Student Ass'
    @student_bp.route('/profile')
    def profile(): return 'Profile'
    @student_bp.route('/submissions/<int:submission_id>')
    def submission_results(submission_id): return f'Submission {submission_id}'
    app.register_blueprint(student_bp, url_prefix='/student')
    
    # Auth Blueprint
    auth_bp = Blueprint('auth', __name__)
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
def instructor_session(client, mock_services):
    mock_user = User(1, "Inst", "i@t.com", "p", "instructor")
    mock_services['user_repo'].get_by_id.return_value = mock_user
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'instructor'
        sess['logged_in'] = True
    return mock_user

class TestAssignmentRoutes:
    def test_create_assignment_get(self, client, instructor_session):
        response = client.get('/assignments/create')
        assert response.status_code == 200
        assert b'Create New Assignment' in response.data

    def test_create_assignment_post_success(self, client, instructor_session, mock_services):
        data = {
            'course_id': '101',
            'title': 'New Ass',
            'description': 'Desc',
            'release_date': '2023-01-01',
            'due_date': '2023-01-10',
            'max_points': '100',
            'allow_late': 'true',
            'late_penalty': '10',
            'is_published': 'true'
        }
        response = client.post('/assignments/create', data=data, follow_redirects=True)
        assert b'Assignment created successfully' in response.data
        mock_services['assignment_service'].create_assignment.assert_called()

    def test_create_assignment_validation_error(self, client, instructor_session, mock_services):
        mock_services['assignment_service'].create_assignment.side_effect = ValidationError("Invalid")
        response = client.post('/assignments/create', data={'title': 'X'}, follow_redirects=True)
        assert b'Invalid' in response.data

    def test_create_assignment_auth_error(self, client, instructor_session, mock_services):
        mock_services['assignment_service'].create_assignment.side_effect = AuthError("Unauthorized")
        response = client.post('/assignments/create', data={'title': 'X'}, follow_redirects=True)
        assert b'Unauthorized' in response.data

    def test_publish_assignment_success(self, client, instructor_session, mock_services):
        response = client.post('/assignments/1/publish', follow_redirects=True)
        assert b'Assignment published' in response.data
        mock_services['assignment_service'].publish_assignment.assert_called_with(
            instructor=instructor_session,
            assignment_id=1
        )

    def test_publish_assignment_error(self, client, instructor_session, mock_services):
        mock_services['assignment_service'].publish_assignment.side_effect = AuthError("Not yours")
        response = client.post('/assignments/1/publish', follow_redirects=True)
        assert b'Not yours' in response.data

    def test_unpublish_assignment_success(self, client, instructor_session, mock_services):
        response = client.post('/assignments/1/unpublish', follow_redirects=True)
        assert b'Assignment unpublished' in response.data

    def test_unpublish_assignment_error(self, client, instructor_session, mock_services):
        mock_services['assignment_service'].unpublish_assignment.side_effect = ValidationError("Err")
        response = client.post('/assignments/1/unpublish', follow_redirects=True)
        assert b'Err' in response.data

    def test_extend_deadline_success(self, client, instructor_session, mock_services):
        response = client.post('/assignments/1/extend', data={'new_due_date': '2023-12-31'}, follow_redirects=True)
        assert b'Deadline extended' in response.data

    def test_extend_deadline_error(self, client, instructor_session, mock_services):
        mock_services['assignment_service'].extend_deadline.side_effect = ValidationError("Date error")
        response = client.post('/assignments/1/extend', data={'new_due_date': 'past'}, follow_redirects=True)
        assert b'Date error' in response.data

    def test_list_assignments_success(self, client, instructor_session, mock_services):
        mock_services['assignment_service'].list_assignments_for_course.return_value = []
        response = client.get('/assignments/course/101')
        assert response.status_code == 200
        assert b'Assignments' in response.data

    def test_list_assignments_error(self, client, instructor_session, mock_services):
        mock_services['assignment_service'].list_assignments_for_course.side_effect = ValidationError("No coarse")
        response = client.get('/assignments/course/101', follow_redirects=True)
        assert b'No coarse' in response.data

    def test_view_submissions_success(self, client, instructor_session, mock_services):
        mock_sub = Mock()
        mock_sub.get_id.return_value = 1
        mock_sub.version = 1
        mock_sub.status = 'graded'
        mock_sub.score = 90
        mock_sub.submitted_at = None
        mock_sub.student_id = 1
        mock_services['assignment_service'].get_submissions.return_value = [mock_sub]
        response = client.get('/assignments/1/submissions')
        assert response.status_code == 200
        assert b'Submissions' in response.data

    def test_view_submissions_error(self, client, instructor_session, mock_services):
        mock_services['assignment_service'].get_submissions.side_effect = AuthError("Denied")
        response = client.get('/assignments/1/submissions', follow_redirects=True)
        assert b'Denied' in response.data

    def test_assignment_statistics_success(self, client, instructor_session, mock_services):
        mock_services['assignment_service'].calculate_statistics.return_value = {
            'count': 10, 'average': 80, 'min': 50, 'max': 100
        }
        response = client.get('/assignments/1/stats')
        assert response.status_code == 200
        assert b'Statistics' in response.data

    def test_assignment_statistics_error(self, client, instructor_session, mock_services):
        mock_services['assignment_service'].calculate_statistics.side_effect = ValidationError("No stats")
        response = client.get('/assignments/1/stats', follow_redirects=True)
        assert b'No stats' in response.data
