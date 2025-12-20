import pytest
import sqlite3
import json
from unittest.mock import Mock, patch
from flask import Flask, session
from core.entities.user import User

@pytest.fixture
def mock_services():
    return {
        'result_repo': Mock(),
        'user_repo': Mock(),
    }

@pytest.fixture
def app(mock_services):
    app = Flask(__name__)
    app.secret_key = 'test_secret'
    app.config['TESTING'] = True
    
    @app.context_processor
    def inject_current_user():
        if 'user_id' in session:
            user = mock_services['user_repo'].get_by_id(session['user_id'])
            return {'current_user': user}
        return {'current_user': None}
        
    app.extensions['services'] = mock_services
    
    from web.routes.result import result_bp
    app.register_blueprint(result_bp)
    
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

class TestResultRoutes:
    def test_results_for_submission_success(self, client, student_session, mock_services):
        mock_result = Mock()
        mock_result.get_id.return_value = 1
        mock_result.get_test_case_id.return_value = 101
        mock_result.passed = True
        mock_result.stdout = "Perfect"
        
        mock_services['result_repo'].find_by_submission.return_value = [mock_result]
        
        response = client.get('/results/submission/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['results']) == 1
        assert data['results'][0]['passed'] is True

    def test_results_for_submission_error(self, client, student_session, mock_services):
        mock_services['result_repo'].find_by_submission.side_effect = sqlite3.Error("DB error")
        response = client.get('/results/submission/1')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'DB error' in data['error']
