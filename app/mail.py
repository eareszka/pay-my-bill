import smtplib
import ssl
from email.message import EmailMessage

from flask import current_app

SMTPS_PORT = 465


def send_email(to: str, subject: str, body: str) -> None:
    cfg = current_app.config
    msg = EmailMessage()
    msg["From"] = cfg["MAIL_FROM"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
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
