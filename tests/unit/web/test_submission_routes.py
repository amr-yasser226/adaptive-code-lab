import pytest
import os
from unittest.mock import Mock, MagicMock
from flask import Flask, session, Blueprint
from core.entities.user import User

@pytest.fixture
def mock_services():
    return {
        'submission_repo': Mock(),
        'result_repo': Mock(),
        'assignment_repo': Mock(),
        'sandbox_service': Mock(),
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
    
    from web.routes.submission import submission_bp
    app.register_blueprint(submission_bp)
    
    instructor_bp = Blueprint('instructor', __name__)
    @instructor_bp.route('/dashboard')
    def dashboard():
        from flask import get_flashed_messages
        return f"Dashboard {' '.join(get_flashed_messages())}"
    @instructor_bp.route('/analytics')
    def analytics(): return 'Analytics'
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    
    student_bp = Blueprint('student', __name__)
    @student_bp.route('/dashboard')
    def dashboard(): return 'Student Dash'
    @student_bp.route('/profile')
    def profile(): return 'Profile'
    @student_bp.route('/assignment/<int:assignment_id>')
    def assignment_detail(assignment_id): return f'Detail {assignment_id}'
    app.register_blueprint(student_bp, url_prefix='/student')

    auth_bp = Blueprint('auth', __name__)
    @auth_bp.route('/logout')
    def logout(): return 'Logout'
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/')
    def index(): return 'Index'
    
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
    return mock_user

class TestSubmissionRoutes:
    def test_view_submission_success(self, client, instructor_session, mock_services):
        mock_sub = Mock()
        mock_sub.get_id.return_value = 1
        mock_sub.get_assignment_id.return_value = 101
        mock_sub.status = 'graded'
        mock_sub.score = 85
        mock_sub.language = 'python'
        mock_sub.created_at = None
        mock_sub.is_late = False
        mock_sub.content = "print('hello')"
        
        mock_services['submission_repo'].get_by_id.return_value = mock_sub
        mock_ass = Mock()
        mock_ass.title = "Test Assignment"
        mock_ass.description = "Test Description"
        mock_ass.get_id.return_value = 101
        mock_services['assignment_repo'].get_by_id.return_value = mock_ass
        mock_services['result_repo'].find_by_submission.return_value = []
        
        mock_services['result_repo'].find_by_submission.return_value = []
        
        response = client.get('/submissions/1')
        assert response.status_code == 200
        assert b'Submission Details' in response.data

    def test_view_submission_not_found(self, client, instructor_session, mock_services):
        mock_services['submission_repo'].get_by_id.return_value = None
        response = client.get('/submissions/1', follow_redirects=True)
        assert b'Submission not found' in response.data

    def test_regrade_submission_success(self, client, instructor_session, mock_services):
        mock_sub = Mock()
        mock_services['submission_repo'].get_by_id.return_value = mock_sub
        
        response = client.post('/submissions/1/regrade', follow_redirects=True)
        assert b'Regrade requested' in response.data
        mock_services['sandbox_service'].regrade_submission.assert_called_with(mock_sub)

    def test_regrade_submission_not_found(self, client, instructor_session, mock_services):
        mock_services['submission_repo'].get_by_id.return_value = None
        response = client.post('/submissions/1/regrade', follow_redirects=True)
        assert b'Submission not found' in response.data

    def test_regrade_submission_error(self, client, instructor_session, mock_services):
        mock_services['submission_repo'].get_by_id.side_effect = Exception("DB error")
        response = client.post('/submissions/1/regrade', follow_redirects=True)
        assert b'DB error' in response.data
