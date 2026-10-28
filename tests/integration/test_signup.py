import logging
import re
import smtplib

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import func, select
from werkzeug.security import check_password_hash

from app import create_app
from app.auth import verified_required
from app.extensions import db
from app.models import User, utcnow
from app.tokens import VERIFY_EMAIL, make_token
from tests.conftest import MakeUser, login_as

FORM = {
    "username": "New_User",
    "email": "New@Example.com",
    "password": "s3cret-pass",
    "confirm": "s3cret-pass",
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
        assert client.post("/signup", data=FORM).status_code == 400
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

    monkeypatch.setattr("app.routes.auth.send_email", fail)
    resp = client.post("/signup", data=FORM, follow_redirects=True)
    assert b"couldn&#39;t send your verification email" in resp.data
    assert b"Verify your email" in resp.data
    assert user_count() == 1
    assert "Could not send the verification email" in caplog.text
    resp = client.post("/verify/resend", follow_redirects=True)
    assert b"new verification link" not in resp.data


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
