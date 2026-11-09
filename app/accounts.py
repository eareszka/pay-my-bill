from sqlalchemy import delete

from app.extensions import db
from app.models import (
    DELETED_EMAIL_DOMAIN,
    DELETED_POST_BODY,
    DELETED_POST_TITLE,
    LoginAttempt,
    Post,
    PostStatus,
    Reaction,
    User,
)


def delete_post(post: Post) -> str | None:
    """Delete or scrub a post. Returns its photo key, to discard once the change commits."""
    photo_key, post.photo_key = post.photo_key, None
    # Any recorded gift keeps the post as a scrubbed shell, so donors keep their
    # credit and their "I sent it" record (T14). Only gift-free posts are removed.
    if not post.donations:
        db.session.delete(post)
        return photo_key
    post.title = DELETED_POST_TITLE
    post.body = DELETED_POST_BODY
    post.update_body = None  # update_posted_at stays: the update was still made
    if post.status == PostStatus.OPEN:
        post.close()
    return photo_key


def anonymize(user: User) -> list[str]:
    """Scrub an account. Returns photo keys to discard once the change commits."""
    photo_keys = [key for post in list(user.posts) if (key := delete_post(post))]
    db.session.execute(
        delete(LoginAttempt).where(LoginAttempt.identifier.in_((user.username, user.email)))
    )
    db.session.execute(delete(Reaction).where(Reaction.user_id == user.id))
    user.username = f"deleted-{user.id}"
    user.email = f"deleted-{user.id}{DELETED_EMAIL_DOMAIN}"
    user.password_hash = "!"  # noqa: S105 - not a hash, so no password matches
    user.email_verified_at = None
    user.city = user.state = None
    user.cashapp_handle = user.venmo_handle = user.paypal_handle = None
    return photo_keys
