import re
from datetime import timedelta
from unittest.mock import patch

import pytest
from flask.testing import FlaskClient
from sqlalchemy import select

from app.extensions import db
from app.models import (
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    PostKind,
    PostStatus,
    User,
    utcnow,
)
from app.tokens import GIFT_ANSWER, make_token
from tests.conftest import MakeUser, login_as


@pytest.fixture
def post(make_user: MakeUser) -> Post:
    owner = make_user("maria_g", cashapp_handle="$mariag")
    post = Post(
        user=owner, kind=PostKind.NEED, title="Rent", body="Short on rent.", goal_cents=3_000
    )
    db.session.add(post)
    db.session.commit()
    return post


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def answer_link(
    client: FlaskClient,
    post: Post,
    donor: User,
    caplog: pytest.LogCaptureFixture,
    amount: str = "20",
) -> str:
    login_as(client, donor)
    client.post(f"/posts/{post.id}/gifts", data={"amount": amount, "method": "cashapp"})
    links = re.findall(r"http://localhost(/gifts/answer/\S+)", caplog.text)
    assert links
    with client.session_transaction() as session:
        session.clear()
    return links[-1]


def gift() -> Donation:
    return db.session.scalars(select(Donation)).one()


def test_email_link_shows_question_without_answering(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    link = answer_link(client, post, donor, caplog)
    assert "answer in one tap" in caplog.text
    page = client.get(link)
    assert page.status_code == 200
    assert b"Did $20 arrive?" in page.data
    assert b"via Cash App from dev_tom" in page.data
    assert gift().status == DonationStatus.PENDING


def test_yes_confirms_without_logging_in(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    link = answer_link(client, post, donor, caplog)
    resp = client.post(f"{link}/confirm")
    assert resp.status_code == 200
    assert b"Confirmed $20 from dev_tom" in resp.data
    assert gift().status == DonationStatus.CONFIRMED
    again = client.post(f"{link}/dispute")
    assert b"already handled" in again.data
    assert b"already handled" in client.get(link).data


def test_no_disputes(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    link = answer_link(client, post, donor, caplog)
    resp = client.post(f"{link}/dispute")
    assert b"as not received" in resp.data
    assert gift().status == DonationStatus.DISPUTED


def test_confirm_that_funds_the_post(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    link = answer_link(client, post, donor, caplog, amount="30")
    resp = client.post(f"{link}/confirm")
    assert b"fully funded" in resp.data
    db.session.refresh(post)
    assert post.status == PostStatus.FUNDED


def test_bad_tokens_are_404(client: FlaskClient, post: Post, donor: User) -> None:
    gift_ = Donation(post=post, donor=donor, amount_cents=500, method=PaymentMethod.CASHAPP)
    db.session.add(gift_)
    db.session.commit()
    assert client.get("/gifts/answer/garbage").status_code == 404
    wrong_owner = make_token(gift_.id, str(donor.id), GIFT_ANSWER)
    assert client.get(f"/gifts/answer/{wrong_owner}").status_code == 404
    not_digits = make_token(gift_.id, "abc", GIFT_ANSWER)
    assert client.get(f"/gifts/answer/{not_digits}").status_code == 404
    missing = make_token(99999, str(post.user_id), GIFT_ANSWER)
    assert client.post(f"/gifts/answer/{missing}/confirm").status_code == 404


def test_expired_link_is_404(client: FlaskClient, post: Post, donor: User) -> None:
    gift_ = Donation(post=post, donor=donor, amount_cents=500, method=PaymentMethod.CASHAPP)
    db.session.add(gift_)
    db.session.commit()
    token = make_token(gift_.id, str(post.user_id), GIFT_ANSWER)
    later = utcnow() + timedelta(days=15)
    with patch("itsdangerous.timed.time.time", return_value=later.timestamp()):
        assert client.get(f"/gifts/answer/{token}").status_code == 404


def test_removed_post_link_is_404(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    link = answer_link(client, post, donor, caplog)
    post.status = PostStatus.REMOVED
    db.session.commit()
    assert client.get(link).status_code == 404
