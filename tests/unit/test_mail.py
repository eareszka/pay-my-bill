import logging
import ssl
from unittest.mock import MagicMock

import pytest
from flask import Flask

from app.mail import send_email


def test_console_backend_logs(app: Flask, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        send_email("a@example.com", "Hello", "Body text")
    assert "Subject: Hello" in caplog.text
    assert "To: a@example.com" in caplog.text
    assert "Body text" in caplog.text


@pytest.mark.parametrize("username", ["", "mailer"])
def test_smtp_backend_sends(app: Flask, monkeypatch: pytest.MonkeyPatch, username: str) -> None:
    smtp = MagicMock()
    monkeypatch.setattr("app.mail.smtplib.SMTP", smtp)
    app.config.update(MAIL_SERVER="smtp.example.com", MAIL_USERNAME=username)
    send_email("a@example.com", "Hello", "Body")
    smtp.assert_called_once_with("smtp.example.com", 587, timeout=10)
    conn = smtp.return_value.__enter__.return_value
    assert conn.starttls.call_args.kwargs["context"].verify_mode == ssl.CERT_REQUIRED
    assert conn.login.called is bool(username)
    sent = conn.send_message.call_args.args[0]
    assert sent["To"] == "a@example.com"


def test_smtps_port_uses_implicit_tls(app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
    smtp_ssl = MagicMock()
    monkeypatch.setattr("app.mail.smtplib.SMTP_SSL", smtp_ssl)
    app.config.update(MAIL_SERVER="smtp.example.com", MAIL_PORT=465)
    send_email("a@example.com", "Hello", "Body")
    assert smtp_ssl.call_args.args == ("smtp.example.com", 465)
    conn = smtp_ssl.return_value.__enter__.return_value
    conn.starttls.assert_not_called()
    conn.send_message.assert_called_once()


def test_app_logger_emits_info(app: Flask) -> None:
    assert app.logger.isEnabledFor(logging.INFO)
