from datetime import timedelta

import pytest
from flask import Flask
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import (
    MAX_GOAL_CENTS,
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    PostKind,
    PostStatus,
    User,
    utcnow,
)


def make_user(username: str = "alice", email: str = "alice@example.com") -> User:
    return User(username=username, email=email, password_hash="x")  # noqa: S106


def make_post(user: User, goal_cents: int = 5_000) -> Post:
    return Post(
        user=user, kind=PostKind.NEED, title="Rent", body="Short on rent.", goal_cents=goal_cents
    )


def test_user_defaults(app: Flask) -> None:
    user = make_user()
    db.session.add(user)
    db.session.commit()
    assert user.is_admin is False
    assert user.created_at is not None
    assert user.is_verified is False
    assert user.has_payment_handle is False


def test_user_verified_and_payment_handle(app: Flask) -> None:
    user = make_user()
    user.email_verified_at = utcnow()
    user.venmo_handle = "@alice"
    assert user.is_verified is True
    assert user.has_payment_handle is True


@pytest.mark.parametrize("field", ["username", "email"])
def test_user_unique_fields(app: Flask, field: str) -> None:
    db.session.add(make_user())
    db.session.commit()
    other = make_user("bob", "bob@example.com")
    setattr(other, field, getattr(make_user(), field))
    db.session.add(other)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_post_defaults_and_relationship(app: Flask) -> None:
    user = make_user()
    post = make_post(user)
    db.session.add(post)
    db.session.commit()
    assert post.status is PostStatus.OPEN
    assert post.created_at is not None
    assert post.updated_at is not None
    assert user.posts == [post]


def test_post_enums_stored_as_values(app: Flask) -> None:
    db.session.add(make_post(make_user()))
    db.session.commit()
    row = db.session.execute(text("SELECT kind, status FROM posts")).one()
    assert tuple(row) == ("need", "open")


def test_post_progress_starts_at_zero(app: Flask) -> None:
    post = make_post(make_user())
    assert (post.raised_cents, post.progress_percent) == (0, 0)


def test_post_goal_at_cap_is_allowed(app: Flask) -> None:
    db.session.add(make_post(make_user(), goal_cents=MAX_GOAL_CENTS))
    db.session.commit()


@pytest.mark.parametrize("goal_cents", [0, -100, MAX_GOAL_CENTS + 1])
def test_post_goal_out_of_range_rejected(app: Flask, goal_cents: int) -> None:
    db.session.add(make_post(make_user(), goal_cents=goal_cents))
    with pytest.raises(IntegrityError):
        db.session.commit()


def make_donation(post: Post, donor: User, cents: int, status: DonationStatus) -> Donation:
    return Donation(
        post=post, donor=donor, amount_cents=cents, method=PaymentMethod.CASHAPP, status=status
    )


def test_donation_defaults_to_pending(app: Flask) -> None:
    post = make_post(make_user())
    donation = Donation(
        post=post,
        donor=make_user("bob", "bob@example.com"),
        amount_cents=500,
        method=PaymentMethod.VENMO,
    )
    db.session.add(donation)
    db.session.commit()
    assert donation.status is DonationStatus.PENDING
    assert donation.resolved_at is None
    assert post.donations == [donation]


def test_raised_counts_only_confirmed(app: Flask) -> None:
    post = make_post(make_user(), goal_cents=10_000)
    donor = make_user("bob", "bob@example.com")
    for cents, status in [
        (2_000, DonationStatus.CONFIRMED),
        (500, DonationStatus.CONFIRMED),
        (4_000, DonationStatus.PENDING),
        (3_000, DonationStatus.DISPUTED),
    ]:
        make_donation(post, donor, cents, status)
    assert (post.raised_cents, post.progress_percent) == (2_500, 25)


def test_progress_caps_at_100(app: Flask) -> None:
    post = make_post(make_user(), goal_cents=1_000)
    make_donation(post, make_user("bob", "bob@example.com"), 1_500, DonationStatus.CONFIRMED)
    assert post.progress_percent == 100


@pytest.mark.parametrize("cents", [0, -1, MAX_GOAL_CENTS + 1])
def test_donation_amount_out_of_range_rejected(app: Flask, cents: int) -> None:
    post = make_post(make_user())
    db.session.add(
        make_donation(post, make_user("bob", "bob@example.com"), cents, DonationStatus.PENDING)
    )
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_deleting_post_deletes_its_gifts(app: Flask) -> None:
    post = make_post(make_user())
    make_donation(post, make_user("bob", "bob@example.com"), 500, DonationStatus.PENDING)
    db.session.add(post)
    db.session.commit()
    db.session.delete(post)
    db.session.commit()
    assert db.session.scalar(text("SELECT count(*) FROM donations")) == 0


def test_status_and_method_labels() -> None:
    assert [s.label for s in DonationStatus] == ["Waiting", "Confirmed", "Not received"]
    assert [m.label for m in PaymentMethod] == ["Cash App", "Venmo", "PayPal"]


@pytest.mark.parametrize(
    ("days_old", "status", "expired"),
    [
        (13.9, DonationStatus.PENDING, False),
        (14.1, DonationStatus.PENDING, True),
        (30, DonationStatus.CONFIRMED, False),
        (30, DonationStatus.DISPUTED, False),
    ],
)
def test_gift_expiry(days_old: float, status: DonationStatus, expired: bool) -> None:
    created = utcnow() - timedelta(days=days_old)
    for created_at in (created, created.replace(tzinfo=None)):
        gift = Donation(
            amount_cents=500, method=PaymentMethod.VENMO, status=status, created_at=created_at
        )
        assert gift.is_expired is expired
        assert gift.status_label == ("Expired" if expired else status.label)
        assert gift.status_class == ("expired" if expired else status.value)


def test_unsaved_gift_is_not_expired() -> None:
    gift = Donation(amount_cents=500, method=PaymentMethod.VENMO, status=DonationStatus.PENDING)
    assert (gift.is_expired, gift.status_label) == (False, "Waiting")
