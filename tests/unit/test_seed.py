from collections import Counter

import pytest
from flask import Flask
from sqlalchemy import select

from app.extensions import db
from app.models import MAX_GOAL_CENTS, Post, PostStatus, User
from app.seed import SeedError, seed


def test_seed_creates_users_and_posts(app: Flask) -> None:
    assert seed() == (10, 20)
    users = db.session.scalars(select(User)).all()
    posts = db.session.scalars(select(Post)).all()
    assert len(users) == 10
    assert len(posts) == 20
    assert len({u.username for u in users}) == 10
    assert all(u.is_verified and u.has_payment_handle for u in users)
    assert all(0 < p.goal_cents <= MAX_GOAL_CENTS for p in posts)


def test_seed_respects_open_post_limit(app: Flask) -> None:
    seed()
    open_posts = db.session.scalars(select(Post).where(Post.status == PostStatus.OPEN)).all()
    assert open_posts
    assert max(Counter(p.user_id for p in open_posts).values()) <= 2


def test_seed_includes_pending_review_post(app: Flask) -> None:
    seed()
    statuses = set(db.session.scalars(select(Post.status)))
    assert PostStatus.PENDING_REVIEW in statuses


def test_seed_extra_users_get_unique_names(app: Flask) -> None:
    assert seed(n_users=12, posts_per_user=1) == (12, 12)
    assert len(set(db.session.scalars(select(User.username)))) == 12


def test_seed_refuses_twice(app: Flask) -> None:
    seed()
    with pytest.raises(SeedError, match="already has users"):
        seed()


def test_seed_refuses_non_sqlite(app: Flask) -> None:
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg://staging/db"
    with pytest.raises(SeedError, match="SQLite"):
        seed()


def test_seed_cli(app: Flask) -> None:
    runner = app.test_cli_runner()
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0
    assert "Seeded 10 users and 20 posts" in result.output
    again = runner.invoke(args=["seed"])
    assert again.exit_code == 1
    assert "refusing to seed twice" in again.output
