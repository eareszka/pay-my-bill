import logging
import smtplib

import pytest
from flask.testing import FlaskClient

from app.extensions import db
from app.models import Post, PostKind, PostStatus, User
from tests.conftest import MakeUser, login_as

FORM = {
    "city": "Sarasota",
    "state": "FL",
    "cashapp_handle": "maria",
    "venmo_handle": "",
    "paypal_handle": "paypal.me/MariaG",
}


def test_profile_requires_login(client: FlaskClient) -> None:
    assert client.get("/profile").location == "/login?next=/profile"


def test_profile_form_renders(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user(city="Tampa", state="FL", venmo_handle="@alice"))
    page = client.get("/profile").get_data(as_text=True)
    assert 'value="Tampa"' in page
    assert 'value="@alice"' in page
    assert '<option selected value="FL">' in page
    assert "never use GPS" in page
    assert "5 to 30 letters" in page


def test_save_profile_normalizes_and_shows_handles(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    user = make_user()
    login_as(client, user)
    resp = client.post("/profile", data=FORM, follow_redirects=True)
    assert b"Profile saved." in resp.data
    assert (user.city, user.state) == ("Sarasota", "FL")
    assert (user.cashapp_handle, user.venmo_handle, user.paypal_handle) == (
        "$maria",
        None,
        "MariaG",
    )
    assert "Your payment handles changed" in caplog.text
    assert "Cash App: (none) -> $maria" in caplog.text
    assert "PayPal: (none) -> paypal.me/MariaG" in caplog.text

    page = client.get("/u/ALICE").get_data(as_text=True)
    assert "Sarasota, FL" in page
    assert "$maria" in page
    assert "paypal.me/MariaG" in page


def test_no_notice_when_handles_unchanged(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    login_as(client, make_user(cashapp_handle="$maria", paypal_handle="MariaG"))
    with caplog.at_level(logging.INFO):
        client.post("/profile", data={**FORM, "city": "Bradenton"})
    assert "Your payment handles changed" not in caplog.text


def test_removing_handle_sends_notice(
    client: FlaskClient, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    user = make_user(venmo_handle="@alice-v")
    login_as(client, user)
    client.post("/profile", data={**FORM, "cashapp_handle": "", "paypal_handle": ""})
    assert user.venmo_handle is None
    assert "Venmo: @alice-v -> (none)" in caplog.text


@pytest.mark.parametrize(
    "overrides",
    [
        {"cashapp_handle": "$not valid"},
        {"venmo_handle": "@abc"},
        {"paypal_handle": "bad_name"},
        {"state": "ZZ"},
        {"state": ""},
        {"city": "", "state": "FL"},
        {"city": "x" * 81},
    ],
)
def test_invalid_profile_not_saved(
    client: FlaskClient, make_user: MakeUser, overrides: dict[str, str]
) -> None:
    user = make_user()
    login_as(client, user)
    resp = client.post("/profile", data={**FORM, **overrides})
    assert resp.status_code == 200
    assert user.cashapp_handle is None
    assert user.city is None


def test_clearing_region_is_allowed(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user(city="Tampa", state="FL")
    login_as(client, user)
    client.post("/profile", data={**FORM, "city": "", "state": ""})
    assert (user.city, user.state) == (None, None)


def test_notice_failure_does_not_block_save(
    client: FlaskClient,
    make_user: MakeUser,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def fail(*_: object) -> None:
        raise smtplib.SMTPServerDisconnected("down")

    monkeypatch.setattr("app.mail.send_email", fail)
    user = make_user()
    login_as(client, user)
    resp = client.post("/profile", data=FORM, follow_redirects=True)
    assert b"Profile saved." in resp.data
    assert user.cashapp_handle == "$maria"
    assert "Could not send 'Your payment handles changed'" in caplog.text


def test_public_profile_without_handles(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("bob")
    page = client.get("/u/bob").get_data(as_text=True)
    assert "No payment handles yet." in page


def test_public_profile_404(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("bob", verified=False, venmo_handle="@bobby")
    assert client.get("/u/nobody").status_code == 404
    assert client.get("/u/bob").status_code == 404


@pytest.mark.parametrize("blank", ["   ", "	"])
def test_whitespace_handle_saved_as_none(
    client: FlaskClient, make_user: MakeUser, blank: str
) -> None:
    user = make_user()
    login_as(client, user)
    client.post("/profile", data={**FORM, "cashapp_handle": blank, "city": "  ", "state": ""})
    assert user.cashapp_handle is None
    assert user.city is None
    assert user.paypal_handle == "MariaG"


CLEARED = {"cashapp_handle": "", "venmo_handle": "", "paypal_handle": "", "city": "", "state": ""}


def live_post(user: User, status: PostStatus = PostStatus.OPEN) -> Post:
    post = Post(user=user, kind=PostKind.NEED, title="Rent", body="Short.", goal_cents=5_000)
    post.status = status
    db.session.add(post)
    db.session.commit()
    return post


@pytest.mark.parametrize("status", [PostStatus.OPEN, PostStatus.PENDING_REVIEW])
def test_cannot_clear_the_last_handle_with_a_live_post(
    client: FlaskClient, make_user: MakeUser, status: PostStatus
) -> None:
    user = make_user(venmo_handle="@alice")
    live_post(user, status)
    login_as(client, user)
    resp = client.post("/profile", data=CLEARED)
    assert resp.status_code == 400
    assert "Keep one way to get paid while you have an open post" in resp.get_data(as_text=True)
    db.session.refresh(user)
    assert user.venmo_handle == "@alice"


def test_can_swap_handles_with_a_live_post(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user(venmo_handle="@alice")
    live_post(user)
    login_as(client, user)
    client.post("/profile", data={**CLEARED, "cashapp_handle": "alice"})
    assert (user.cashapp_handle, user.venmo_handle) == ("$alice", None)


def test_can_clear_handles_once_posts_are_closed(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user(venmo_handle="@alice")
    live_post(user, PostStatus.CLOSED)
    login_as(client, user)
    assert client.post("/profile", data=CLEARED).status_code == 302
    assert user.venmo_handle is None


def test_card_counts_as_a_way_to_get_paid(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user(venmo_handle="@alice", stripe_ready=True)
    live_post(user)
    login_as(client, user)
    assert client.post("/profile", data=CLEARED).status_code == 302
