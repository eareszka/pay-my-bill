import logging
import smtplib

import pytest
from flask.testing import FlaskClient
from sqlalchemy import select

from app.extensions import db
from app.models import Donation, DonationStatus, PaymentMethod, Post, PostKind, PostStatus, User
from tests.conftest import MakeUser, login_as


@pytest.fixture
def post(make_user: MakeUser) -> Post:
    owner = make_user("maria_g", cashapp_handle="$mariag", venmo_handle="@maria-g")
    post = Post(
        user=owner, kind=PostKind.NEED, title="Rent", body="Short on rent.", goal_cents=30_000
    )
    db.session.add(post)
    db.session.commit()
    return post


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def gifts() -> list[Donation]:
    return list(db.session.scalars(select(Donation)))


def send(client: FlaskClient, post: Post, amount: str = "20", method: str = "venmo"):  # type: ignore[no-untyped-def]
    return client.post(f"/posts/{post.id}/gifts", data={"amount": amount, "method": method})


def test_record_gift_emails_poster(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    login_as(client, donor)
    with caplog.at_level(logging.INFO):
        resp = send(client, post, "$12.50")
    assert resp.status_code == 302
    assert resp.location == f"/posts/{post.id}"
    [gift] = gifts()
    assert (gift.donor, gift.amount_cents, gift.method, gift.status) == (
        donor,
        1_250,
        PaymentMethod.VENMO,
        DonationStatus.PENDING,
    )
    assert post.raised_cents == 0
    assert "dev_tom sent you a gift" in caplog.text
    assert 'dev_tom says they sent you $12.50 via Venmo for "Rent"' in caplog.text


def test_form_shown_to_logged_in_donor(client: FlaskClient, post: Post, donor: User) -> None:
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f'action="/posts/{post.id}/gifts"' in page
    assert '<option value="cashapp">Cash App</option>' in page
    assert "I sent it" in page


def test_logged_out_visitor_gets_login_link(client: FlaskClient, post: Post) -> None:
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f"/login?next=/posts/{post.id}" in page
    assert "I sent it" not in page
    assert send(client, post).location.startswith("/login")
    assert gifts() == []


def test_unverified_donor_sent_to_verify(
    client: FlaskClient, post: Post, make_user: MakeUser
) -> None:
    login_as(client, make_user("newbie", verified=False))
    assert send(client, post).location == "/verify/pending"
    assert gifts() == []


def test_poster_cannot_gift_themselves(client: FlaskClient, post: Post) -> None:
    login_as(client, post.user)
    assert send(client, post).status_code == 403
    assert gifts() == []


@pytest.mark.parametrize("status", [PostStatus.FUNDED, PostStatus.CLOSED, PostStatus.REMOVED])
def test_only_open_posts_take_gifts(
    client: FlaskClient, post: Post, donor: User, status: PostStatus
) -> None:
    post.status = status
    db.session.commit()
    login_as(client, donor)
    assert send(client, post).status_code == 404
    assert gifts() == []


def test_missing_post(client: FlaskClient, donor: User) -> None:
    login_as(client, donor)
    assert client.post("/posts/999/gifts").status_code == 404
    assert client.post(f"/posts/{2**31}/gifts").status_code == 404


@pytest.mark.parametrize(
    ("amount", "method", "message"),
    [
        ("0", "venmo", "Gifts can be up to $1,000"),
        ("1000.01", "venmo", "Gifts can be up to $1,000"),
        ("5,50", "venmo", "Enter an amount like 20 or 12.50"),
        ("", "venmo", "This field is required"),
        ("20", "paypal", "Not a valid choice"),
    ],
)
def test_bad_gift_rejected(
    client: FlaskClient, post: Post, donor: User, amount: str, method: str, message: str
) -> None:
    login_as(client, donor)
    resp = send(client, post, amount, method)
    page = resp.get_data(as_text=True)
    assert resp.status_code == 400
    assert message in page
    assert page.count('class="error">') == 1
    assert gifts() == []


def test_gift_saved_when_email_fails(
    client: FlaskClient,
    post: Post,
    donor: User,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def fail(*_: object) -> None:
        raise smtplib.SMTPException("down")

    monkeypatch.setattr("app.routes.gifts.send_email", fail)
    login_as(client, donor)
    assert send(client, post).status_code == 302
    assert len(gifts()) == 1
    assert "Could not send the gift notice" in caplog.text
