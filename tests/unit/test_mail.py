import json
import logging
import ssl
import urllib.error
from unittest.mock import MagicMock

import pytest
from flask import Flask

from app.mail import send_email, send_later


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


def test_brevo_backend_posts_json(app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen = MagicMock()
    monkeypatch.setattr("app.mail.urllib.request.urlopen", urlopen)
    app.config.update(
        BREVO_API_KEY="key-123", MAIL_FROM="Pay My Bill <hi@example.com>", MAIL_SERVER="smtp.x"
    )
    send_email("a@example.com", "Hello", "Body")
    request = urlopen.call_args.args[0]
    assert request.full_url == "https://api.brevo.com/v3/smtp/email"
    assert request.get_header("Api-key") == "key-123"
    payload = json.loads(request.data)
    assert payload["sender"] == {"name": "Pay My Bill", "email": "hi@example.com"}
    assert payload["to"] == [{"email": "a@example.com"}]
    assert (payload["subject"], payload["textContent"]) == ("Hello", "Body")


def test_brevo_bare_sender_and_errors_are_oserror(
    app: Flask, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*_: object, **__: object) -> None:
        raise urllib.error.URLError("down")

    monkeypatch.setattr("app.mail.urllib.request.urlopen", fail)
    app.config.update(BREVO_API_KEY="key", MAIL_FROM="hi@example.com")
    with pytest.raises(OSError):
        send_email("a@example.com", "Hello", "Body")


def test_send_later_runs_in_the_background(app: Flask, caplog: pytest.LogCaptureFixture) -> None:
    app.config["MAIL_ASYNC"] = True
    caplog.set_level(logging.INFO)
    with app.app_context():
        future = send_later("a@example.com", "Hello", "Body")
    assert future is not None
    future.result(timeout=5)
    assert "Subject: Hello" in caplog.text


def test_send_later_logs_failures(
    app: Flask, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def fail(*_: object) -> None:
        raise KeyError("MAIL_FROM")  # not a mail error, still logged

    monkeypatch.setattr("app.mail.send_email", fail)
    app.config["MAIL_ASYNC"] = True
    with app.app_context():
        future = send_later("a@example.com", "Hello", "Body")
    assert future is not None
    future.result(timeout=5)
    assert "Could not send 'Hello'" in caplog.text
