import logging
import smtplib
from datetime import timedelta

import pytest
from flask import Flask
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
from tests.conftest import MakeUser, login_as


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g")


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def add_post(owner: User, title: str = "Rent") -> Post:
    post = Post(user=owner, kind=PostKind.NEED, title=title, body="Short.", goal_cents=30_000)
    db.session.add(post)
    db.session.commit()
    return post


def add_gift(
    post: Post,
    donor: User,
    days_old: float,
    status: DonationStatus = DonationStatus.PENDING,
    cents: int = 2_000,
) -> Donation:
    gift = Donation(
        post=post,
        donor=donor,
        amount_cents=cents,
        method=PaymentMethod.VENMO,
        status=status,
        created_at=utcnow() - timedelta(days=days_old),
    )
    db.session.add(gift)
    db.session.commit()
    return gift


def test_expired_gift_leaves_to_confirm_and_badge(
    client: FlaskClient, poster: User, donor: User
) -> None:
    add_gift(add_post(poster), donor, days_old=15)
    login_as(client, poster)
    page = client.get("/gifts").get_data(as_text=True)
    assert "To confirm" not in page
    assert 'class="badge"' not in page


def test_gift_under_14_days_still_waits(client: FlaskClient, poster: User, donor: User) -> None:
    add_gift(add_post(poster), donor, days_old=13.9)
    login_as(client, poster)
    page = client.get("/gifts").get_data(as_text=True)
    assert '<span class="count">1</span>' in page


def test_expired_gift_cannot_be_confirmed(client: FlaskClient, poster: User, donor: User) -> None:
    gift = add_gift(add_post(poster), donor, days_old=15)
    login_as(client, poster)
    assert client.post(f"/gifts/{gift.id}/confirm").location == "/gifts"
    assert gift.status is DonationStatus.PENDING
    assert gift.post.raised_cents == 0
    page = client.get("/gifts").get_data(as_text=True)
    assert "That gift expired after 14 days, so it can&#39;t count." in page


def test_donor_sees_expired_status(client: FlaskClient, poster: User, donor: User) -> None:
    add_gift(add_post(poster), donor, days_old=15)
    login_as(client, donor)
    page = client.get("/gifts").get_data(as_text=True)
    assert 'chip-expired">Expired' in page


def test_expired_gift_does_not_block_a_new_one(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster)
    add_gift(post, donor, days_old=15)
    login_as(client, donor)
    resp = client.post(f"/posts/{post.id}/gifts", data={"amount": "10", "method": "venmo"})
    assert resp.location == f"/posts/{post.id}"
    assert len(post.donations) == 2


def run_remind(app: Flask) -> str:
    result = app.test_cli_runner().invoke(args=["gifts", "remind"])
    assert result.exit_code == 0
    return result.output


def test_remind_emails_each_poster_once(
    app: Flask, poster: User, donor: User, make_user: MakeUser, caplog: pytest.LogCaptureFixture
) -> None:
    rent = add_post(poster)
    due = add_gift(rent, donor, days_old=4)
    too_new = add_gift(rent, donor, days_old=2, cents=500)
    expired = add_gift(rent, donor, days_old=15, cents=700)
    confirmed = add_gift(rent, donor, days_old=5, status=DonationStatus.CONFIRMED, cents=900)
    removed = add_post(poster, "Gone")
    removed.status = PostStatus.REMOVED
    on_removed = add_gift(removed, donor, days_old=4, cents=1_100)
    other = add_post(make_user("kayla.r"), "Textbook")
    other_due = add_gift(other, donor, days_old=3.01, cents=1_500)

    with caplog.at_level(logging.INFO):
        assert run_remind(app) == "Reminder emails sent: 2\n"
    assert due.reminded_at is not None
    assert other_due.reminded_at is not None
    assert all(g.reminded_at is None for g in (too_new, expired, confirmed, on_removed))
    assert "Gifts waiting for you to confirm" in caplog.text
    assert '- $20 via Venmo from dev_tom for "Rent"' in caplog.text
    assert "http://localhost" in caplog.text
    assert "/gifts" in caplog.text
    assert run_remind(app) == "Reminder emails sent: 0\n"


def test_remind_retries_after_email_failure(
    app: Flask,
    poster: User,
    donor: User,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    gift = add_gift(add_post(poster), donor, days_old=4)

    def fail(*_: object) -> None:
        raise smtplib.SMTPException("down")

    monkeypatch.setattr("app.routes.gifts.send_email", fail)
    assert run_remind(app) == "Reminder emails sent: 0\n"
    assert gift.reminded_at is None
    assert "Could not send the gift reminder" in caplog.text
    monkeypatch.undo()
    assert run_remind(app) == "Reminder emails sent: 1\n"
    assert db.session.scalar(select(Donation.reminded_at)) is not None
