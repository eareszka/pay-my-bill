from datetime import timedelta

from flask import Flask
from sqlalchemy import select

from app.auth import KEEP_ATTEMPTS, prune_login_attempts
from app.extensions import db
from app.models import LoginAttempt, utcnow


def add(identifier: str, age: timedelta) -> None:
    db.session.add(
        LoginAttempt(
            identifier=identifier, ip="1.2.3.4", succeeded=False, created_at=utcnow() - age
        )
    )
    db.session.commit()


def test_prune_keeps_rows_a_limit_can_still_use(app: Flask) -> None:
    with app.app_context():
        add("old", KEEP_ATTEMPTS + timedelta(minutes=1))
        add("recent", timedelta(hours=2))
        assert prune_login_attempts() == 1
        assert list(db.session.scalars(select(LoginAttempt.identifier))) == ["recent"]


def test_prune_command(app: Flask) -> None:
    with app.app_context():
        add("old", KEEP_ATTEMPTS * 2)
    result = app.test_cli_runner().invoke(args=["auth", "prune"])
    assert "Old login attempts deleted: 1" in result.output
