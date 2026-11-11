import logging
import re
import smtplib
from datetime import timedelta

import pytest
from flask import Flask, g
from flask.testing import FlaskClient
from sqlalchemy import func, select, update
from werkzeug.security import check_password_hash

from app import create_app
from app.auth import MAX_SIGNUPS_PER_IP, SIGNUP_WINDOW, verified_required
from app.extensions import db
from app.models import LoginAttempt, User, as_utc, utcnow
from app.tokens import VERIFY_EMAIL, make_token
from tests.conftest import PASSWORD, MakeUser, login_as

FORM = {
    "username": "New_User",
    "email": "New@Example.com",
    "password": "s3cret-pass",
    "confirm": "s3cret-pass",
    "adult": "y",
}


def user_count() -> int:
    return db.session.scalar(select(func.count()).select_from(User)) or 0


def test_signup_page_renders(client: FlaskClient) -> None:
    resp = client.get("/signup")
    assert resp.status_code == 200
    assert b"Create your account" in resp.data


def test_signup_creates_hashed_user_and_sends_verification(
    client: FlaskClient, caplog: pytest.LogCaptureFixture
) -> None:
    resp = client.post("/signup", data=FORM)
    assert resp.status_code == 302
    assert resp.location.endswith("/verify/pending")
    user = db.session.scalars(select(User)).one()
    assert (user.username, user.email) == ("new_user", "new@example.com")
    assert user.password_hash != FORM["password"]
    assert check_password_hash(user.password_hash, FORM["password"])
    assert not user.is_verified
    assert "Verify your Pay My Bill email" in caplog.text
    link = re.search(r"http://localhost/verify/\S+", caplog.text)
    assert link is not None

    resp = client.get(link.group(0))
    assert resp.status_code == 302
    db.session.refresh(user)
    assert user.is_verified


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("username", "alice", b"That username is taken."),
        ("email", "ALICE@example.com", b"An account with that email already exists."),
    ],
)
def test_signup_duplicate_rejected(
    client: FlaskClient, make_user: MakeUser, field: str, value: str, message: bytes
) -> None:
    make_user("alice")
    resp = client.post("/signup", data={**FORM, field: value})
    assert resp.status_code == 200
    assert message in resp.data
    assert user_count() == 1


@pytest.mark.parametrize(
    "overrides",
    [
        {"username": "ab"},
        {"username": "bad name!"},
        {"email": "not-an-email"},
        {"password": "short", "confirm": "short"},
        {"confirm": "different-pass"},
    ],
)
def test_signup_invalid_input_rejected(client: FlaskClient, overrides: dict[str, str]) -> None:
    resp = client.post("/signup", data={**FORM, **overrides})
    assert resp.status_code == 200
    assert user_count() == 0


def test_signup_redirects_when_logged_in(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user())
    assert client.get("/signup").status_code == 302


def test_signup_race_on_unique_constraint(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch, make_user: MakeUser
) -> None:
    make_user("new_user")
    monkeypatch.setattr("app.routes.auth.or_", lambda *_: User.id == -1)
    resp = client.post("/signup", data=FORM)
    assert resp.status_code == 200
    assert b"already in use" in resp.data
    assert user_count() == 1


