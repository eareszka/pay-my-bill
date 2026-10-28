import logging
from unittest.mock import MagicMock

import pytest
from flask import Flask

from app.mail import send_email


def test_console_backend_logs(app: Flask, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO):
        send_email("a@example.com", "Hello", "Body text")
    assert "Subject: Hello" in caplog.text
    assert "Body text" in caplog.text


@pytest.mark.parametrize("username", ["", "mailer"])
def test_smtp_backend_sends(app: Flask, monkeypatch: pytest.MonkeyPatch, username: str) -> None:
    smtp = MagicMock()
    monkeypatch.setattr("app.mail.smtplib.SMTP", smtp)
    app.config.update(MAIL_SERVER="smtp.example.com", MAIL_USERNAME=username)
    send_email("a@example.com", "Hello", "Body")
    smtp.assert_called_once_with("smtp.example.com", 587, timeout=10)
    conn = smtp.return_value.__enter__.return_value
    conn.starttls.assert_called_once()
    assert conn.login.called is bool(username)
    sent = conn.send_message.call_args.args[0]
    assert sent["To"] == "a@example.com"
