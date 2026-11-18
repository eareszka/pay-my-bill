"""Categories a viewer asked to see less of (#119, ADR 0018).

Logged in, the choice lives on the account. Logged out, it lives in a cookie that
joins the account at the next log in.
"""

from flask import current_app, request
from flask_login import current_user
from werkzeug.wrappers import Response

from app.extensions import db
from app.models import PostCategory, User

COOKIE = "show_less"
COOKIE_DAYS = 365
VALUES = {category.value for category in PostCategory}


def parse(raw: str | None) -> set[PostCategory]:
    # The cookie is the viewer's to edit, so anything unknown is dropped.
    return {PostCategory(value) for value in (raw or "").split(",") if value in VALUES}


def dump(categories: set[PostCategory]) -> str | None:
    return ",".join(sorted(categories)) or None


def chosen() -> set[PostCategory]:
    if current_user.is_authenticated:
        return parse(current_user.show_less)
    return parse(request.cookies.get(COOKIE))


def save(categories: set[PostCategory], response: Response) -> None:
    if current_user.is_authenticated:
        current_user.show_less = dump(categories)
        db.session.commit()
    elif raw := dump(categories):
        response.set_cookie(
            COOKIE,
            raw,
            max_age=COOKIE_DAYS * 24 * 3600,
            httponly=True,
            samesite="Lax",
            secure=current_app.config["SESSION_COOKIE_SECURE"],
        )
    else:
        response.delete_cookie(COOKIE)


def join_account(user: User, response: Response) -> None:
    """Fold a logged-out choice into the account at log in."""
    if COOKIE not in request.cookies:
        return
    user.show_less = dump(parse(user.show_less) | parse(request.cookies[COOKIE]))
    db.session.commit()
    response.delete_cookie(COOKIE)
