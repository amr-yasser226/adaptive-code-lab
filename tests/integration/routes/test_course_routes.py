import pytest
import sqlite3
from core.entities.user import User
from core.entities.instructor import Instructor
from core.entities.course import Course
from core.entities.enrollment import Enrollment
from datetime import datetime
from werkzeug.security import generate_password_hash


@pytest.mark.integration
class TestCourseRoutes:
    """Test suite for course routes"""

    @pytest.fixture
    def logged_student(self, client, user_repo):
        user = User(None, "Student", "student@test.edu", generate_password_hash("password"), "student")
        user = user_repo.create(user)
        with client.session_transaction() as sess:
            sess['user_id'] = user.get_id()
            sess['user_role'] = 'student'
        return user

    @pytest.fixture
    def logged_instructor(self, client, user_repo, instructor_repo):
        user = User(None, "Instructor", "inst@test.edu", generate_password_hash("password"), "instructor")
        user = user_repo.create(user)
        # Must populate instructors table for FK constraint in courses
        inst = Instructor(user.get_id(), user.name, user.email, user.get_password_hash(), user.created_at, user.updated_at, "INST123", "Bio", "Hours")
        instructor_repo.save(inst)
        with client.session_transaction() as sess:
            sess['user_id'] = user.get_id()
            sess['user_role'] = 'instructor'
        return user

    def test_list_courses_instructor(self, client, logged_instructor, course_repo):
        # Create a course for this instructor
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "CS101", "Intro", "Desc", "2023", "Fall", 30, now, "active", now, 3)
        course_repo.create(course)
        
        response = client.get('/courses/')
        assert response.status_code == 200
        assert b'Intro' in response.data

    def test_list_courses_student(self, client, logged_student, course_repo, enrollment_repo, logged_instructor):
        # Create a course and enroll student
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "CS101", "Intro", "Desc", "2023", "Fall", 30, now, "active", now, 3)
        course = course_repo.create(course)
        enrollment_repo.enroll(Enrollment(logged_student.get_id(), course.get_id(), 'enrolled', datetime.now(), None, None))
        
        response = client.get('/courses/')
        assert response.status_code == 200
        assert b'Intro' in response.data

    def test_list_courses_other_role(self, client, user_repo):
        # Admin or other role
        user = User(None, "Admin", "admin@test.edu", generate_password_hash("password"), "admin")
        user = user_repo.create(user)
        with client.session_transaction() as sess:
            sess['user_id'] = user.get_id()
            sess['user_role'] = 'admin'
        
        response = client.get('/courses/')
        assert response.status_code == 200
        # Should return empty list/default view
        assert b'Courses' in response.data

    def test_course_detail_success(self, client, logged_student, course_repo, logged_instructor):
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "CS101", "Intro", "Desc", "2023", "Fall", 30, now, "active", now, 3)
        course = course_repo.create(course)
        
        response = client.get(f'/courses/{course.get_id()}')
        assert response.status_code == 200
        assert b'CS101' in response.data

    def test_course_detail_not_found(self, client, logged_student):
        response = client.get('/courses/9999', follow_redirects=True)
        assert b'Course not found' in response.data

    def test_create_course_get(self, client, logged_instructor):
        response = client.get('/courses/create')
        assert response.status_code == 200
        assert b'Create Course' in response.data or b'Create New Course' in response.data

    def test_create_course_post_success(self, client, logged_instructor, course_repo):
        data = {
            'code': 'CS202',
            'title': 'Advanced CS',
            'description': 'Deep dive',
            'year': '2024',
            'semester': 'Spring',
            'max_students': '50',
            'credits': '4'
        }
        response = client.post('/courses/create', data=data, follow_redirects=True)
        assert b'Course created successfully' in response.data
        
        courses = course_repo.list_by_instructor(logged_instructor.get_id())
        assert any(c.title == 'Advanced CS' for c in courses)

    def test_edit_course_success(self, client, logged_instructor, course_repo):
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "EDITME", "Old", "Old", "2023", "Fall", 30, now, "active", now, 3)
        course = course_repo.create(course)
        
        data = {
            'code': 'EDITED',
            'title': 'New Title',
            'description': 'New Desc',
            'year': '2025',
            'semester': 'Winter',
            'max_students': '100',
            'credits': '5'
        }
        response = client.post(f'/courses/{course.get_id()}/edit', data=data, follow_redirects=True)
        assert b'Course updated' in response.data
        
        updated = course_repo.get_by_id(course.get_id())
        assert updated.code == 'EDITED'
        assert updated.title == 'New Title'

    def test_edit_course_not_owner(self, client, user_repo, course_repo, logged_instructor):
        # Create course with instructor 1
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "PRIVATE", "Secret", "Desc", "2023", "Fall", 30, now, "active", now, 3)
        course = course_repo.create(course)
        
        # Log in as instructor 2
        user2 = User(None, "Inst 2", "inst2@test.edu", generate_password_hash("password"), "instructor")
        inst2 = user_repo.create(user2)
        with client.session_transaction() as sess:
            sess['user_id'] = inst2.get_id()
            sess['user_role'] = 'instructor'
            
        data = {'code': 'HACKED'}
        response = client.post(f'/courses/{course.get_id()}/edit', data=data, follow_redirects=True)
        assert b'You are not the owner of this course' in response.data

    def test_publish_course(self, client, logged_instructor, course_repo):
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "DRAFT", "Draft", "Desc", "2023", "Fall", 30, now, 'draft', now, 3)
        course = course_repo.create(course)
        
        response = client.post(f'/courses/{course.get_id()}/publish', follow_redirects=True)
        assert b'Course published' in response.data
        
        updated = course_repo.get_by_id(course.get_id())
        assert updated.status == 'active'

    def test_archive_course(self, client, logged_instructor, course_repo):
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "ACTIVE", "Active", "Desc", "2023", "Fall", 30, now, 'active', now, 3)
        course = course_repo.create(course)
        
        response = client.post(f'/courses/{course.get_id()}/archive', follow_redirects=True)
        assert b'Course archived' in response.data
        
        updated = course_repo.get_by_id(course.get_id())
        assert updated.status == 'inactive'

    def test_enroll_success(self, client, logged_student, course_repo, logged_instructor):
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "OPEN", "Open", "Desc", "2023", "Fall", 100, now, 'active', now, 3)
        course = course_repo.create(course)
        
        response = client.post(f'/courses/{course.get_id()}/enroll', follow_redirects=True)
        assert b'Enrolled successfully' in response.data

    def test_course_exceptions(self, client, logged_instructor, course_repo, monkeypatch):
        """Test general exception handling in list_courses"""
        def mock_list(*args, **kwargs):
            raise sqlite3.Error("Mock error")
        
        client.application.config['PROPAGATE_EXCEPTIONS'] = False
        with monkeypatch.context() as m:
            m.setattr("infrastructure.repositories.course_repository.CourseRepository.list_by_instructor", mock_list)
            response = client.get('/courses/', follow_redirects=True)
            assert b'Mock error' in response.data
        client.application.config['PROPAGATE_EXCEPTIONS'] = True

    def test_edit_course_not_found(self, client, logged_instructor):
        response = client.post('/courses/9999/edit', data={}, follow_redirects=True)
        assert b'Course not found' in response.data

    def test_publish_not_found(self, client, logged_instructor):
        response = client.post('/courses/9999/publish', follow_redirects=True)
        assert b'Course not found' in response.data

    def test_archive_not_found(self, client, logged_instructor):
        response = client.post('/courses/9999/archive', follow_redirects=True)
        assert b'Course not found' in response.data

    def test_enroll_not_found(self, client, logged_student):
        response = client.post('/courses/9999/enroll', follow_redirects=True)
        assert b'Course not found' in response.data
        
    def test_publish_not_authorized(self, client, user_repo, course_repo, logged_instructor):
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "AUTH", "Auth", "Desc", "2023", "Fall", 30, now, 'active', now, 3)
        course = course_repo.create(course)
        
        user2 = User(None, "Inst 2", "inst2@test.edu", generate_password_hash("password"), "instructor")
        inst2 = user_repo.create(user2)
        with client.session_transaction() as sess:
            sess['user_id'] = inst2.get_id()
            sess['user_role'] = 'instructor'
            
        response = client.post(f'/courses/{course.get_id()}/publish', follow_redirects=True)
        assert b'Not authorized' in response.data

    def test_archive_not_authorized(self, client, user_repo, course_repo, logged_instructor):
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "AUTH", "Auth", "Desc", "2023", "Fall", 30, now, 'active', now, 3)
        course = course_repo.create(course)
        
        user2 = User(None, "Inst 2", "inst2@test.edu", generate_password_hash("password"), "instructor")
        inst2 = user_repo.create(user2)
        with client.session_transaction() as sess:
            sess['user_id'] = inst2.get_id()
            sess['user_role'] = 'instructor'
            
        response = client.post(f'/courses/{course.get_id()}/archive', follow_redirects=True)
        assert b'Not authorized' in response.data

    def test_course_detail_exception(self, client, logged_student, course_repo, monkeypatch):
        def mock_get(*args, **kwargs):
            raise sqlite3.Error("Detail error")
        
        client.application.config['PROPAGATE_EXCEPTIONS'] = False
        with monkeypatch.context() as m:
            m.setattr("infrastructure.repositories.course_repository.CourseRepository.get_by_id", mock_get)
            response = client.get('/courses/1', follow_redirects=True)
            assert b'Detail error' in response.data
        client.application.config['PROPAGATE_EXCEPTIONS'] = True

    def test_create_course_validation_error(self, client, logged_instructor, monkeypatch):
        from core.exceptions.validation_error import ValidationError
        def mock_create(*args, **kwargs):
            raise ValidationError("Validation failed")
            
        with monkeypatch.context() as m:
            m.setattr("core.services.instructor_service.InstructorService.create_course", mock_create)
            data = {'code': 'FAIL', 'title': 'Fail'}
            response = client.post('/courses/create', data=data, follow_redirects=True)
            assert b'Validation failed' in response.data

    def test_edit_course_update_failure(self, client, logged_instructor, course_repo, monkeypatch):
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "FAILUPDATE", "Old", "Old", "2023", "Fall", 30, now, "active", now, 3)
        course = course_repo.create(course)
        
        def mock_update(*args, **kwargs):
            return None
            
        with monkeypatch.context() as m:
            m.setattr("infrastructure.repositories.course_repository.CourseRepository.update", mock_update)
            data = {'title': 'New'}
            response = client.post(f'/courses/{course.get_id()}/edit', data=data, follow_redirects=True)
            assert b'Failed to update course' in response.data

    def test_archive_exception(self, client, logged_instructor, course_repo, monkeypatch):
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "ARCHFAIL", "Old", "Old", "2023", "Fall", 30, now, "active", now, 3)
        course = course_repo.create(course)
        
        def mock_archive(*args, **kwargs):
            raise sqlite3.Error("Archive error")
            
        client.application.config['PROPAGATE_EXCEPTIONS'] = False
        with monkeypatch.context() as m:
            m.setattr("infrastructure.repositories.course_repository.CourseRepository.archive", mock_archive)
            response = client.post(f'/courses/{course.get_id()}/archive', follow_redirects=True)
            print(f"DEBUG RESPONSE: {response.data[:500]}")
            assert b'Archive error' in response.data
        client.application.config['PROPAGATE_EXCEPTIONS'] = True

    def test_enroll_validation_error(self, client, logged_student, course_repo, logged_instructor, monkeypatch):
        now = datetime.now()
        course = Course(None, logged_instructor.get_id(), "ENROLLFAIL", "Open", "Desc", "2023", "Fall", 100, now, 'active', now, 3)
        course = course_repo.create(course)
        
        from core.exceptions.validation_error import ValidationError
        def mock_enroll(*args, **kwargs):
            raise ValidationError("Enrollment failed")
            
        with monkeypatch.context() as m:
            m.setattr("infrastructure.repositories.enrollment_repository.EnrollmentRepository.enroll", mock_enroll)
            response = client.post(f'/courses/{course.get_id()}/enroll', follow_redirects=True)
            assert b'Enrollment failed' in response.data
