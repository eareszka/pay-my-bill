"""Blocking another user (#257, App Store Guideline 1.2).

A block works both ways: neither person sees the other's posts in the feed, opens them,
or chips in or reacts to them. It's silent, so the blocked person is never told.
"""

from typing import Any

from flask import has_request_context
from flask_login import current_user
from sqlalchemy import ColumnElement, and_, exists, or_, select, true

from app.extensions import db
from app.models import Block, Post, User


def _between(a: Any, b: Any) -> ColumnElement[bool]:
    return exists().where(
        or_(
            and_(Block.blocker_id == a, Block.blocked_id == b),
            and_(Block.blocker_id == b, Block.blocked_id == a),
        )
    )


def apart(a: User | None, b_id: int) -> bool:
    return a is not None and a.id != b_id and bool(db.session.scalar(select(_between(a.id, b_id))))


def signed_in() -> bool:
    # Jobs and the CLI have no viewer, so nothing is hidden there.
    return has_request_context() and current_user.is_authenticated


def viewer_apart(user_id: int) -> bool:
    return signed_in() and apart(current_user, user_id)


def visible_posts() -> ColumnElement[bool]:
    """Posts the current viewer may see in the feed."""
    if not signed_in():
        return true()
    return ~_between(current_user.id, Post.user_id)


def is_blocking(user: User, other: User) -> bool:
    return bool(
        db.session.scalar(
            select(exists().where(Block.blocker_id == user.id, Block.blocked_id == other.id))
        )
    )


def blocked_by(user: User) -> list[User]:
    return list(
        db.session.scalars(
            select(User)
            .join(Block, Block.blocked_id == User.id)
            .where(Block.blocker_id == user.id)
            .order_by(User.username)
        )
    )
