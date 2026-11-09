import json
import smtplib
import ssl
import urllib.request
from concurrent.futures import Future, ThreadPoolExecutor
from email.message import EmailMessage
from email.utils import parseaddr

from flask import Flask, current_app

SMTPS_PORT = 465
BREVO_URL = "https://api.brevo.com/v3/smtp/email"
_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="mail")


def _send_brevo(api_key: str, sender: str, to: str, subject: str, body: str) -> None:
    # Render's free tier blocks SMTP ports, so this sends over HTTPS instead.
    name, address = parseaddr(sender)
    payload = {
        "sender": {"name": name or address, "email": address},
        "to": [{"email": to}],
        "subject": subject,
        "textContent": body,
    }
    request = urllib.request.Request(  # noqa: S310 - fixed https URL
        BREVO_URL,
        data=json.dumps(payload).encode(),
        headers={
            "api-key": api_key,
            "content-type": "application/json",
            "accept": "application/json",
        },
        method="POST",
    )
    # urllib raises URLError/HTTPError (both OSError) on failure, which callers already handle.
    with urllib.request.urlopen(request, timeout=10):  # noqa: S310
        pass


def send_email(to: str, subject: str, body: str) -> None:
    cfg = current_app.config
    msg = EmailMessage()
    msg["From"] = cfg["MAIL_FROM"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    if cfg["BREVO_API_KEY"]:
        _send_brevo(cfg["BREVO_API_KEY"], cfg["MAIL_FROM"], to, subject, body)
        return
    if not cfg["MAIL_SERVER"]:
        current_app.logger.info(
            "Email (console backend)\nTo: %s\nSubject: %s\n\n%s", to, subject, body
        )
        return
    context = ssl.create_default_context()
    smtp: smtplib.SMTP
    if cfg["MAIL_PORT"] == SMTPS_PORT:
        smtp = smtplib.SMTP_SSL(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=10, context=context)
    else:
        smtp = smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=10)
    with smtp as conn:
        if cfg["MAIL_PORT"] != SMTPS_PORT:
            conn.starttls(context=context)
        if cfg["MAIL_USERNAME"]:
            conn.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
        conn.send_message(msg)


def _deliver(app: Flask, to: str, subject: str, body: str) -> None:
    with app.app_context():
        try:
            send_email(to, subject, body)
        except (smtplib.SMTPException, OSError):
            app.logger.exception("Could not send %r", subject)


def send_later(to: str, subject: str, body: str) -> Future[None] | None:
    """Send off the request path, so a slow mail service never holds up a page or webhook.

    A failure is logged, never raised: every caller treats email as best effort (#105).
    """
    app: Flask = current_app._get_current_object()  # type: ignore[attr-defined]
    if app.config["MAIL_ASYNC"]:
        return _pool.submit(_deliver, app, to, subject, body)
    _deliver(app, to, subject, body)
    return None
