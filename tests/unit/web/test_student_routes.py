import pytest
from unittest.mock import Mock, patch
from flask import Flask, session
from core.entities.user import User
from core.entities.student import Student
from core.entities.assignment import Assignment
from core.entities.submission import Submission

@pytest.fixture
def app():
    # Create a minimal app with the blueprint
    app = Flask(__name__)
    app.secret_key = 'test_secret'
    
    # Register blueprint
    from web.routes.student import student_bp
    app.register_blueprint(student_bp, url_prefix='/student')
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_container():
    with patch('web.routes.student.get_service') as mock_get:
        yield mock_get

@pytest.fixture
def auth_session(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'student'
        sess['logged_in'] = True

@pytest.mark.unit
class TestStudentRoutes:

    def test_dashboard_access(self, client, mock_container, auth_session):
        # Mock services
        mock_user_repo = Mock()
        mock_student_service = Mock()
        mock_assignment_repo = Mock()
        
        mock_container.side_effect = lambda name: {
            'user_repo': mock_user_repo,
            'student_service': mock_student_service,
            'assignment_repo': mock_assignment_repo
        }.get(name)
        
        # Mock data
        mock_user_repo.get_by_id.return_value = User(1, "Test Student", "test@test.com", "pwd", "student")
        mock_student_service.get_student_submissions.return_value = []
        mock_assignment_repo.get_all.return_value = []

        response = client.get('/student/dashboard')
        assert response.status_code == 200
        assert b'My Profile' in response.data or b'Dashboard' in response.data

    def test_assignments_view(self, client, mock_container, auth_session):
        mock_assignment_repo = Mock()
        mock_student_service = Mock()
        
        mock_container.side_effect = lambda name: {
            'assignment_repo': mock_assignment_repo,
            'student_service': mock_student_service
        }.get(name)

        # Corrected Assignment init
        mock_assignment_repo.get_all.return_value = [
            Assignment(1, 101, "A1", "Desc", None, None, 100, True, True, 0, None, None)
        ]
        mock_student_service.get_student_submissions.return_value = []

        response = client.get('/student/assignments')
        assert response.status_code == 200
        assert b'A1' in response.data

    def test_submit_assignment_post(self, client, mock_container, auth_session):
        mock_assignment_repo = Mock()
        mock_student_service = Mock()
        
        mock_container.side_effect = lambda name: {
            'assignment_repo': mock_assignment_repo,
            'student_service': mock_student_service
        }.get(name)

        # Corrected Assignment init
        assignment = Assignment(1, 101, "A1", "Desc", None, None, 100, True, True, 0, None, None)
        mock_assignment_repo.get_by_id.return_value = assignment
        
        mock_student_service.submit_assignment.return_value = Mock()

        response = client.post('/student/submit/1', data={'code': 'print("hello")'}, follow_redirects=True)
        
        assert response.status_code == 200
        mock_student_service.submit_assignment.assert_called_with(1, '1', 'print("hello")')
        assert b'Code submitted successfully' in response.data

    def test_profile_view(self, client, mock_container, auth_session):
        mock_student_service = Mock()
        mock_user_repo = Mock()
        
        mock_container.side_effect = lambda name: {
            'student_service': mock_student_service,
            'user_repo': mock_user_repo
        }.get(name)

        mock_student_service.get_student.return_value = Student(
            1, "Student Name", "s@test.com", "pwd", None, None, "S123", "CS", 1
        )
        mock_student_service.get_student_submissions.return_value = []

        response = client.get('/student/profile')
        assert response.status_code == 200
        assert b'Student Name' in response.data
        # Verify stub form rendering
        assert b'type="password"' in response.data
