import os
import smtplib
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.utils.emailer import send_reset_email


def test_send_reset_email_retries_with_ssl_on_gmail(monkeypatch):
    app = create_app()
    app.config['SMTP_HOST'] = 'smtp.gmail.com'
    app.config['SMTP_PORT'] = 587
    app.config['SMTP_USER'] = 'arsip.chici@gmail.com'
    app.config['SMTP_PASSWORD'] = 'secret'
    app.config['SMTP_FROM'] = 'arsip.chici@gmail.com'
    app.config['SMTP_TLS'] = True

    calls = []

    class DummySMTP:
        def __init__(self, host, port, timeout=None):
            calls.append(('smtp', host, port, timeout))
            if port == 587:
                raise TimeoutError('timed out')

    class DummySMTPSSL:
        def __init__(self, host, port, timeout=None):
            calls.append(('smtp_ssl', host, port, timeout))
            self.host = host
            self.port = port

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def login(self, user, password):
            calls.append(('login', user, password))

        def send_message(self, msg):
            calls.append(('send', msg['To']))

    monkeypatch.setattr(smtplib, 'SMTP', DummySMTP)
    monkeypatch.setattr(smtplib, 'SMTP_SSL', DummySMTPSSL)

    with app.app_context():
        sent = send_reset_email('user@example.com', 'User', 'https://example.com/reset')

    assert sent is True
    assert ('smtp', 'smtp.gmail.com', 587, 20) in calls
    assert ('smtp_ssl', 'smtp.gmail.com', 465, 20) in calls
