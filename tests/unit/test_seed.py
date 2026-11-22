from collections import Counter
from pathlib import Path

import pytest
from flask import Flask
from sqlalchemy import select

from app.demo import DEMO_WANTS
from app.extensions import db
from app.models import MAX_GOAL_CENTS, Donation, DonationStatus, Post, PostStatus, User
from app.photos import MAX_PHOTOS
from app.seed import SEED_PHOTO_DIR, SEED_PHOTOS, SeedError, seed


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


def test_seed_adds_gifts_without_funding_open_posts(app: Flask) -> None:
    seed()
    donations = db.session.scalars(select(Donation)).all()
    assert {d.status for d in donations} == set(DonationStatus)
    assert all(d.donor_id != d.post.user_id for d in donations)
    assert all(d.post.raised_cents < d.post.goal_cents for d in donations)
    assert all(d.resolved_at is None or d.resolved_at > d.created_at for d in donations)


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


def test_seeded_closed_posts_have_a_close_date(app: Flask) -> None:
    seed()
    posts = db.session.scalars(select(Post)).all()
    assert all(
        (post.closed_at is not None) == (post.status in (PostStatus.FUNDED, PostStatus.CLOSED))
        for post in posts
    )


def test_seed_gives_each_known_post_its_photos(app: Flask) -> None:
    seed()
    posts = db.session.scalars(select(Post)).all()
    assert all(bool(p.photo_key) == (p.title in SEED_PHOTOS) for p in posts)
    with_photos = [p for p in posts if p.photo_key]
    assert with_photos
    for post in with_photos:
        assert 1 <= len(post.photo_keys) <= MAX_PHOTOS
        assert all((Path(app.config["PHOTO_DIR"]) / key).exists() for key in post.photo_keys)


def test_every_photo_subject_has_up_to_five_credited_photos() -> None:
    sources = (SEED_PHOTO_DIR / "SOURCES.md").read_text(encoding="utf-8")
    subjects = {p.name for p in SEED_PHOTO_DIR.iterdir() if p.is_dir()}
    assert set(SEED_PHOTOS.values()) | set(s for *_, s in DEMO_WANTS) == subjects
    for subject in subjects:
        files = sorted((SEED_PHOTO_DIR / subject).glob("*.jpg"))
        assert 1 <= len(files) <= MAX_PHOTOS, subject
        assert all(f"{subject}/{f.name}" in sources for f in files), subject
