import pytest
import os
import json
from unittest.mock import Mock, patch
from flask import Flask, session
from core.entities.user import User

@pytest.fixture
def mock_services():
    return {
        'user_repo': Mock(),
        'assignment_repo': Mock(),
        'test_case_service': Mock(),
        'sandbox_service': Mock(),
        'draft_service': Mock(),
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
    
    from web.routes.api import api_bp
    app.register_blueprint(api_bp)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user_session(client, mock_services):
    mock_user = User(1, "User", "u@t.com", "p", "student")
    mock_services['user_repo'].get_by_id.return_value = mock_user
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'student'
    return mock_user

class TestApiRoutes:
    def test_test_code_no_assignment(self, client, user_session, mock_services):
        mock_services['assignment_repo'].get_by_id.return_value = None
        response = client.post('/api/test-code', 
                               data=json.dumps({'code': 'print(1)', 'assignment_id': 99}),
                               content_type='application/json')
        assert response.status_code == 404
        assert b'Assignment not found' in response.data

    def test_test_code_dry_run_success(self, client, user_session, mock_services):
        mock_services['assignment_repo'].get_by_id.return_value = Mock()
        mock_services['test_case_service'].list_test_cases.return_value = []
        mock_services['sandbox_service'].execute_code.return_value = {
            'success': True,
            'stdout': 'output',
            'stderr': '',
            'runtime_ms': 10
        }
        mock_services['sandbox_service'].groq_client = None
        
        response = client.post('/api/test-code', 
                               data=json.dumps({'code': 'print(1)', 'assignment_id': 1}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['score'] == 100

    def test_test_code_dry_run_failure_with_ai(self, client, user_session, mock_services):
        mock_services['assignment_repo'].get_by_id.return_value = Mock()
        mock_services['test_case_service'].list_test_cases.return_value = []
        mock_services['sandbox_service'].execute_code.return_value = {
            'success': False,
            'stdout': '',
            'stderr': 'SyntaxError',
            'runtime_ms': 5
        }
        mock_services['sandbox_service'].groq_client = Mock()
        mock_services['sandbox_service'].get_ai_feedback.return_value = "Try fixing your bracket"
        
        response = client.post('/api/test-code', 
                               data=json.dumps({'code': 'print(1', 'assignment_id': 1}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ai_feedback'] == "Try fixing your bracket"

    def test_test_code_with_test_cases(self, client, user_session, mock_services):
        mock_services['assignment_repo'].get_by_id.return_value = Mock()
        tc = Mock()
        tc.name = "Test 1"
        mock_services['test_case_service'].list_test_cases.return_value = [tc]
        mock_services['sandbox_service'].run_all_tests.return_value = {
            'results': [{
                'test_name': 'Test 1',
                'passed': True,
                'stdout': 'out',
                'expected_output': 'out',
                'actual_output': 'out',
                'runtime_ms': 10,
                'timed_out': False
            }]
        }
        mock_services['sandbox_service'].groq_client = None
        
        response = client.post('/api/test-code', 
                               data=json.dumps({'code': 'print(1)', 'assignment_id': 1}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['passed_count'] == 1
        assert data['score'] == 100

    def test_test_code_exception(self, client, user_session, mock_services):
        mock_services['assignment_repo'].get_by_id.return_value = Mock()
        mock_services['test_case_service'].list_test_cases.side_effect = Exception("DB error")
        response = client.post('/api/test-code', 
                               data=json.dumps({'code': 'print(1)', 'assignment_id': 1}),
                               content_type='application/json')
        assert response.status_code == 400
        assert b'DB error' in response.data

    def test_get_test_cases_success(self, client, user_session, mock_services):
        tc = Mock()
        tc.name = "Name"
        tc.description = "Desc"
        tc.stdin = "in"
        tc.expected_out = "out"
        tc.points = 10
        mock_services['test_case_service'].list_test_cases.return_value = [tc]
        
        response = client.get('/api/assignment/1/test-cases')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['test_cases']) == 1
        assert data['test_cases'][0]['name'] == "Name"

    def test_get_hint_success(self, client, user_session, mock_services):
        mock_services['sandbox_service'].groq_client = Mock()
        mock_services['sandbox_service'].get_ai_feedback.return_value = "Hint text"
        
        response = client.post('/api/hint', 
                               data=json.dumps({'code': 'xxx', 'error': 'err'}),
                               content_type='application/json')
        assert response.status_code == 200
        assert json.loads(response.data)['hint'] == "Hint text"

    def test_get_hint_no_groq(self, client, user_session, mock_services):
        mock_services['sandbox_service'].groq_client = None
        response = client.post('/api/hint', 
                               data=json.dumps({'code': 'xxx'}),
                               content_type='application/json')
        assert response.status_code == 503

    def test_get_languages(self, client):
        response = client.get('/api/languages')
        assert response.status_code == 200
        assert b'python' in response.data

    def test_get_draft_not_found(self, client, user_session, mock_services):
        mock_services['draft_service'].get_latest_draft.return_value = None
        response = client.get('/api/drafts?assignment_id=1')
        assert json.loads(response.data)['draft'] is None

    def test_get_draft_success(self, client, user_session, mock_services):
        mock_draft = Mock()
        mock_draft.to_dict.return_value = {'content': 'some code'}
        mock_services['draft_service'].get_latest_draft.return_value = mock_draft
        response = client.get('/api/drafts?assignment_id=1')
        assert json.loads(response.data)['draft']['content'] == 'some code'

    def test_save_draft_success(self, client, user_session, mock_services):
        mock_draft = Mock()
        mock_draft.to_dict.return_value = {'id': 1}
        mock_services['draft_service'].save_draft.return_value = mock_draft
        response = client.post('/api/drafts', 
                               data=json.dumps({'assignment_id': 1, 'content': 'code'}),
                               content_type='application/json')
        assert response.status_code == 200
        assert json.loads(response.data)['draft']['id'] == 1

    def test_test_code_with_test_cases_ai_feedback(self, client, user_session, mock_services):
        mock_services['assignment_repo'].get_by_id.return_value = Mock()
        tc = Mock()
        tc.name = "Test 1"
        mock_services['test_case_service'].list_test_cases.return_value = [tc]
        mock_services['sandbox_service'].run_all_tests.return_value = {
            'results': [{
                'test_name': 'Test 1',
                'passed': False,
                'stdout': '',
                'stderr': 'Some error',
                'expected_output': 'out',
                'actual_output': 'err',
                'runtime_ms': 10,
                'timed_out': False
            }]
        }
        mock_services['sandbox_service'].groq_client = Mock()
        mock_services['sandbox_service'].get_ai_feedback.return_value = "AI feedback"
        
        response = client.post('/api/test-code', 
                               data=json.dumps({'code': 'print(1)', 'assignment_id': 1}),
                               content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['ai_feedback'] == "AI feedback"

    def test_get_test_cases_exception(self, client, user_session, mock_services):
        mock_services['test_case_service'].list_test_cases.side_effect = Exception("error")
        response = client.get('/api/assignment/1/test-cases')
        assert response.status_code == 400

    def test_get_hint_exception(self, client, user_session, mock_services):
        mock_services['sandbox_service'].groq_client = Mock()
        mock_services['sandbox_service'].get_ai_feedback.side_effect = Exception("AI error")
        response = client.post('/api/hint', 
                               data=json.dumps({'code': 'x', 'error': 'e'}),
                               content_type='application/json')
        assert response.status_code == 500

    def test_get_draft_no_id(self, client, user_session, mock_services):
        response = client.get('/api/drafts')
        assert response.status_code == 400

    def test_save_draft_storage_error(self, client, user_session, mock_services):
        mock_services['draft_service'].save_draft.return_value = None
        response = client.post('/api/drafts', 
                               data=json.dumps({'assignment_id': 1, 'content': 'code'}),
                               content_type='application/json')
        assert response.status_code == 500
        assert b'storage error' in response.data

    def test_save_draft_exception(self, client, user_session, mock_services):
        mock_services['draft_service'].save_draft.side_effect = Exception("DB fail")
        response = client.post('/api/drafts', 
                               data=json.dumps({'assignment_id': 1, 'content': 'code'}),
                               content_type='application/json')
        assert response.status_code == 500
        assert b'DB fail' in response.data

    def test_save_draft_no_id(self, client, user_session, mock_services):
        response = client.post('/api/drafts', data=json.dumps({}), content_type='application/json')
        assert response.status_code == 400

    def test_test_code_malformed_json(self, client, user_session, mock_services):
        response = client.post('/api/test-code', 
                               data="not a json",
                               content_type='application/json')
        assert response.status_code == 400 # Flask handles bad JSON

    def test_test_code_missing_id(self, client, user_session, mock_services):
        mock_services['assignment_repo'].get_by_id.return_value = None
        response = client.post('/api/test-code', 
                               data=json.dumps({'code': 'print(1)'}),
                               content_type='application/json')
        # Line 27 in api.py: if not assignment -> 404
        assert response.status_code == 404

    def test_get_hint_empty_payload(self, client, user_session, mock_services):
        # api.py line 136-138 handles missing keys via data.get('', '')
        response = client.post('/api/hint', 
                               data=json.dumps({}),
                               content_type='application/json')
        # If groq is not mocked as None, it tries to proceed
        mock_services['sandbox_service'].groq_client = Mock()
        mock_services['sandbox_service'].get_ai_feedback.return_value = "Hint"
        response = client.post('/api/hint', 
                               data=json.dumps({}),
                               content_type='application/json')
        assert response.status_code == 200
        assert json.loads(response.data)['hint'] == "Hint"

    def test_save_draft_malformed_types(self, client, user_session, mock_services):
        # Passing string instead of int for assignment_id
        response = client.post('/api/drafts', 
                               data=json.dumps({'assignment_id': 'abc'}),
                               content_type='application/json')
        # api.py line 204: int(assignment_id) -> raises ValueError
        # caught by Exception block line 208 -> returns 500
        assert response.status_code == 500
        assert b'invalid literal for int()' in response.data.lower()
