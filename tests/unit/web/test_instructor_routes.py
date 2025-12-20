import pytest
import os
import sqlite3
from datetime import datetime as dt
from unittest.mock import Mock, MagicMock
from flask import Flask
from core.entities.user import User
from core.entities.course import Course
from core.entities.assignment import Assignment
from core.entities.submission import Submission


@pytest.fixture
def mock_services():
    """Create mock services for testing."""
    return {
        'auth_service': Mock(),
        'user_repo': Mock(),
        'student_service': Mock(),
        'assignment_repo': Mock(),
        'instructor_service': Mock(),
        'submission_repo': Mock(),
        'course_repo': Mock(),
        'enrollment_repo': Mock(),
        'flag_repo': Mock(),
        'assignment_service': Mock(),
    }


@pytest.fixture
def app(mock_services):
    """Create a test Flask app with instructor and related blueprints."""
    template_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/templates')
    static_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/static')
    
    app = Flask(__name__, 
                template_folder=os.path.abspath(template_dir),
                static_folder=os.path.abspath(static_dir))
    app.secret_key = 'test_secret'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    # Add csrf_token to template context
    @app.context_processor
    def inject_csrf_token():
        return {'csrf_token': lambda: ''}
    
    # Add current_user context processor (templates require this)
    @app.context_processor
    def inject_current_user():
        from flask import session
        if 'user_id' in session:
            user = mock_services['user_repo'].get_by_id(session['user_id'])
            return {'current_user': user, 'user': user}
        return {'current_user': None}
    
    # format_date filter
    def format_date(value, fmt='%b %d, %Y'):
        if value is None:
            return 'N/A'
        if isinstance(value, str):
            for parse_fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                try:
                    value = dt.strptime(value, parse_fmt)
                    break
                except ValueError:
                    continue
            else:
                return value
        return value.strftime(fmt)
    
    app.jinja_env.filters['format_date'] = format_date
    
    # Inject mock services
    app.extensions['services'] = mock_services
    
    # Stub index route
    @app.route('/')
    def index():
        return 'Home'
    
    # Register blueprints
    from web.routes.auth import auth_bp
    from web.routes.student import student_bp
    from web.routes.instructor import instructor_bp
    from web.routes.course import course_bp
    from web.routes.assignment import assignment_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(instructor_bp, url_prefix='/instructor')
    app.register_blueprint(course_bp, url_prefix='/courses')
    app.register_blueprint(assignment_bp, url_prefix='/assignments')
    
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def instructor_session(client):
    """Set up an authenticated instructor session."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'instructor'
        sess['logged_in'] = True


@pytest.fixture
def mock_instructor_user():
    """Create a mock instructor user."""
    return User(1, "Test Instructor", "instructor@test.com", "hashed", "instructor")


@pytest.mark.unit
class TestInstructorRoutes:

    def test_dashboard_unauthenticated_redirects(self, client):
        """Test that unauthenticated access redirects to login."""
        response = client.get('/instructor/dashboard')
        assert response.status_code == 302
        assert '/login' in response.location or 'auth' in response.location.lower()

    def test_dashboard_student_role_redirects(self, client, mock_services):
        """Test that student role cannot access instructor dashboard."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_role'] = 'student'
        
        response = client.get('/instructor/dashboard')
        assert response.status_code == 302  # Redirected due to role check

    def test_dashboard_renders_for_instructor(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test that dashboard is accessible and renders correctly for instructor."""
        mock_services['user_repo'].get_by_id.return_value = mock_instructor_user
        mock_services['instructor_service'].get_instructor.return_value = mock_instructor_user
        mock_services['course_repo'].list_by_instructor.return_value = []
        mock_services['assignment_repo'].get_all.return_value = []
        mock_services['submission_repo'].get_all.return_value = []
        mock_services['flag_repo'].get_all.return_value = []
        mock_services['enrollment_repo'].get_all.return_value = []
        
        response = client.get('/instructor/dashboard')
        assert response.status_code == 200
        assert b'Assignment Dashboard' in response.data
        assert b'Total Assignments' in response.data

    def test_analytics_page_accessible(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test that analytics page is accessible for instructor."""
        mock_services['user_repo'].get_by_id.return_value = mock_instructor_user
        mock_services['instructor_service'].get_instructor.return_value = mock_instructor_user
        mock_services['course_repo'].find_by_instructor.return_value = []
        mock_services['assignment_repo'].get_all.return_value = []
        mock_services['submission_repo'].get_all.return_value = []
        mock_services['enrollment_repo'].get_all.return_value = []
        
        response = client.get('/instructor/analytics')
        # Check route is accessible and auth works
        assert response.status_code != 302

    def test_plagiarism_dashboard_renders(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test that plagiarism dashboard renders for instructor."""
        mock_services['user_repo'].get_by_id.return_value = mock_instructor_user
        mock_services['flag_repo'].list_unreviewed.return_value = []
        mock_services['assignment_repo'].get_all.return_value = []
        
        response = client.get('/instructor/plagiarism')
        assert response.status_code == 200

    def test_assignment_detail_accessible(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test that assignment detail page is accessible."""
        mock_assignment = Assignment(
            1, 101, "Test Assignment", "Description", 
            "2024-01-01", "2024-01-31", 100, True, True, 0, dt.now(), dt.now()
        )
        mock_services['user_repo'].get_by_id.return_value = mock_instructor_user
        mock_services['assignment_repo'].get_by_id.return_value = mock_assignment
        mock_services['submission_repo'].get_all.return_value = []
        
        response = client.get('/instructor/analytics/assignment/1')
        assert response.status_code == 200
        assert b'Test Assignment' in response.data

    def test_assignment_detail_not_found_redirects(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test that non-existent assignment redirects."""
        mock_services['user_repo'].get_by_id.return_value = mock_instructor_user
        mock_services['assignment_repo'].get_by_id.return_value = None
        mock_services['submission_repo'].get_all.return_value = []
        
        response = client.get('/instructor/analytics/assignment/999')
        # Should redirect to analytics page
        assert response.status_code == 302

    def test_export_csv(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test CSV export functionality."""
        mock_services['user_repo'].get_by_id.return_value = mock_instructor_user
        mock_services['instructor_service'].get_instructor.return_value = mock_instructor_user
        mock_services['course_repo'].list_by_instructor.return_value = []
        mock_services['assignment_repo'].get_all.return_value = []
        mock_services['submission_repo'].get_all.return_value = []
        
        response = client.get('/instructor/analytics/export')
        assert response.status_code == 200
        assert 'text/csv' in response.content_type
        assert b'Student ID,Student Name' in response.data

    def test_analytics_with_filters(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test analytics page with assignment and date filtering."""
        mock_services['user_repo'].get_by_id.return_value = mock_instructor_user
        
        mock_assignment = Mock()
        mock_assignment.get_id.return_value = 1
        mock_assignment.title = "Test"
        mock_assignment.due_date = "2024-01-01"
        mock_services['assignment_repo'].get_all.return_value = [mock_assignment]
        
        from datetime import timedelta
        now = dt.now()
        
        # Multiple submissions with different dates and scores
        mock_sub1 = Mock()
        mock_sub1.get_assignment_id.return_value = 1
        mock_sub1.get_student_id.return_value = 10
        mock_sub1.score = 85
        mock_sub1.created_at = now - timedelta(days=2)
        
        mock_sub2 = Mock()
        mock_sub2.get_assignment_id.return_value = 1
        mock_sub2.get_student_id.return_value = 11
        mock_sub2.score = 45
        mock_sub2.created_at = now - timedelta(days=15) # month
        
        mock_services['submission_repo'].get_all.return_value = [mock_sub1, mock_sub2]
        
        # Test assignment filter
        response = client.get('/instructor/analytics?assignment=1')
        assert response.status_code == 200
        
        # Filter by invalid assignment ID should not crash (Lines 99-100)
        response = client.get('/instructor/analytics?assignment=abc')
        assert response.status_code == 200
        
        # Test date range filters
        for dr in ['week', 'month', 'semester', 'all', 'invalid']:
            response = client.get(f'/instructor/analytics?date_range={dr}')
            assert response.status_code == 200
            
        # Test malformed date to trigger exception handling (Lines 124-127)
        mock_sub_bad_date = Mock()
        mock_sub_bad_date.get_assignment_id.return_value = 1
        mock_sub_bad_date.get_student_id.return_value = 12
        mock_sub_bad_date.score = 50
        mock_sub_bad_date.created_at = "not-a-date"
        
        mock_sub_no_date = Mock()
        mock_sub_no_date.get_assignment_id.return_value = 1
        mock_sub_no_date.get_student_id.return_value = 13
        mock_sub_no_date.score = 50
        mock_sub_no_date.created_at = None # Line 127
        
        mock_services['submission_repo'].get_all.return_value.extend([mock_sub_bad_date, mock_sub_no_date])
        response = client.get('/instructor/analytics?date_range=week')
        assert response.status_code == 200
        
        # Test export with actual loop content
        response = client.get('/instructor/analytics/export')
        assert response.status_code == 200

    def test_dashboard_with_submissions(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test dashboard with pending and recent submissions."""
        mock_services['user_repo'].get_by_id.return_value = mock_instructor_user
        mock_services['instructor_service'].get_instructor.return_value = mock_instructor_user
        mock_services['course_repo'].list_by_instructor.return_value = []
        
        mock_ass = Mock()
        mock_ass.get_id.return_value = 1
        mock_ass.get_course_id.return_value = 1
        mock_ass.is_published = True
        mock_services['assignment_repo'].get_all.return_value = [mock_ass]
        mock_services['assignment_repo'].get_by_id.return_value = mock_ass
        
        mock_sub = Mock()
        mock_sub.get_id.return_value = "s1"
        mock_sub.get_student_id.return_value = 10
        mock_sub.get_assignment_id.return_value = 1
        mock_sub.status = 'pending'
        mock_sub.created_at = dt.now()
        mock_services['submission_repo'].get_all.return_value = [mock_sub]
        
        mock_services['flag_repo'].get_all.return_value = []
        mock_services['enrollment_repo'].get_all.return_value = []
        
        response = client.get('/instructor/dashboard')
        assert response.status_code == 200

    def test_plagiarism_dashboard_with_filters(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test plagiarism dashboard with severity and sort filters."""
        mock_services['user_repo'].get_by_id.return_value = mock_instructor_user
        
        mock_flag = Mock()
        mock_flag.get_id.return_value = "flag1"
        mock_flag.submission_id = 1
        mock_flag.similarity_score = 0.9 # High score
        mock_flag.is_dismissed = False
        
        mock_flag_low = Mock()
        mock_flag_low.get_id.return_value = "flag2"
        mock_flag_low.submission_id = 2
        mock_flag_low.similarity_score = 0.4 # Low score
        mock_flag_low.is_dismissed = False
        
        mock_flag_dismissed = Mock()
        mock_flag_dismissed.is_dismissed = True  # Line 273
        
        mock_services['flag_repo'].list_unreviewed.return_value = [mock_flag, mock_flag_low, mock_flag_dismissed]
        
        mock_sub = Mock()
        mock_sub.student_id = 10
        mock_services['submission_repo'].get_by_id.return_value = mock_sub
        
        # Test severity filters
        # Severity 'high' triggers score < 0.8 continue (Line 279) for flag2
        response = client.get('/instructor/plagiarism?severity=high')
        assert response.status_code == 200
        
        response = client.get('/instructor/plagiarism?severity=medium')
        assert response.status_code == 200
        
        response = client.get('/instructor/plagiarism?severity=low')
        assert response.status_code == 200
            
        # Test sorting
        response = client.get('/instructor/plagiarism?sort=score')
        assert response.status_code == 200

    def test_plagiarism_compare_and_review(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test plagiarism comparison and review actions."""
        mock_services['user_repo'].get_by_id.return_value = mock_instructor_user
        
        mock_flag = Mock()
        mock_flag.get_id.return_value = "flag1"
        mock_flag.submission_id = 1
        mock_flag.matched_submission_id = 2
        mock_flag.similarity_score = 0.95
        mock_services['flag_repo'].get_by_id.return_value = mock_flag
        
        # Test comparison page
        response = client.get('/instructor/plagiarism/compare/flag1')
        assert response.status_code == 200
        
        # Test non-existent flag
        mock_services['flag_repo'].get_by_id.return_value = None
        response = client.get('/instructor/plagiarism/compare/999')
        assert response.status_code == 302
        
        # Test review action (POST)
        mock_services['instructor_service'].review_similarity.return_value = mock_flag
        response = client.post('/instructor/plagiarism/review/flag1', data={
            'action': 'approve',
            'notes': 'Confirmed plagiarism'
        })
        assert response.status_code == 302
        mock_services['instructor_service'].review_similarity.assert_called()

    def test_plagiarism_review_error_flash(self, client, mock_services, instructor_session, mock_instructor_user):
        """Test that plagiarism review error is flashed."""
        mock_services['instructor_service'].review_similarity.side_effect = Exception("DB error")
        mock_services['flag_repo'].list_unreviewed.return_value = [] # Fix for redirect
        response = client.post('/instructor/plagiarism/review/flag1', data={
            'action': 'approve'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Error reviewing flag' in response.data
