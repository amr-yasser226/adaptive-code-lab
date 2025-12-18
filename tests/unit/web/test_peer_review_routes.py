import pytest
import os
from flask import Flask, session
from unittest.mock import Mock


@pytest.fixture
def mock_services():
    """Create mock services."""
    services = {
        'user_repo': Mock(),
        'peer_review_service': Mock(),
    }
    
    mock_user = Mock()
    mock_user.get_id.return_value = 1
    mock_user.name = "Test User"
    mock_user.role = "student"
    services['user_repo'].get_by_id.return_value = mock_user
    
    mock_review = Mock()
    mock_review.get_id.return_value = 1
    mock_review.feedback = "Good work!"
    mock_review.score = 85
    services['peer_review_service'].get_reviews_for_submission.return_value = [mock_review]
    services['peer_review_service'].get_pending_reviews.return_value = []
    
    return services


@pytest.fixture
def app(mock_services):
    """Create Flask test app."""
    template_dir = os.path.join(os.path.dirname(__file__), '../../../src/web/templates')
    
    app = Flask(__name__, template_folder=os.path.abspath(template_dir))
    app.secret_key = 'test_secret'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    def format_date(value, fmt='%b %d, %Y'):
        return value if isinstance(value, str) else 'N/A'
    
    app.jinja_env.filters['format_date'] = format_date
    
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=lambda: 'test-token')
    
    @app.context_processor
    def inject_current_user():
        user_id = session.get('user_id')
        if user_id:
            return dict(current_user=mock_services['user_repo'].get_by_id(user_id))
        return dict(current_user=None)
    
    app.extensions['services'] = mock_services
    
    from web.routes.peer_review import peer_review_bp
    from web.routes.auth import auth_bp
    
    @app.route('/')
    def index():
        return 'Home'
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(peer_review_bp)
    
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_session(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'student'
    return client


@pytest.mark.unit
class TestPeerReviewRoutes:
    
    def test_create_review_requires_login(self, client):
        """Test creating review requires login."""
        response = client.post('/peer-review/create/1')
        assert response.status_code in [302, 401]
    
    def test_update_review_requires_login(self, client):
        """Test updating review requires login."""
        response = client.post('/peer-review/update/1')
        assert response.status_code in [302, 401]
    
    def test_submit_review_requires_login(self, client):
        """Test submitting review requires login."""
        response = client.post('/peer-review/submit/1')
        assert response.status_code in [302, 401]
    
    def test_list_reviews_for_submission_requires_login(self, client):
        """Test listing reviews for submission requires login."""
        response = client.get('/peer-review/submission/1')
        assert response.status_code in [302, 401]
