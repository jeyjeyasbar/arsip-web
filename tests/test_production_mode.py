import os
import sys
from uuid import uuid4

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


def test_no_dev_tokens_in_production_register():
    """In production mode, registration should NOT return dev_verify_token."""
    app = create_app()
    app.config['ENVIRONMENT'] = 'production'
    client = app.test_client()
    email = f'prod_test_{uuid4().hex[:8]}@example.com'

    resp = client.post(
        '/api/auth/register',
        json={'name': 'Prod Test', 'email': email, 'password': 'secret123'},
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert 'access_token' not in data, 'Production must not issue access_token before verification'
    assert 'dev_verify_token' not in data, 'Production must not leak dev_verify_token'
    assert 'dev_verify_link' not in data, 'Production must not leak dev_verify_link'
    assert 'message' in data, 'Production must return message to check email'


def test_no_dev_tokens_in_production_forgot():
    """In production mode, forgot-password should NOT return dev_reset_token."""
    app = create_app()
    app.config['ENVIRONMENT'] = 'production'
    client = app.test_client()
    email = f'prod_test_{uuid4().hex[:8]}@example.com'

    # Create user first
    client.post(
        '/api/auth/register',
        json={'name': 'Prod Test', 'email': email, 'password': 'secret123'},
    )

    # Simulate SMTP failure (monkeypatch would do this in real test)
    # For now, just check that dev_reset_token is not returned
    resp = client.post('/api/auth/forgot-password', json={'email': email})

    assert resp.status_code == 200
    data = resp.get_json()
    assert 'dev_reset_token' not in data, 'Production must not leak dev_reset_token even if SMTP fails'
    assert 'message' in data, 'Production must return generic message'


def test_dev_tokens_returned_in_development():
    """In development mode, dev tokens should be returned for testing."""
    app = create_app()
    app.config['ENVIRONMENT'] = 'development'
    client = app.test_client()
    email = f'dev_test_{uuid4().hex[:8]}@example.com'

    resp = client.post(
        '/api/auth/register',
        json={'name': 'Dev Test', 'email': email, 'password': 'secret123'},
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert 'dev_verify_token' in data, 'Development should return dev_verify_token'
    assert 'dev_verify_link' in data, 'Development should return dev_verify_link'
    assert 'access_token' in data, 'Development should return access_token immediately'
