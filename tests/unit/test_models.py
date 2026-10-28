import pytest
from flask import Flask
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import MAX_GOAL_CENTS, Post, PostKind, PostStatus, User, utcnow


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