def test_verify_bad_token(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user(verified=False)
    resp = client.get("/verify/not-a-token", follow_redirects=True)
    assert b"invalid or has expired" in resp.data
    wrong_purpose = make_token(user.id, user.email, "reset-password")
    client.get(f"/verify/{wrong_purpose}")
    assert not user.is_verified


def test_verify_expired_token(
    client: FlaskClient, make_user: MakeUser, monkeypatch: pytest.MonkeyPatch
) -> None:
    user = make_user(verified=False)
    token = make_token(user.id, user.email, VERIFY_EMAIL)
    monkeypatch.setattr("app.routes.auth.VERIFY_MAX_AGE", -1)
    resp = client.get(f"/verify/{token}", follow_redirects=True)
    assert b"invalid or has expired" in resp.data
    assert not user.is_verified


def test_verify_already_verified_is_idempotent(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user()
    verified_at = user.email_verified_at
    client.get(f"/verify/{make_token(user.id, user.email, VERIFY_EMAIL)}")
    assert user.email_verified_at == verified_at


def test_verify_pending_page(client: FlaskClient, make_user: MakeUser) -> None:
    unverified = make_user("bob", verified=False)
    login_as(client, unverified)
    resp = client.get("/verify/pending")
    assert b"Verify your email" in resp.data
    assert b"bob@example.com" in resp.data
    assert b"Check your spam or junk folder" in resp.data


def test_verify_pending_redirects_verified_user(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user())
    assert client.get("/verify/pending").status_code == 302


def test_resend_sends_new_link(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    login_as(client, make_user(verified=False))
    with caplog.at_level(logging.INFO):
        resp = client.post("/verify/resend", follow_redirects=True)
    assert b"new verification link" in resp.data
    assert "/verify/" in caplog.text


def test_resend_is_limited_per_hour(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    user = make_user(verified=False)
    login_as(client, user)
    for _ in range(3):
        assert b"new verification link" in client.post("/verify/resend", follow_redirects=True).data
    caplog.clear()
    with caplog.at_level(logging.INFO):
        resp = client.post("/verify/resend", follow_redirects=True)
    assert b"try again in an hour" in resp.data
    assert "/verify/" not in caplog.text
    # The limit lifts once the earlier emails are an hour old.
    for row in db.session.scalars(select(LoginAttempt)):
        row.created_at = utcnow() - timedelta(hours=1, minutes=1)
    db.session.commit()
    assert b"new verification link" in client.post("/verify/resend", follow_redirects=True).data


def test_verified_required_prompts_unverified_user() -> None:
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    @app.get("/protected")
    @verified_required
    def protected() -> str:
        return "ok"

    with app.app_context():
        db.create_all()
        unverified = User(username="u", email="u@example.com", password_hash="x")  # noqa: S106
        verified = User(username="v", email="v@example.com", password_hash="x")  # noqa: S106
        verified.email_verified_at = utcnow()
        db.session.add_all([unverified, verified])
        db.session.commit()
        unverified_id, verified_id = unverified.id, verified.id

    client = app.test_client()
    assert "/login?next=" in client.get("/protected").location
    with client.session_transaction() as session:
        session["_user_id"] = str(unverified_id)
    resp = client.get("/protected")
    assert resp.status_code == 302
    assert resp.location.endswith("/verify/pending")
    with client.session_transaction() as session:
        session["_user_id"] = str(verified_id)
    assert client.get("/protected").get_data(as_text=True) == "ok"


def test_csrf_token_required() -> None:
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        client = app.test_client()
        rejected = client.post("/signup", data=FORM)
        assert rejected.status_code == 400
        assert "Your session ended" in rejected.get_data(as_text=True)
        page = client.get("/signup").get_data(as_text=True)
        token = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', page)
        assert token is not None
        resp = client.post("/signup", data={**FORM, "csrf_token": token.group(1)})
        assert resp.status_code == 302


def test_index_renders(app: Flask, client: FlaskClient) -> None:
    assert client.get("/").status_code == 200


def test_verify_token_bound_to_email(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user(verified=False)
    token = make_token(user.id, "old@example.com", VERIFY_EMAIL)
    resp = client.get(f"/verify/{token}", follow_redirects=True)
    assert b"invalid or has expired" in resp.data
    assert not user.is_verified


def test_signup_survives_mail_failure(
    client: FlaskClient, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def fail(*_: object) -> None:
        raise smtplib.SMTPServerDisconnected("down")

    monkeypatch.setattr("app.mail.send_email", fail)
    resp = client.post("/signup", data=FORM, follow_redirects=True)
    # Mail goes out in the background, so the page can only promise it (#105).
    assert b"Check your email to verify it" in resp.data
    assert b"Verify your email" in resp.data
    assert user_count() == 1
    assert "Could not send 'Verify your Pay My Bill email'" in caplog.text
    resp = client.post("/verify/resend", follow_redirects=True)
    assert b"new verification link" in resp.data


def test_malformed_session_user_id_is_anonymous(client: FlaskClient) -> None:
    with client.session_transaction() as session:
        session["_user_id"] = "not-a-number"
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Sign up" in resp.data


def test_proxy_headers_make_https_links(
    client: FlaskClient, caplog: pytest.LogCaptureFixture
) -> None:
    client.post("/signup", data=FORM, headers={"X-Forwarded-Proto": "https"})
    assert "https://localhost/verify/" in caplog.text


def test_signup_requires_18_plus(client: FlaskClient) -> None:
    resp = client.post("/signup", data={k: v for k, v in FORM.items() if k != "adult"})
    assert resp.status_code == 200
    assert "You need to be 18 or older and agree to the Terms and Privacy Policy." in resp.get_data(
        as_text=True
    )
    assert user_count() == 0


def test_signup_stores_adult_attestation(client: FlaskClient) -> None:
    client.post("/signup", data=FORM)
    user = db.session.scalar(select(User))
    assert user is not None
    assert user.adult_attested_at is not None
    assert utcnow() - as_utc(user.adult_attested_at) < timedelta(seconds=30)


def test_field_errors_are_linked_for_screen_readers(client: FlaskClient) -> None:
    page = client.post("/signup", data={**FORM, "username": "x"}).get_data(as_text=True)
    assert 'aria-describedby="username-error" aria-invalid="true"' in page
    assert (
        '<small class="error" id="username-error">Usernames are 3 to 30 characters.</small>' in page
    )


def signup_as(client: FlaskClient, n: int, ip: str = "203.0.113.7") -> int:
    form = {**FORM, "username": f"user{n}", "email": f"user{n}@example.com"}
    status = client.post("/signup", data=form, environ_base={"REMOTE_ADDR": ip}).status_code
    # Requests in the fixture's app context share g, so forget who signed up.
    g.pop("_login_user", None)
    return status


def test_signups_are_limited_per_address(app: Flask) -> None:
    for n in range(MAX_SIGNUPS_PER_IP):
        assert signup_as(app.test_client(), n) == 302
    resp = app.test_client().post(
        "/signup",
        data={**FORM, "username": "one_more", "email": "more@example.com"},
        environ_base={"REMOTE_ADDR": "203.0.113.7"},
    )
    assert resp.status_code == 429
    assert resp.headers["Retry-After"] == str(int(SIGNUP_WINDOW.total_seconds()))
    assert b"Too many new accounts from your network" in resp.data
    assert user_count() == MAX_SIGNUPS_PER_IP
    # Another address is unaffected, and the window passing lifts the limit.
    assert signup_as(app.test_client(), 100, ip="198.51.100.9") == 302
    db.session.execute(
        update(LoginAttempt).values(created_at=utcnow() - SIGNUP_WINDOW - timedelta(minutes=1))
    )
    db.session.commit()
    assert signup_as(app.test_client(), 101) == 302


def test_signups_do_not_count_toward_the_login_lockout(app: Flask, make_user: MakeUser) -> None:
    make_user("alice")
    for n in range(MAX_SIGNUPS_PER_IP):
        signup_as(app.test_client(), n, ip="127.0.0.1")
    resp = app.test_client().post("/login", data={"identifier": "alice", "password": PASSWORD})
    assert resp.status_code == 302
