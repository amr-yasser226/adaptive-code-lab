import pytest
import os
from unittest.mock import Mock, patch
from flask import Flask, session, Blueprint
from core.entities.user import User
from core.exceptions.validation_error import ValidationError
from core.exceptions.auth_error import AuthError

@pytest.fixture
def mock_services():
    return {
        'enrollment_service': Mock(),
        'enrollment_repo': Mock(),
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
    
    from web.routes.enrollment import enrollment_bp
    app.register_blueprint(enrollment_bp)
    
    course_bp = Blueprint('course', __name__)
    @course_bp.route('/<int:course_id>')
    def course_detail(course_id):
        from flask import get_flashed_messages
        return f"Detail {course_id} {' '.join(get_flashed_messages())}"
    @course_bp.route('/')
    def list_courses():
        from flask import get_flashed_messages
        return f"Courses {' '.join(get_flashed_messages())}"
    app.register_blueprint(course_bp, url_prefix='/courses')
    
    student_bp = Blueprint('student', __name__)
    @student_bp.route('/dashboard')
    def dashboard(): return 'Student Dash'
    @student_bp.route('/assignments')
    def assignments(): return 'Student Ass'
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

@pytest.fixture
def instructor_session(client, mock_services):
    mock_user = User(2, "Inst", "i@t.com", "p", "instructor")
    mock_services['user_repo'].get_by_id.return_value = mock_user
    with client.session_transaction() as sess:
        sess['user_id'] = 2
        sess['user_role'] = 'instructor'
    return mock_user

@pytest.fixture
def admin_session(client, mock_services):
    mock_user = User(3, "Admin", "a@t.com", "p", "admin")
    mock_services['user_repo'].get_by_id.return_value = mock_user
    with client.session_transaction() as sess:
        sess['user_id'] = 3
        sess['user_role'] = 'admin'
    return mock_user

class TestEnrollmentRoutes:
    def test_my_enrollments_success(self, client, student_session, mock_services):
        mock_services['enrollment_service'].list_by_student.return_value = []
        response = client.get('/enrollments/my', follow_redirects=True)
        assert response.status_code == 200
        assert b'enrollments' in response.data or b'Enrollments' in response.data

    def test_my_enrollments_error(self, client, student_session, mock_services):
        mock_services['enrollment_service'].list_by_student.side_effect = Exception("error")
        response = client.get('/enrollments/my', follow_redirects=True)
        assert b'error' in response.data

    def test_course_enrollments_success(self, client, instructor_session, mock_services):
        mock_services['enrollment_service'].list_by_course.return_value = []
        response = client.get('/enrollments/course/1', follow_redirects=True)
        assert response.status_code == 200

    def test_enroll_in_course_success(self, client, student_session, mock_services):
        response = client.post('/enrollments/course/1/enroll', follow_redirects=True)
        assert b'Enrolled successfully' in response.data

    def test_enroll_in_course_validation_error(self, client, student_session, mock_services):
        mock_services['enrollment_service'].enroll_student.side_effect = ValidationError("Already enrolled")
        response = client.post('/enrollments/course/1/enroll', follow_redirects=True)
        assert b'Already enrolled' in response.data

    def test_drop_course_success(self, client, student_session, mock_services):
        response = client.post('/enrollments/course/1/drop', follow_redirects=True)
        assert b'Dropped course' in response.data

    def test_complete_student_course_success(self, client, instructor_session, mock_services):
        mock_en = Mock()
        mock_services['enrollment_repo'].get.return_value = mock_en
        response = client.post('/enrollments/1/1/complete', data={'final_grade': '95'}, follow_redirects=True)
        assert b'Marked as completed' in response.data
        mock_services['enrollment_service'].complete_course.assert_called()

    def test_complete_student_course_not_found(self, client, instructor_session, mock_services):
        mock_services['enrollment_repo'].get.return_value = None
        response = client.post('/enrollments/1/1/complete', data={'final_grade': '95'}, follow_redirects=True)
        assert b'Enrollment not found' in response.data

    def test_complete_student_course_invalid_grade(self, client, instructor_session, mock_services):
        mock_en = Mock()
        mock_services['enrollment_repo'].get.return_value = mock_en
        response = client.post('/enrollments/1/1/complete', data={'final_grade': 'abc'}, follow_redirects=True)
        assert b'Invalid grade value' in response.data

    def test_manage_enrollment_drop(self, client, admin_session, mock_services):
        mock_en = Mock()
        mock_services['enrollment_repo'].get.return_value = mock_en
        response = client.post('/enrollments/1/1/manage', data={'action': 'drop'}, follow_redirects=True)
        assert b'Enrollment dropped' in response.data
        mock_services['enrollment_repo'].update.assert_called()

    def test_manage_enrollment_complete(self, client, admin_session, mock_services):
        mock_en = Mock()
        mock_services['enrollment_repo'].get.return_value = mock_en
        response = client.post('/enrollments/1/1/manage', data={'action': 'complete', 'final_grade': '80'}, follow_redirects=True)
        assert b'Enrollment updated' in response.data
        assert mock_en.status == 'completed'

    def test_manage_enrollment_invalid_grade(self, client, admin_session, mock_services):
        mock_en = Mock()
        mock_services['enrollment_repo'].get.return_value = mock_en
        response = client.post('/enrollments/1/1/manage', data={'action': 'complete', 'final_grade': 'xxx'}, follow_redirects=True)
        assert b'Invalid grade' in response.data

    def test_manage_enrollment_unknown_action(self, client, admin_session, mock_services):
        mock_en = Mock()
        mock_services['enrollment_repo'].get.return_value = mock_en
        response = client.post('/enrollments/1/1/manage', data={'action': 'jump'}, follow_redirects=True)
        assert b'Unknown action' in response.data

    def test_enroll_in_course_generic_error(self, client, student_session, mock_services):
        mock_services['enrollment_service'].enroll_student.side_effect = Exception("DB fail")
        response = client.post('/enrollments/course/1/enroll', follow_redirects=True)
        assert b'DB fail' in response.data

    def test_drop_course_auth_error(self, client, student_session, mock_services):
        mock_services['enrollment_service'].drop_course.side_effect = AuthError("Cannot drop")
        response = client.post('/enrollments/course/1/drop', follow_redirects=True)
        assert b'Cannot drop' in response.data

    def test_complete_student_course_auth_error(self, client, instructor_session, mock_services):
        mock_en = Mock()
        mock_services['enrollment_repo'].get.return_value = mock_en
        mock_services['enrollment_service'].complete_course.side_effect = AuthError("Not auth")
        response = client.post('/enrollments/1/1/complete', data={'final_grade': '90'}, follow_redirects=True)
        assert b'Not auth' in response.data

    def test_manage_enrollment_not_found(self, client, admin_session, mock_services):
        mock_services['enrollment_repo'].get.return_value = None
        response = client.post('/enrollments/1/1/manage', data={'action': 'drop'}, follow_redirects=True)
        assert b'Enrollment not found' in response.data

    def test_manage_enrollment_exception(self, client, admin_session, mock_services):
        mock_services['enrollment_repo'].get.side_effect = Exception("error")
        response = client.post('/enrollments/1/1/manage', data={'action': 'drop'}, follow_redirects=True)
        assert b'error' in response.data
