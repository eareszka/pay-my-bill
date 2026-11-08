from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import stripe
from flask import Flask
from flask.testing import FlaskClient

from app import stripe_pay
from app.extensions import db
from app.models import Post, PostKind, User
from tests.conftest import MakeUser, login_as


@pytest.fixture
def stripe_on(app: Flask) -> None:
    app.config["STRIPE_SECRET_KEY"] = "sk_test_fake"  # noqa: S105 - test fixture


@pytest.fixture
def fake_client(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    fake = MagicMock()
    fake.v1.accounts.create.return_value = SimpleNamespace(id="acct_123")
    fake.v1.account_links.create.return_value = SimpleNamespace(url="https://connect.stripe.com/x")
    fake.v1.accounts.login_links.create.return_value = SimpleNamespace(
        url="https://connect.stripe.com/express/x"
    )
    monkeypatch.setattr(stripe_pay, "client", lambda: fake)
    return fake


def account(details: bool = True, payouts: bool = True, transfers: str | None = "active") -> object:
    caps = SimpleNamespace(transfers=transfers) if transfers is not None else None
    return SimpleNamespace(details_submitted=details, payouts_enabled=payouts, capabilities=caps)


def test_profile_hides_stripe_when_not_configured(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("alice"))
    assert b"Connect Stripe" not in client.get("/profile").data
    assert client.post("/stripe/connect").status_code == 404
    assert client.get("/stripe/connect/done").status_code == 404
    assert client.post("/stripe/dashboard").status_code == 404


@pytest.mark.usefixtures("stripe_on")
def test_connect_creates_account_and_redirects_to_stripe(
    client: FlaskClient, make_user: MakeUser, fake_client: MagicMock
) -> None:
    user = make_user("alice")
    login_as(client, user)
    assert b"Connect Stripe" in client.get("/profile").data
    resp = client.post("/stripe/connect")
    assert resp.status_code == 302
    assert resp.location == "https://connect.stripe.com/x"
    db.session.refresh(user)
    assert user.stripe_account_id == "acct_123"
    params = fake_client.v1.account_links.create.call_args.kwargs["params"]
    assert params["account"] == "acct_123"
    assert params["return_url"] == "http://localhost/stripe/connect/done"
    assert b"Finish Stripe setup" in client.get("/profile").data

    client.get("/stripe/connect/refresh")
    assert fake_client.v1.accounts.create.call_count == 1


@pytest.mark.usefixtures("stripe_on")
def test_connect_needs_verified_email(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("new", verified=False))
    assert client.post("/stripe/connect").location.endswith("/verify/pending")


@pytest.mark.usefixtures("stripe_on")
@pytest.mark.parametrize(
    ("acct", "ready", "message"),
    [
        (account(), True, b"Stripe is connected"),
        (account(details=False), False, b"still needs a few details"),
        (account(transfers="pending"), False, b"still needs a few details"),
        (account(transfers=None), False, b"still needs a few details"),
    ],
)
def test_return_from_stripe_records_readiness(
    client: FlaskClient,
    make_user: MakeUser,
    fake_client: MagicMock,
    acct: object,
    ready: bool,
    message: bytes,
) -> None:
    user = make_user("alice", stripe_account_id="acct_123")
    fake_client.v1.accounts.retrieve.return_value = acct
    login_as(client, user)
    resp = client.get("/stripe/connect/done", follow_redirects=True)
    assert message in resp.data
    db.session.refresh(user)
    assert user.stripe_ready is ready


@pytest.mark.usefixtures("stripe_on")
def test_return_without_account_is_not_ready(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("alice"))
    assert (
        b"still needs a few details"
        in client.get("/stripe/connect/done", follow_redirects=True).data
    )


@pytest.mark.usefixtures("stripe_on")
def test_dashboard_link_for_connected_recipient(
    client: FlaskClient, make_user: MakeUser, fake_client: MagicMock
) -> None:
    user = make_user("alice", stripe_account_id="acct_123", stripe_ready=True)
    login_as(client, user)
    assert b"Payouts and bank details" in client.get("/profile").data
    resp = client.post("/stripe/dashboard")
    assert resp.location == "https://connect.stripe.com/express/x"


@pytest.mark.usefixtures("stripe_on")
def test_dashboard_without_account_is_404(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("alice"))
    assert client.post("/stripe/dashboard").status_code == 404


@pytest.mark.usefixtures("stripe_on")
@pytest.mark.parametrize(
    ("method", "path", "fail"),
    [
        ("post", "/stripe/connect", "account_links"),
        ("get", "/stripe/connect/done", "retrieve"),
        ("post", "/stripe/dashboard", "login_links"),
    ],
)
def test_stripe_errors_are_explained(
    client: FlaskClient,
    make_user: MakeUser,
    fake_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
    method: str,
    path: str,
    fail: str,
) -> None:
    error = stripe.APIConnectionError("down")
    targets = {
        "account_links": fake_client.v1.account_links.create,
        "retrieve": fake_client.v1.accounts.retrieve,
        "login_links": fake_client.v1.accounts.login_links.create,
    }
    targets[fail].side_effect = error
    login_as(client, make_user("alice", stripe_account_id="acct_123"))
    resp = getattr(client, method)(path, follow_redirects=True)
    assert b"Stripe isn&#39;t answering" in resp.data
    assert "Stripe" in caplog.text


def test_stripe_only_recipient_can_post_and_be_paid(
    client: FlaskClient, make_user: MakeUser
) -> None:
    user: User = make_user("alice", stripe_ready=True)
    assert user.can_be_paid and not user.has_payment_handle
    login_as(client, user)
    assert client.get("/posts/new").status_code == 200
    post = Post(user=user, kind=PostKind.NEED, title="Rent", body="Short on rent.", goal_cents=5000)
    db.session.add(post)
    db.session.commit()
    assert not make_user("bob").can_be_paid
