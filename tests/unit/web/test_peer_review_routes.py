import pytest
import os
import sqlite3
from unittest.mock import Mock, patch
from flask import Flask, session, Blueprint
from core.entities.user import User
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError

@pytest.fixture
def mock_services():
    return {
        'peer_review_service': Mock(),
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
        
    app.extensions['services'] = mock_services
    
    from web.routes.peer_review import peer_review_bp
    app.register_blueprint(peer_review_bp)
    
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

class TestPeerReviewRoutes:
    def test_create_review_success(self, client, student_session, mock_services):
        response = client.post('/peer-review/create/1', data={'rubric_score': '5', 'comments': 'Good'}, follow_redirects=True)
        assert b'Peer review created successfully' in response.data
        mock_services['peer_review_service'].create_review.assert_called_with(
            reviewer_student=student_session,
            submission_id=1,
            rubric_score='5',
            comments='Good'
        )

    def test_create_review_error(self, client, student_session, mock_services):
        mock_services['peer_review_service'].create_review.side_effect = ValidationError("Invalid score")
        response = client.post('/peer-review/create/1', data={'rubric_score': '15'}, follow_redirects=True)
        assert b'Invalid score' in response.data

    def test_create_review_db_error(self, client, student_session, mock_services):
        mock_services['peer_review_service'].create_review.side_effect = sqlite3.Error("DB error")
        response = client.post('/peer-review/create/1', data={}, follow_redirects=True)
        assert b'DB error' in response.data

    def test_update_review_success(self, client, student_session, mock_services):
        response = client.post('/peer-review/update/1', data={'rubric_score': '4', 'comments': 'Updated'}, follow_redirects=True)
        assert b'Peer review updated successfully' in response.data
        mock_services['peer_review_service'].update_review.assert_called_with(
            reviewer_student=student_session,
            submission_id=1,
            rubric_score='4',
            comments='Updated'
        )

    def test_update_review_error(self, client, student_session, mock_services):
        mock_services['peer_review_service'].update_review.side_effect = AuthError("Not reviewer")
        response = client.post('/peer-review/update/1', data={}, follow_redirects=True)
        assert b'Not reviewer' in response.data

    def test_submit_review_success(self, client, student_session, mock_services):
        response = client.post('/peer-review/submit/1', follow_redirects=True)
        assert b'Peer review submitted successfully' in response.data
        mock_services['peer_review_service'].submit_review.assert_called_with(
            reviewer_student=student_session,
            submission_id=1
        )

    def test_submit_review_error(self, client, student_session, mock_services):
        mock_services['peer_review_service'].submit_review.side_effect = ValidationError("Already submitted")
        response = client.post('/peer-review/submit/1', follow_redirects=True)
        assert b'Already submitted' in response.data

    def test_list_reviews_success(self, client, student_session, mock_services):
        mock_services['peer_review_service'].list_reviews_for_submission.return_value = []
        response = client.get('/peer-review/submission/1')
        assert response.status_code == 200
        assert b'reviews' in response.data or b'Reviews' in response.data

    def test_list_reviews_error(self, client, student_session, mock_services):
        mock_services['peer_review_service'].list_reviews_for_submission.side_effect = AuthError("Denied")
        response = client.get('/peer-review/submission/1', follow_redirects=True)
        assert b'Denied' in response.data
