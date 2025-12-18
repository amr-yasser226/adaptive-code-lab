import pytest
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# No top-level imports from 'src' or 'web' here to avoid early DatabaseManager init

@pytest.fixture(autouse=True)
def env_setup(test_db_path):
    os.environ['ACCL_DB_PATH'] = f"sqlite:///{test_db_path}"
    os.environ['SECRET_KEY'] = 'testing_secret_key'
    yield

@pytest.fixture
def app():
    # Deferred imports
    from web.app import create_app
    test_config = {
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'testing_secret_key'
    }
    return create_app(test_config)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.mark.integration
class TestFullFlow:
    """End-to-end integration tests for critical flows."""

    @patch('core.services.sandbox_service.SandboxService.execute_code')
    def test_student_happy_path(self, mock_execute, client, clean_db):
        """Student: Register -> Login -> Enroll -> Submit -> View Results"""
        mock_execute.return_value = {
            'success': True,
            'stdout': 'Hello World\n',
            'stderr': '',
            'runtime_ms': 100
        }

        # 1. Register student
        client.post('/auth/register', data={
            'name': 'Bob Student',
            'email': 'bob_integration@test.edu',
            'password': 'password123',
            'role': 'student'
        }, follow_redirects=True)
        
        # Manually create student record
        services = client.application.extensions['services']
        user_repo = services['user_repo']
        student_user = user_repo.get_by_email('bob_integration@test.edu')
        assert student_user is not None
        
        services['student_repo'].db.execute(
            "INSERT INTO students (id, student_number, program, year_level) VALUES (?, ?, ?, ?)",
            (student_user.get_id(), "S12345", "Computer Science", 1)
        )
        services['student_repo'].db.commit()

        # 2. Login
        resp = client.post('/auth/login', data={
            'email': 'bob_integration@test.edu',
            'password': 'password123'
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Dashboard" in resp.data

        # 3. Setup Course & Assignment
        course_repo = services['course_repo']
        assignment_repo = services['assignment_repo']
        
        # Need an instructor
        from core.entities.user import User
        instructor_user = User(None, "Prof", "prof_integration@test.edu", "hashed", "instructor")
        instructor = user_repo.create(instructor_user)
        assert instructor is not None
        
        # Create instructor record
        services['instructor_repo'].db.execute(
            "INSERT INTO instructors (id, instructor_code, bio, office_hours) VALUES (?, ?, ?, ?)",
            (instructor.get_id(), "I-001", "Professor of CS", "Mon 10-12")
        )
        services['instructor_repo'].db.commit()

        from core.entities.course import Course
        course = course_repo.create(Course(
            None, instructor.get_id(), "CS101", "Intro", "Desc", 2024, "Fall", 30,
            datetime.now(), "active", datetime.now(), 3
        ))
        assert course is not None, "Course creation failed"
        
        from core.entities.assignment import Assignment
        assignment = assignment_repo.create(Assignment(
            None, course.get_id(), "Lab 1", "Print Hello",
            datetime.now().strftime('%Y-%m-%d'), (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            100, True, True, 0.1, None, None
        ))

        # 4. Enroll in course
        resp = client.post(f'/courses/{course.get_id()}/enroll', follow_redirects=True)
        assert resp.status_code == 200
        assert b"Enrolled successfully" in resp.data

        # 5. Submit code
        resp = client.post(f'/student/submit/{assignment.get_id()}', data={
            'code': 'print("Hello World")',
            'language': 'python'
        }, follow_redirects=True)
        assert resp.status_code == 200

        # 6. Verify dashboard
        resp = client.get('/student/dashboard')
        assert b"Lab 1" in resp.data

    def test_instructor_happy_path(self, client, clean_db):
        """Instructor: Login -> Create Course -> Create Assignment -> View Submissions"""
        services = client.application.extensions['services']
        user_repo = services['user_repo']
        auth_service = services['auth_service']

        # 1. Register instructor
        auth_service.register("Dr. Alice", "alice_integration@test.edu", "password123", "instructor")
        instructor_user = user_repo.get_by_email('alice_integration@test.edu')
        assert instructor_user is not None
        
        services['instructor_repo'].db.execute(
            "INSERT INTO instructors (id, instructor_code, bio, office_hours) VALUES (?, ?, ?, ?)",
            (instructor_user.get_id(), "I-102", "Senior Lecturer", "Wed 2-4")
        )
        services['instructor_repo'].db.commit()

        # 2. Login
        client.post('/auth/login', data={
            'email': 'alice_integration@test.edu',
            'password': 'password123'
        }, follow_redirects=True)

        # 3. Create Course
        resp = client.post('/courses/create', data={
            'code': 'CS202',
            'title': 'Advanced Python',
            'description': 'Deep dive',
            'year': 2024,
            'semester': 'Spring',
            'max_students': 50,
            'credits': 4
        }, follow_redirects=True)
        assert resp.status_code == 200
        
        # Verify course created
        course_repo = services['course_repo']
        courses = course_repo.list_by_instructor(instructor_user.get_id())
        assert len(courses) > 0
        course_id = courses[0].get_id()

        # 3b. Publish Course (Assignments only allowed on active courses)
        client.post(f'/courses/{course_id}/publish', follow_redirects=True)

        # 4. Create Assignment
        resp = client.post('/assignments/create', data={
            'course_id': course_id,
            'title': 'Project X',
            'description': 'Build something',
            'release_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'max_points': 100,
            'allow_late': 'on',
            'late_penalty': 5
        }, follow_redirects=True)
        assert resp.status_code == 200
        
        # If failure, print response to help debug
        if b"Project X" not in resp.data and b"Dashboard" in resp.data:
             # We might be back on dashboard but without the assignment
             pass 

        # 5. Check Dashboard
        resp = client.get('/instructor/dashboard')
        assert b"Advanced Python" in resp.data
        assert b"Project X" in resp.data
