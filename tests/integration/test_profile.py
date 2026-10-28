import logging
import smtplib

import pytest
from flask.testing import FlaskClient

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

    monkeypatch.setattr("app.routes.profile.send_email", fail)
    user = make_user()
    login_as(client, user)
    resp = client.post("/profile", data=FORM, follow_redirects=True)
    assert b"Profile saved." in resp.data
    assert user.cashapp_handle == "$maria"
    assert "Could not send the handle-change notice" in caplog.text


def test_public_profile_without_handles(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("bob")
    page = client.get("/u/bob").get_data(as_text=True)
    assert "No payment handles yet." in page


def test_public_profile_404(client: FlaskClient) -> None:
    assert client.get("/u/nobody").status_code == 404
