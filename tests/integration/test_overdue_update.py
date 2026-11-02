import logging
import smtplib
from datetime import timedelta

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.accounts import anonymize, delete_post
from app.extensions import db
from app.models import (
    UPDATE_DUE_DAYS,
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    PostKind,
    PostStatus,
    User,
    utcnow,
)
from app.routes.posts import overdue_post, send_update_reminders
from tests.conftest import MakeUser, login_as

NOTE = "Made rent on time. Thank you all so much."
FORM = {"kind": "need", "title": "Phone bill", "body": "Need it for work.", "goal": "20"}


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g", rules_accepted_at=utcnow())


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def closed_days_ago(owner: User, donor: User | None, days: float) -> Post:
    when = utcnow() - timedelta(days=days)
    post = Post(
        user=owner,
        kind=PostKind.NEED,
        title="Rent",
        body="Short.",
        goal_cents=9_000,
        status=PostStatus.CLOSED,
        closed_at=when,
    )
    if donor:
        post.donations.append(
            Donation(
                donor=donor,
                amount_cents=2_000,
                method=PaymentMethod.VENMO,
                status=DonationStatus.CONFIRMED,
                resolved_at=when,
            )
        )
    db.session.add(post)
    db.session.commit()
    return post


def reminders(caplog: pytest.LogCaptureFixture) -> int:
    return sum("Your results update is due soon" in r.getMessage() for r in caplog.records)


@pytest.mark.parametrize(
    ("days", "blocked"), [(UPDATE_DUE_DAYS - 0.01, False), (UPDATE_DUE_DAYS, True)]
)
def test_block_starts_at_the_deadline(
    poster: User, donor: User, days: float, blocked: bool
) -> None:
    post = closed_days_ago(poster, donor, days)
    assert (overdue_post(poster) is post) is blocked


def test_no_confirmed_gift_means_no_block(poster: User) -> None:
    closed_days_ago(poster, None, 30)
    assert overdue_post(poster) is None


def test_other_peoples_overdue_posts_do_not_count(
    poster: User, donor: User, make_user: MakeUser
) -> None:
    closed_days_ago(make_user("kayla"), donor, 30)
    assert overdue_post(poster) is None


def test_auto_closed_post_can_go_overdue(poster: User, donor: User) -> None:
    post = closed_days_ago(poster, donor, 40)
    post.status = PostStatus.OPEN
    post.closed_at = None
    post.created_at = utcnow() - timedelta(days=40)
    db.session.commit()
    assert overdue_post(poster) is post


@pytest.mark.parametrize("method", ["get", "post"])
def test_overdue_poster_is_sent_to_the_post(
    client: FlaskClient, poster: User, donor: User, method: str
) -> None:
    post = closed_days_ago(poster, donor, 8)
    login_as(client, poster)
    response = getattr(client, method)("/posts/new", data=FORM)
    assert response.status_code == 302
    assert response.location.endswith(f"/posts/{post.id}#update")
    page = client.get(response.location).get_data(as_text=True)
    assert "Post this overdue results update" in page
    assert "can't create new posts until it's up" in page
    assert db.session.query(Post).filter_by(title="Phone bill").first() is None


def test_posting_the_update_lifts_the_block_right_away(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = closed_days_ago(poster, donor, 30)
    login_as(client, poster)
    client.post(f"/posts/{post.id}/update", data={"note": NOTE})
    assert client.get("/posts/new").status_code == 200
    assert client.post("/posts/new", data=FORM).status_code == 302
    assert db.session.query(Post).filter_by(title="Phone bill").first() is not None


def test_deleting_does_not_lift_the_block(client: FlaskClient, poster: User, donor: User) -> None:
    post = closed_days_ago(poster, donor, 30)
    delete_post(post)
    db.session.commit()
    login_as(client, poster)
    assert client.get("/posts/new").location.endswith(f"/posts/{post.id}#update")
    client.post(f"/posts/{post.id}/update", data={"note": NOTE})
    assert client.get("/posts/new").status_code == 200


def test_others_see_that_it_is_overdue(client: FlaskClient, poster: User, donor: User) -> None:
    post = closed_days_ago(poster, donor, 30)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "hasn't shared how it went yet." in page
    assert "has until" not in page


@pytest.mark.parametrize(
    ("days", "sent", "count", "after"),
    [
        (2.9, 0, 0, 0),
        (3, 0, 1, 1),
        (3, 1, 0, 1),
        (6, 1, 1, 2),
        (6, 2, 0, 2),
        (6, 0, 1, 2),  # A missed run sends one email, not two.
        (UPDATE_DUE_DAYS, 2, 0, 2),
        (UPDATE_DUE_DAYS, 0, 0, 0),
    ],
)
def test_reminders_go_out_once_on_day_3_and_day_6(
    app: Flask,
    poster: User,
    donor: User,
    caplog: pytest.LogCaptureFixture,
    days: float,
    sent: int,
    count: int,
    after: int,
) -> None:
    post = closed_days_ago(poster, donor, days)
    post.update_reminders_sent = sent
    db.session.commit()
    with caplog.at_level(logging.INFO):
        assert send_update_reminders() == count
    assert reminders(caplog) == count
    assert post.update_reminders_sent == after


def test_reminder_links_to_the_form(
    app: Flask, poster: User, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    post = closed_days_ago(poster, donor, 3)
    with caplog.at_level(logging.INFO):
        send_update_reminders()
    assert f"/posts/{post.id}#update" in caplog.text


def test_no_reminder_once_posted_or_when_nothing_is_owed(
    app: Flask, poster: User, donor: User
) -> None:
    posted = closed_days_ago(poster, donor, 3)
    posted.update_body = NOTE
    posted.update_posted_at = utcnow()
    closed_days_ago(poster, None, 3)
    db.session.commit()
    assert send_update_reminders() == 0


def test_deleted_poster_gets_no_reminder(app: Flask, poster: User, donor: User) -> None:
    closed_days_ago(poster, donor, 3)
    anonymize(poster)
    db.session.commit()
    assert send_update_reminders() == 0


def test_failed_send_is_retried_next_run(
    app: Flask, poster: User, donor: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*_: object) -> None:
        raise smtplib.SMTPException

    post = closed_days_ago(poster, donor, 3)
    monkeypatch.setattr("app.routes.posts.send_email", fail)
    assert send_update_reminders() == 0
    assert post.update_reminders_sent == 0
    monkeypatch.undo()
    assert send_update_reminders() == 1


def test_remind_command(app: Flask, poster: User, donor: User) -> None:
    closed_days_ago(poster, donor, 3)
    result = app.test_cli_runner().invoke(args=["posts", "remind"])
    assert "Update reminder emails sent: 1" in result.output
