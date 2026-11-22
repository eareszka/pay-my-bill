from collections import Counter
from pathlib import Path

import pytest
from flask import Flask
from sqlalchemy import func, select

from app.demo import DEMO_LABEL, DEMO_POSTERS, DEMO_WANTS, DemoError, clear_demo, seed_demo
from app.extensions import db
from app.models import (
    MAX_GOAL_CENTS,
    Donation,
    PaymentMethod,
    Post,
    PostKind,
    PostStatus,
    Report,
    ReportReason,
    User,
)
from app.photos import MAX_PHOTOS
from tests.conftest import MakeUser


def count(model: type) -> int:
    return db.session.scalar(select(func.count()).select_from(model)) or 0


def test_seed_adds_labeled_open_wants(app: Flask) -> None:
    assert seed_demo() == len(DEMO_WANTS)
    posts = db.session.scalars(select(Post)).all()
    assert 10 <= len(posts) <= 20
    assert all(p.kind is PostKind.WANT and p.status is PostStatus.OPEN for p in posts)
    assert all(DEMO_LABEL in p.body and 0 < p.goal_cents <= MAX_GOAL_CENTS for p in posts)
    assert max(Counter(p.user_id for p in posts).values()) <= 2
    users = db.session.scalars(select(User)).all()
    assert len(users) == len(DEMO_POSTERS)
    assert all(u.is_verified and u.has_payment_handle for u in users)
    assert all(1 <= len(p.photo_keys) <= MAX_PHOTOS for p in posts)


def test_seed_twice_is_refused(app: Flask) -> None:
    seed_demo()
    with pytest.raises(DemoError, match="already"):
        seed_demo()


def test_seed_refuses_a_taken_username(app: Flask, make_user: MakeUser) -> None:
    make_user(DEMO_POSTERS[0][0])
    with pytest.raises(DemoError, match="taken"):
        seed_demo()


def test_seed_refuses_flagged_wants(app: Flask, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.demo.is_flagged", lambda *texts: True)
    with pytest.raises(DemoError, match="fundraising"):
        seed_demo()
    assert count(Post) == 0


def test_clear_removes_demo_data_and_keeps_real_users(app: Flask, make_user: MakeUser) -> None:
    real = make_user("emery")
    seed_demo()
    post = db.session.scalars(select(Post)).first()
    assert post is not None
    db.session.add_all(
        [
            Donation(post=post, donor=real, amount_cents=500, method=PaymentMethod.VENMO),
            Report(reporter=real, user=post.user, reason=ReportReason.SPAM),
        ]
    )
    db.session.commit()
    stored = [
        Path(app.config["PHOTO_DIR"]) / k
        for p in db.session.scalars(select(Post))
        for k in p.photo_keys
    ]
    assert stored and all(f.exists() for f in stored)
    assert clear_demo() == len(DEMO_WANTS)
    assert not any(f.exists() for f in stored)
    assert (count(Post), count(Donation), count(Report)) == (0, 0, 0)
    assert db.session.scalars(select(User.username)).all() == ["emery"]
    assert clear_demo() == 0


def test_cli_seed_and_clear(app: Flask) -> None:
    runner = app.test_cli_runner()
    assert "Added 16 test wants" in runner.invoke(args=["demo", "seed"]).output
    again = runner.invoke(args=["demo", "seed"])
    assert again.exit_code != 0
    assert "already" in again.output
    assert "Removed 16 test wants" in runner.invoke(args=["demo", "clear"]).output
