import re
import smtplib
from datetime import timedelta
from unittest.mock import patch

import pytest
from flask.testing import FlaskClient
from werkzeug.security import check_password_hash

from app.extensions import db
from app.models import LoginAttempt, utcnow
from app.tokens import RESET_PASSWORD, make_token
from tests.conftest import PASSWORD, MakeUser

NEW = "brand-new-pass"


def reset_link(caplog: pytest.LogCaptureFixture) -> str:
    match = re.search(r"http://localhost(/reset/\S+)", caplog.text)
    assert match is not None
    return match.group(1)


def test_login_links_to_reset(client: FlaskClient) -> None:
    assert b'href="/reset"' in client.get("/login").data
    assert client.get("/reset").status_code == 200


def test_same_reply_whether_or_not_the_account_exists(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    make_user("alice")
    known = client.post("/reset", data={"email": "alice@example.com"}, follow_redirects=True)
    unknown = client.post("/reset", data={"email": "nobody@example.com"}, follow_redirects=True)
    assert known.status_code == unknown.status_code == 200
    assert b"If an account uses that email" in known.data
    assert b"If an account uses that email" in unknown.data
    assert b"Check your spam or junk folder" in known.data
    assert caplog.text.count("Reset your Pay My Bill password") == 1


def test_invalid_email_shows_form_error(client: FlaskClient) -> None:
    resp = client.post("/reset", data={"email": "not-an-email"})
    assert resp.status_code == 200
    assert b"Enter a valid email address." in resp.data


def test_link_sets_new_password_once_and_notifies(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    user = make_user("alice", verified=False)
    client.post("/reset", data={"email": "alice@example.com"})
    link = reset_link(caplog)
    assert b"Choose a new password" in client.get(link).data

    resp = client.post(link, data={"password": NEW, "confirm": NEW})
    assert resp.status_code == 302
    assert resp.location.endswith("/login")
    db.session.refresh(user)
    assert check_password_hash(user.password_hash, NEW)
    assert not check_password_hash(user.password_hash, PASSWORD)
    assert user.is_verified
    assert "Your Pay My Bill password changed" in caplog.text

    reused = client.get(link)
    assert reused.status_code == 302
    assert reused.location.endswith("/reset")

    login = client.post("/login", data={"identifier": "alice", "password": NEW})
    assert login.status_code == 302


def test_mismatched_passwords_are_refused(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    make_user("alice")
    client.post("/reset", data={"email": "alice@example.com"})
    resp = client.post(reset_link(caplog), data={"password": NEW, "confirm": "other-pass"})
    assert resp.status_code == 200
    assert b"Passwords must match." in resp.data


def test_expired_link_is_refused(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user("alice")
    token = make_token(user.id, user.password_hash, RESET_PASSWORD)
    later = utcnow() + timedelta(hours=2)
    with patch("itsdangerous.timed.time.time", return_value=later.timestamp()):
        resp = client.get(f"/reset/{token}", follow_redirects=True)
    assert b"invalid, expired, or already used" in resp.data


def test_garbage_and_deleted_accounts_are_refused(client: FlaskClient, make_user: MakeUser) -> None:
    assert client.get("/reset/garbage").status_code == 302
    user = make_user("gone")
    user.email = "x@deleted.invalid"
    db.session.commit()
    token = make_token(user.id, user.password_hash, RESET_PASSWORD)
    assert client.get(f"/reset/{token}").location.endswith("/reset")
    client.post("/reset", data={"email": "x@deleted.invalid"})


def test_requests_are_rate_limited(client: FlaskClient) -> None:
    for _ in range(6):
        client.post("/reset", data={"email": "a@example.com"})
    resp = client.post("/reset", data={"email": "a@example.com"})
    assert resp.status_code == 429
    assert "Retry-After" in resp.headers


def test_reset_clears_a_login_lockout(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    make_user("alice")
    for _ in range(7):
        client.post("/login", data={"identifier": "alice", "password": "wrong-guess"})
    assert (
        client.post("/login", data={"identifier": "alice", "password": PASSWORD}).status_code == 429
    )
    client.post("/reset", data={"email": "alice@example.com"})
    client.post(reset_link(caplog), data={"password": NEW, "confirm": NEW})
    assert db.session.query(LoginAttempt).filter_by(succeeded=True).count() == 1
    assert client.post("/login", data={"identifier": "alice", "password": NEW}).status_code == 302


def test_mail_failure_keeps_the_same_reply(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("alice")
    with patch("app.routes.auth.send_email", side_effect=smtplib.SMTPException("down")):
        resp = client.post("/reset", data={"email": "alice@example.com"}, follow_redirects=True)
    assert b"If an account uses that email" in resp.data
