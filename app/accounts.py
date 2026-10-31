from sqlalchemy import delete

from app.extensions import db
from app.models import (
    DELETED_EMAIL_DOMAIN,
    DELETED_POST_BODY,
    DELETED_POST_TITLE,
    LoginAttempt,
    Post,
    PostStatus,
    User,
)


def delete_post(post: Post) -> None:
    # Any recorded gift keeps the post as a scrubbed shell, so donors keep their
    # credit and their "I sent it" record (T14). Only gift-free posts are removed.
    if not post.donations:
        db.session.delete(post)
        return
    post.title = DELETED_POST_TITLE
    post.body = DELETED_POST_BODY
    if post.status == PostStatus.OPEN:
        post.status = PostStatus.CLOSED


def anonymize(user: User) -> None:
    for post in list(user.posts):
        delete_post(post)
    db.session.execute(
        delete(LoginAttempt).where(LoginAttempt.identifier.in_((user.username, user.email)))
    )
    user.username = f"deleted-{user.id}"
    user.email = f"deleted-{user.id}{DELETED_EMAIL_DOMAIN}"
    user.password_hash = "!"  # noqa: S105 - not a hash, so no password matches
    user.email_verified_at = None
    user.city = user.state = None
    user.cashapp_handle = user.venmo_handle = user.paypal_handle = None
