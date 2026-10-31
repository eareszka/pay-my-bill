from app.extensions import db
from app.models import DonationStatus, Post, PostStatus, User

DELETED_TITLE = "Deleted post"
DELETED_BODY = "The poster deleted this post."


def has_confirmed_gifts(post: Post) -> bool:
    return any(d.status == DonationStatus.CONFIRMED for d in post.donations)


def delete_post(post: Post) -> None:
    # Donors keep credit for confirmed gifts, so those posts lose their story but stay (T14).
    if has_confirmed_gifts(post):
        post.title = DELETED_TITLE
        post.body = DELETED_BODY
        post.status = PostStatus.CLOSED
    else:
        db.session.delete(post)


def anonymize(user: User) -> None:
    for post in list(user.posts):
        delete_post(post)
    user.username = f"deleted-{user.id}"
    user.email = f"deleted-{user.id}@deleted.invalid"
    user.password_hash = "!"  # noqa: S105 - not a hash, so no password matches
    user.email_verified_at = None
    user.city = user.state = None
    user.cashapp_handle = user.venmo_handle = user.paypal_handle = None
