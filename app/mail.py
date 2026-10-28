import smtplib
from email.message import EmailMessage

from flask import current_app


def send_email(to: str, subject: str, body: str) -> None:
    cfg = current_app.config
    msg = EmailMessage()
    msg["From"] = cfg["MAIL_FROM"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    if not cfg["MAIL_SERVER"]:
        current_app.logger.info("Email (console backend)\n%s", msg)
        return
    with smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=10) as smtp:
        smtp.starttls()
        if cfg["MAIL_USERNAME"]:
            smtp.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
        smtp.send_message(msg)
