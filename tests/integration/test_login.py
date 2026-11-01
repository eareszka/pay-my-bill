from datetime import timedelta

import pytest
from flask.testing import FlaskClient
from sqlalchemy import select, update

from app.auth import LOGIN_WINDOW, MAX_FAILED_LOGINS, MAX_FAILED_LOGINS_PER_IP
from app.extensions import db
from app.models import LoginAttempt, utcnow
from tests.conftest import PASSWORD, MakeUser, login_as


def log_in(client: FlaskClient, identifier: str, password: str = PASSWORD, next_: str = "") -> int:
    url = f"/login?next={next_}" if next_ else "/login"
    resp = client.post(url, data={"identifier": identifier, "password": password})
    return resp.status_code


def logged_in_as(client: FlaskClient) -> str | None:
    with client.session_transaction() as session:
        return session.get("_user_id")


def test_login_page_renders(client: FlaskClient) -> None:
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"Log in" in resp.data


@pytest.mark.parametrize("identifier", ["alice", "ALICE@example.com"])
def test_login_success_lands_on_feed(
    client: FlaskClient, make_user: MakeUser, identifier: str
) -> None:
    user = make_user("alice")
    resp = client.post("/login", data={"identifier": identifier, "password": PASSWORD})
    assert resp.status_code == 302
    assert resp.location == "/"
    assert logged_in_as(client) == str(user.id)
    attempt = db.session.scalars(select(LoginAttempt)).one()
    assert (attempt.identifier, attempt.succeeded) == ("alice", True)


@pytest.mark.parametrize(
    ("identifier", "password"), [("alice", "wrong-pass"), ("nobody", PASSWORD)]
)
def test_login_failure(
    client: FlaskClient, make_user: MakeUser, identifier: str, password: str
) -> None:
    make_user("alice")
    resp = client.post("/login", data={"identifier": identifier, "password": password})
    assert resp.status_code == 200
    assert b"Wrong username, email, or password." in resp.data
    assert logged_in_as(client) is None


def test_login_rate_limited_after_five_failures(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("alice")
    for _ in range(MAX_FAILED_LOGINS):
        assert log_in(client, "alice", "wrong-pass") == 200
    resp = client.post("/login", data={"identifier": "alice", "password": PASSWORD})
    assert resp.status_code == 429
    assert resp.headers["Retry-After"] == str(int(LOGIN_WINDOW.total_seconds()))
    assert logged_in_as(client) is None
    assert log_in(client, "Alice@Example.com") == 429
    make_user("bob")
    assert log_in(client, "bob") == 302


def test_rate_limit_window_expires(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("alice")
    for _ in range(MAX_FAILED_LOGINS):
        log_in(client, "alice", "wrong-pass")
    db.session.execute(
        update(LoginAttempt).values(created_at=utcnow() - LOGIN_WINDOW - timedelta(seconds=1))
    )
    db.session.commit()
    assert log_in(client, "alice") == 302


@pytest.mark.parametrize(
    ("next_", "expected"),
    [
        ("/verify/pending", "/verify/pending"),
        ("https://evil.example.com/", "/"),
        ("//evil.example.com/", "/"),
        (r"/\evil.example.com", "/"),
    ],
)
def test_login_next_must_be_local(
    client: FlaskClient, make_user: MakeUser, next_: str, expected: str
) -> None:
    make_user("alice")
    resp = client.post(
        "/login", query_string={"next": next_}, data={"identifier": "alice", "password": PASSWORD}
    )
    assert resp.location == expected


def test_login_redirects_when_logged_in(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user())
    assert client.get("/login").status_code == 302


def test_logout_ends_session(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user())
    assert b"Log out" in client.get("/profile").data
    resp = client.post("/logout", follow_redirects=True)
    assert b"logged out" in resp.data
    assert logged_in_as(client) is None
    assert b"Log in" in resp.data


def test_logout_requires_post(client: FlaskClient) -> None:
    assert client.get("/logout").status_code == 405


def test_success_resets_failure_count(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("alice")
    for _ in range(MAX_FAILED_LOGINS - 1):
        log_in(client, "alice", "wrong-pass")
    assert log_in(client, "alice") == 302
    client.post("/logout")
    for _ in range(MAX_FAILED_LOGINS - 1):
        log_in(client, "alice", "wrong-pass")
    assert log_in(client, "alice") == 302


def test_lockout_is_per_ip(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("alice")
    attacker = {"REMOTE_ADDR": "203.0.113.9"}
    for _ in range(MAX_FAILED_LOGINS + 3):
        client.post("/login", data={"identifier": "alice", "password": "x"}, environ_base=attacker)
    assert log_in(client, "alice") == 302


def test_password_spraying_limited_per_ip(client: FlaskClient) -> None:
    for i in range(MAX_FAILED_LOGINS_PER_IP):
        assert log_in(client, f"user{i}", "password123") == 200
    assert log_in(client, "another", "password123") == 429


def test_locked_attempts_are_recorded(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("alice")
    for _ in range(MAX_FAILED_LOGINS + 2):
        log_in(client, "alice", "wrong-pass")
    assert len(db.session.scalars(select(LoginAttempt)).all()) == MAX_FAILED_LOGINS + 2


def test_unauthorized_get_keeps_next_post_drops_it(client: FlaskClient) -> None:
    assert client.get("/verify/pending").location == "/login?next=/verify/pending"
    assert client.post("/verify/resend").location == "/login"
