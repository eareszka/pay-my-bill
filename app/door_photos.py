"""Photos from real posts for the home page doors (#120).

The help door shows open asks and the ask door shows asks that got funded. Only posts
from verified, active accounts that have never been reported can appear, and a door
shows nothing until it has enough photos to fill it. Any report, on the account or on any
of its posts, keeps all of that account's photos off the doors.
"""

from sqlalchemy import select

from app.extensions import db
from app.models import DELETED_EMAIL_DOMAIN, Post, PostStatus, Report, User, open_posts

DOOR_PHOTOS = 6


def door_photos(funded: bool) -> list[str]:
    shown = open_posts() if not funded else Post.status == PostStatus.FUNDED
    reported_users = select(Report.user_id).where(Report.user_id.is_not(None))
    reported_posters = select(Post.user_id).join(Report, Report.post_id == Post.id).correlate(None)
    keys = db.session.scalars(
        select(Post.photo_key)
        .join(Post.user)
        .where(
            shown,
            Post.photo_key.is_not(None),
            User.id.not_in(reported_users),
            User.id.not_in(reported_posters),
            User.email_verified_at.is_not(None),
            User.banned_at.is_(None),
            ~User.email.endswith(DELETED_EMAIL_DOMAIN),
        )
        .order_by(Post.created_at.desc(), Post.id.desc())
        .limit(DOOR_PHOTOS)
    ).all()
    return [key for key in keys if key] if len(keys) == DOOR_PHOTOS else []
