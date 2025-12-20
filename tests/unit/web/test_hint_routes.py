import pytest
import os
from unittest.mock import Mock, patch
from flask import Flask, session, Blueprint
from core.entities.user import User

@pytest.fixture
def mock_services():
    return {
        'hint_service': Mock(),
        'user_repo': Mock(),
    }

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
            return {'current_user': user}
        return {'current_user': None}

    def format_date(value, fmt='%b %d, %Y'):
        if value is None: return 'N/A'
        return value.strftime(fmt) if hasattr(value, 'strftime') else str(value)
    
    app.jinja_env.filters['format_date'] = format_date
    app.extensions['services'] = mock_services
    
    from web.routes.hint import hint_bp
    app.register_blueprint(hint_bp)
    
    student_bp = Blueprint('student', __name__)
    @student_bp.route('/dashboard')
    def dashboard(): return 'Student Dash'
    @student_bp.route('/assignments')
    def assignments(): return 'Student Ass'
    @student_bp.route('/profile')
    def profile(): return 'Profile'
    app.register_blueprint(student_bp, url_prefix='/student')
    
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
def user_session(client, mock_services):
    mock_user = User(1, "User", "u@t.com", "p", "student")
    mock_services['user_repo'].get_by_id.return_value = mock_user
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'student'
    return mock_user

class TestHintRoutes:
    def test_generate_hint_success(self, client, user_session, mock_services):
        response = client.post('/hints/generate/1', follow_redirects=True)
        assert b'Hint generated successfully' in response.data
        mock_services['hint_service'].generate_hint.assert_called_with(submission_id=1)

    def test_generate_hint_error(self, client, user_session, mock_services):
        mock_services['hint_service'].generate_hint.side_effect = Exception("error")
        response = client.post('/hints/generate/1', follow_redirects=True)
        assert b'error' in response.data

    def test_list_hints_success(self, client, user_session, mock_services):
        mock_services['hint_service'].list_hints_for_submission.return_value = []
        response = client.get('/hints/submission/1', follow_redirects=True)
        assert b'Hints' in response.data or b'No hints available' in response.data

    def test_list_hints_error(self, client, user_session, mock_services):
        mock_services['hint_service'].list_hints_for_submission.side_effect = Exception("fail")
        response = client.get('/hints/submission/1', follow_redirects=True)
        assert b'fail' in response.data

    def test_mark_hint_helpful_success(self, client, user_session, mock_services):
        response = client.post('/hints/1/helpful', follow_redirects=True)
        assert b'Thanks for your feedback!' in response.data
        mock_services['hint_service'].mark_hint_helpful.assert_called_with(1)

    def test_mark_hint_helpful_error(self, client, user_session, mock_services):
        mock_services['hint_service'].mark_hint_helpful.side_effect = Exception("err")
        response = client.post('/hints/1/helpful', follow_redirects=True)
        assert b'err' in response.data

    def test_mark_hint_not_helpful_success(self, client, user_session, mock_services):
        response = client.post('/hints/1/not-helpful', follow_redirects=True)
        assert b'Feedback recorded' in response.data
        mock_services['hint_service'].mark_hint_not_helpful.assert_called_with(1)

    def test_mark_hint_not_helpful_error(self, client, user_session, mock_services):
        mock_services['hint_service'].mark_hint_not_helpful.side_effect = Exception("err")
        response = client.post('/hints/1/not-helpful', follow_redirects=True)
        assert b'err' in response.data
