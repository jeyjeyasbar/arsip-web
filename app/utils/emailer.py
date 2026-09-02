import smtplib
from email.message import EmailMessage
from flask import current_app


def _send_with_smtp(cfg, msg):
    host = cfg['SMTP_HOST']
    port = cfg['SMTP_PORT']
    try:
        with smtplib.SMTP(host, port, timeout=20) as s:
            if cfg['SMTP_TLS']:
                s.starttls()
            s.login(cfg['SMTP_USER'], cfg['SMTP_PASSWORD'])
            s.send_message(msg)
        return True
    except Exception:
        if host and port == 587:
            try:
                with smtplib.SMTP_SSL(host, 465, timeout=20) as s:
                    s.login(cfg['SMTP_USER'], cfg['SMTP_PASSWORD'])
                    s.send_message(msg)
                return True
            except Exception:
                raise
        raise


def send_reset_email(to_email, name, link):
    cfg = current_app.config
    if not cfg['SMTP_HOST'] or not cfg['SMTP_USER'] or not cfg['SMTP_PASSWORD']:
        return False
    msg = EmailMessage()
    msg['Subject'] = 'Reset Kata Sandi ARSIP!'
    msg['From'] = cfg['SMTP_FROM']
    msg['To'] = to_email
    msg.set_content(
        f'Halo {name},\n\nGunakan tautan berikut untuk mengatur ulang kata sandi ARSIP!:\n{link}\n\nTautan berlaku 30 menit.'
    )
    return _send_with_smtp(cfg, msg)
