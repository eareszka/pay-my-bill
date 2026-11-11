import re
import smtplib
from datetime import timedelta
from unittest.mock import patch

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import check_password_hash

from app.extensions import db
from app.models import LoginAttempt, User, utcnow
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
    with patch("app.mail.send_email", side_effect=smtplib.SMTPException("down")):
        resp = client.post("/reset", data={"email": "alice@example.com"}, follow_redirects=True)
    assert b"If an account uses that email" in resp.data


def test_reset_ends_sessions_from_before_it(
    app: Flask, client: FlaskClient, caplog: pytest.LogCaptureFixture
) -> None:
    # Someone signs up with alice's email and stays logged in (#130).
    squatter = app.test_client()
    squatter.post(
        "/signup",
        data={
            "username": "squatter",
            "email": "alice@example.com",
            "password": PASSWORD,
            "confirm": PASSWORD,
            "adult": "y",
            "rules": "y",
        },
    )
    user = db.session.query(User).filter_by(email="alice@example.com").one()
    assert squatter.get("/profile").status_code == 200

    # Alice claims the account through her inbox.
    client.post("/reset", data={"email": "alice@example.com"})
    client.post(reset_link(caplog), data={"password": NEW, "confirm": NEW})
    db.session.refresh(user)
    assert user.is_verified

    resp = squatter.get("/profile")
    assert resp.status_code == 302
    assert "/login" in resp.location
    assert (
        client.post("/login", data={"identifier": "alice@example.com", "password": NEW}).status_code
        == 302
    )
    assert client.get("/profile").status_code == 200


def test_session_without_current_version_is_anonymous(
    client: FlaskClient, make_user: MakeUser
) -> None:
    user = make_user("alice")
    for stale in (str(user.id), f"{user.id}:{user.session_version + 1}", f"{user.id}:"):
        with client.session_transaction() as session:
            session["_user_id"] = stale
        assert client.get("/profile").status_code == 302


def test_claiming_an_unverified_account_clears_its_handles(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    # Set up by someone else before the email's owner claimed it (#133).
    user = make_user(
        "alice",
        verified=False,
        venmo_handle="squatter",
        cashapp_handle="squatter",
        paypal_handle="squatter",
        city="Madison",
        state="WI",
    )
    client.post("/reset", data={"email": "alice@example.com"})
    resp = client.post(
        reset_link(caplog), data={"password": NEW, "confirm": NEW}, follow_redirects=True
    )
    assert b"we cleared its payment handles and city" in resp.data
    db.session.refresh(user)
    assert user.is_verified
    assert (user.cashapp_handle, user.venmo_handle, user.paypal_handle) == (None, None, None)
    assert (user.city, user.state) == (None, None)


def test_claiming_a_bare_unverified_account_says_nothing_extra(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    make_user("alice", verified=False)
    client.post("/reset", data={"email": "alice@example.com"})
    resp = client.post(
        reset_link(caplog), data={"password": NEW, "confirm": NEW}, follow_redirects=True
    )
    assert b"Your password is changed" in resp.data
    assert b"we cleared" not in resp.data


def test_reset_keeps_a_verified_accounts_handles(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    user = make_user("alice", venmo_handle="alice-v", city="Madison", state="WI")
    client.post("/reset", data={"email": "alice@example.com"})
    resp = client.post(
        reset_link(caplog), data={"password": NEW, "confirm": NEW}, follow_redirects=True
    )
    assert b"we cleared" not in resp.data
    db.session.refresh(user)
    assert (user.venmo_handle, user.city, user.state) == ("alice-v", "Madison", "WI")
