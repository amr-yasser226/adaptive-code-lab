import pytest
from flask import Flask
from unittest.mock import Mock


@pytest.fixture
def mock_services():
    services = {
        'user_repo': Mock(),
        'draft_service': Mock(),
    }

    mock_user = Mock()
    mock_user.get_id.return_value = 1
    mock_user.name = 'Student'
    mock_user.role = 'student'
    services['user_repo'].get_by_id.return_value = mock_user

    return services


@pytest.fixture
def app(mock_services):
    app = Flask(__name__)
    app.secret_key = 'test'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.extensions['services'] = mock_services

    from web.routes.api import api_bp
    app.register_blueprint(api_bp)
    return app


def test_save_draft_requires_authentication(client=None):
    # use a fresh Flask app client without session
    from flask import Flask
    app = Flask(__name__)
    app.secret_key = 's'
    app.config['TESTING'] = True
    from web.routes.api import api_bp
    app.register_blueprint(api_bp)
    c = app.test_client()
    resp = c.post('/api/drafts', json={'assignment_id': 1, 'content': 'x'})
    assert resp.status_code in (302, 401)


def test_save_and_get_draft_authenticated(app):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'student'

    # Configure draft_service mock
    svc = app.extensions['services']['draft_service']
    svc.save_draft.return_value = Mock(to_dict=lambda: {'id': 1, 'content': 'hello'})
    svc.get_latest_draft.return_value = Mock(to_dict=lambda: {'id': 1, 'content': 'hello'})

    resp = client.post('/api/drafts', json={'assignment_id': 2, 'content': 'hello'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True

    resp2 = client.get('/api/drafts?assignment_id=2')
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert data2['success'] is True
