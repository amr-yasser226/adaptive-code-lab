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
        'test_case_service': Mock(),
        'test_case_repo': Mock(),
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
            return {'current_user': user, 'csrf_token': lambda: 'mock_token'}
        return {'current_user': None, 'csrf_token': lambda: 'mock_token'}
        
    app.extensions['services'] = mock_services
    
    from web.routes.test_case import test_case_bp
    app.register_blueprint(test_case_bp)
    
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
    
    instructor_bp = Blueprint('instructor', __name__)
    @instructor_bp.route('/dashboard')
    def dashboard(): 
        from flask import get_flashed_messages
        return f"Instructor Dash {' '.join(get_flashed_messages())}"
    @instructor_bp.route('/analytics')
    def analytics(): return 'Analytics'
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    
    assignment_bp = Blueprint('assignment', __name__)
    @assignment_bp.route('/view-submissions/<int:assignment_id>')
    def view_submissions(assignment_id): 
        from flask import get_flashed_messages
        return f'Submissions {assignment_id} {" ".join(get_flashed_messages())}'
    app.register_blueprint(assignment_bp, url_prefix='/assignment')
    
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
    mock_user = User(1, "Instructor", "i@t.com", "p", "instructor")
    mock_services['user_repo'].get_by_id.return_value = mock_user
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'instructor'
    return mock_user

class TestTestCaseRoutes:
    def test_create_test_case_get(self, client, instructor_session, mock_services):
        response = client.get('/test-cases/create/1')
        assert response.status_code == 200
        assert b'create' in response.data or b'Create' in response.data

    def test_create_test_case_success(self, client, instructor_session, mock_services):
        data = {'name': 'TC1', 'stdin': 'in', 'expected_out': 'out', 'points': '10', 'is_visible': 'on'}
        response = client.post('/test-cases/create/1', data=data, follow_redirects=True)
        assert b'Test case created' in response.data
        mock_services['test_case_service'].create_test_case.assert_called()

    def test_create_test_case_error(self, client, instructor_session, mock_services):
        mock_services['test_case_service'].create_test_case.side_effect = ValidationError("Bad data")
        response = client.post('/test-cases/create/1', data={}, follow_redirects=True)
        assert b'Bad data' in response.data

    def test_create_test_case_db_error(self, client, instructor_session, mock_services):
        mock_services['test_case_service'].create_test_case.side_effect = sqlite3.Error("DB fail")
        response = client.post('/test-cases/create/1', data={}, follow_redirects=True)
        assert b'DB fail' in response.data

    def test_edit_test_case_get_success(self, client, instructor_session, mock_services):
        mock_services['test_case_repo'].get_by_id.return_value = Mock(id=1, name='TC1', stdin='', expected_out='', points=0, is_visible=True)
        response = client.get('/test-cases/1/edit')
        assert response.status_code == 200
        assert b'Edit Test Case' in response.data

    def test_edit_test_case_get_not_found(self, client, instructor_session, mock_services):
        mock_services['test_case_repo'].get_by_id.return_value = None
        response = client.get('/test-cases/1/edit', follow_redirects=True)
        assert b'Test case not found' in response.data

    def test_edit_test_case_get_db_error(self, client, instructor_session, mock_services):
        mock_services['test_case_repo'].get_by_id.side_effect = sqlite3.Error("DB error")
        response = client.get('/test-cases/1/edit', follow_redirects=True)
        assert b'DB error' in response.data

    def test_edit_test_case_post_success(self, client, instructor_session, mock_services):
        data = {'name': 'TC1 Updated', 'points': '20'}
        response = client.post('/test-cases/1/edit', data=data, follow_redirects=True)
        assert b'Test case updated' in response.data
        mock_services['test_case_service'].update_test_case.assert_called()

    def test_edit_test_case_post_error(self, client, instructor_session, mock_services):
        mock_services['test_case_service'].update_test_case.side_effect = AuthError("No access")
        # For error case, it renders the template again, but we need the testcase mock for GET part
        mock_services['test_case_repo'].get_by_id.return_value = Mock(id=1, name='TC1', stdin='', expected_out='', points=0, is_visible=True)
        response = client.post('/test-cases/1/edit', data={}, follow_redirects=True)
        assert b'No access' in response.data

    def test_edit_test_case_post_db_error(self, client, instructor_session, mock_services):
        mock_services['test_case_service'].update_test_case.side_effect = sqlite3.Error("DB fail")
        mock_services['test_case_repo'].get_by_id.return_value = Mock(id=1, name='TC1', stdin='', expected_out='', points=0, is_visible=True)
        response = client.post('/test-cases/1/edit', data={}, follow_redirects=True)
        assert b'DB fail' in response.data

    def test_delete_test_case_success(self, client, instructor_session, mock_services):
        response = client.post('/test-cases/1/delete', follow_redirects=True)
        assert b'Test case deleted' in response.data
        mock_services['test_case_service'].delete_test_case.assert_called()

    def test_delete_test_case_error(self, client, instructor_session, mock_services):
        mock_services['test_case_service'].delete_test_case.side_effect = Exception("failed")
        response = client.post('/test-cases/1/delete', follow_redirects=True)
        assert b'failed' in response.data
