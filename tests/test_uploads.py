import os
import sys
from io import BytesIO
from uuid import uuid4

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


def test_valid_pdf_upload_succeeds():
    app = create_app()
    client = app.test_client()
    email = f'upload_{uuid4().hex[:8]}@example.com'

    register = client.post(
        '/api/auth/register',
        json={'name': 'Upload User', 'email': email, 'password': 'secret123'},
    )
    assert register.status_code == 200
    token = register.get_json()['access_token']
    headers = {'Authorization': 'Bearer ' + token}

    pdf = b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF'
    resp = client.post('/api/files', data={'file': (BytesIO(pdf), 'test.pdf')}, headers=headers)

    assert resp.status_code == 201, resp.get_data(as_text=True)
    assert resp.get_json()['file_name'] == 'test.pdf'

    document = client.post(
        '/api/documents',
        json={
            'name': 'KTP',
            'category': 'Identitas',
            'date': '2026-09-02',
            'description': 'Scan dokumen',
            'file_path': resp.get_json()['file_path'],
            'file_name': 'test.pdf',
        },
        headers=headers,
    )

    assert document.status_code == 201, document.get_data(as_text=True)
    assert document.get_json()['item']['file_name'] == 'test.pdf'


def test_pdf_with_leading_bytes_still_accepted():
    app = create_app()
    client = app.test_client()
    email = f'upload_{uuid4().hex[:8]}@example.com'

    register = client.post(
        '/api/auth/register',
        json={'name': 'Upload User', 'email': email, 'password': 'secret123'},
    )
    assert register.status_code == 200
    token = register.get_json()['access_token']
    headers = {'Authorization': 'Bearer ' + token}

    pdf = b'\x00\x00\x00%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF'
    resp = client.post('/api/files', data={'file': (BytesIO(pdf), 'leading.pdf')}, headers=headers)

    assert resp.status_code == 201, resp.get_data(as_text=True)
    assert resp.get_json()['file_name'] == 'leading.pdf'


def test_file_download_requires_auth():
    app = create_app()
    owner_client = app.test_client()
    attacker_client = app.test_client()
    email = f'upload_{uuid4().hex[:8]}@example.com'

    register = owner_client.post(
        '/api/auth/register',
        json={'name': 'Upload User', 'email': email, 'password': 'secret123'},
    )
    assert register.status_code == 200
    token = register.get_json()['access_token']
    headers = {'Authorization': 'Bearer ' + token}

    pdf = b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF'
    resp = owner_client.post('/api/files', data={'file': (BytesIO(pdf), 'secure.pdf')}, headers=headers)
    assert resp.status_code == 201

    path = resp.get_json()['file_path']
    noauth = attacker_client.get(path)
    assert noauth.status_code == 401, noauth.get_data(as_text=True)

    auth = owner_client.get(path, headers={'Authorization': 'Bearer ' + token})
    assert auth.status_code == 200


def test_email_verification_required_before_login():
    app = create_app()
    client = app.test_client()
    email = f'verify_{uuid4().hex[:8]}@example.com'

    register = client.post(
        '/api/auth/register',
        json={'name': 'Verify User', 'email': email, 'password': 'secret123'},
    )
    assert register.status_code == 200
    assert 'dev_verify_token' in register.get_json()

    login = client.post('/api/auth/login', json={'email': email, 'password': 'secret123'})
    assert login.status_code == 403, login.get_data(as_text=True)

    token = register.get_json()['dev_verify_token']
    verify = client.post('/api/auth/verify-email', json={'token': token})
    assert verify.status_code == 200, verify.get_data(as_text=True)

    login_after = client.post('/api/auth/login', json={'email': email, 'password': 'secret123'})
    assert login_after.status_code == 200, login_after.get_data(as_text=True)
