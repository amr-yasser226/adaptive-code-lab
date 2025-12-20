import pytest
from core.entities.user import User
from flask import session


@pytest.mark.integration
class TestAuthRoutes:
    """Test suite for authentication routes"""

    def test_login_page_get(self, client):
        """Test GET /auth/login"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'Sign In' in response.data

    def test_register_page_get(self, client):
        """Test GET /auth/register"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data or b'Create Account' in response.data

    def test_registration_success(self, client, user_repo):
        """Test successful registration"""
        data = {
            'name': 'New Student',
            'email': 'new@student.edu',
            'password': 'password123',
            'role': 'student'
        }
        response = client.post('/auth/register', data=data)
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/auth/login')
        
        user = user_repo.get_by_email('new@student.edu')
        assert user is not None
        assert user.name == 'New Student'
        assert user.role == 'student'

    def test_registration_validation_name(self, client):
        """Test registration validation for name"""
        data = {'name': 's', 'email': 'valid@test.com', 'password': 'password123'}
        response = client.post('/auth/register', data=data, follow_redirects=True)
        assert b'Name must be at least 2 characters' in response.data

    def test_registration_validation_email(self, client):
        """Test registration validation for email"""
        data = {'name': 'Valid Name', 'email': 'invalid-email', 'password': 'password123'}
        response = client.post('/auth/register', data=data, follow_redirects=True)
        assert b'Invalid email format' in response.data

    def test_registration_validation_password(self, client):
        """Test registration validation for password"""
        data = {'name': 'Valid Name', 'email': 'valid@test.com', 'password': 'short'}
        response = client.post('/auth/register', data=data, follow_redirects=True)
        assert b'Password must be at least 8 characters' in response.data

    def test_login_success_student(self, client, user_repo):
        """Test successful login for a student"""
        client.post('/auth/register', data={
            'name': 'Login Student',
            'email': 'login@student.edu',
            'password': 'password123',
            'role': 'student'
        })
        
        response = client.post('/auth/login', data={
            'email': 'login@student.edu',
            'password': 'password123'
        })
        
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/student/dashboard')
        
        with client.session_transaction() as sess:
            assert sess['user_role'] == 'student'

    def test_login_success_instructor(self, client, user_repo):
        """Test successful login for an instructor"""
        client.post('/auth/register', data={
            'name': 'Login Instructor',
            'email': 'login@inst.edu',
            'password': 'password123',
            'role': 'instructor'
        })
        
        response = client.post('/auth/login', data={
            'email': 'login@inst.edu',
            'password': 'password123'
        })
        
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/instructor/dashboard')
        
        with client.session_transaction() as sess:
            assert sess['user_role'] == 'instructor'

    def test_login_success_admin(self, client, user_repo):
         """Test successful login for an admin (redirects to index)"""
         from werkzeug.security import generate_password_hash
         user = User(None, 'Admin User', 'admin@test.edu', generate_password_hash('password123'), 'admin')
         user_repo.create(user)
         
         response = client.post('/auth/login', data={
             'email': 'admin@test.edu',
             'password': 'password123'
         })
         
         assert response.status_code == 302
         # Redirects to index
         assert response.headers['Location'].endswith('/')

    def test_login_failure(self, client):
        """Test login failure with wrong credentials"""
        response = client.post('/auth/login', data={
            'email': 'wrong@test.edu',
            'password': 'wrong'
        }, follow_redirects=True)
        # AuthError in AuthService.login is "Invalid credentials"
        assert b'Invalid credentials' in response.data

    def test_logout(self, client):
        """Test logout"""
        response = client.get('/auth/logout')
        assert response.status_code == 302
        assert response.headers['Location'].endswith('/')
        
        with client.session_transaction() as sess:
            assert 'user_id' not in sess

    def test_registration_auth_error(self, client):
        """Test registration with existing email (AuthError)"""
        client.post('/auth/register', data={
            'name': 'User 1',
            'email': 'duplicate@test.edu',
            'password': 'password123',
            'role': 'student'
        })
        response = client.post('/auth/register', data={
            'name': 'User 2',
            'email': 'duplicate@test.edu',
            'password': 'password123',
            'role': 'student'
        }, follow_redirects=True)
        # AuthError in AuthService.register is "Email already registered"
        assert b'Email already registered' in response.data
