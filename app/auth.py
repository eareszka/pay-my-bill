from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, cast

import flask_login
from flask import flash, redirect, request, url_for
from flask_login import current_user
from sqlalchemy import ColumnElement, func, select
from werkzeug.wrappers import Response

from app.extensions import db, login_manager
from app.models import LoginAttempt, User, utcnow

MAX_FAILED_LOGINS = 5
MAX_FAILED_LOGINS_PER_IP = 20
LOGIN_WINDOW = timedelta(minutes=15)


def load_user(user_id: str) -> User | None:
    try:
        return db.session.get(User, int(user_id))
    except ValueError:
        return None


def unauthorized() -> Response:
    flash("Please log in to continue.", "info")
    # A POST-only page can't be reopened with the GET that follows login.
    next_ = request.full_path.rstrip("?") if request.method == "GET" else None
    return redirect(url_for("auth.login", next=next_))


login_manager.user_loader(load_user)
login_manager.unauthorized_handler(unauthorized)


def _failures_since(since: datetime, *where: ColumnElement[bool]) -> int:
    count = db.session.scalar(
        select(func.count())
        .select_from(LoginAttempt)
        .where(*where, LoginAttempt.succeeded.is_(False), LoginAttempt.created_at >= since)
    )
    return count or 0


def begin_login_attempt(identifier: str, ip: str | None) -> LoginAttempt | None:
    """Record the attempt as failed, then return it unless the caller is rate-limited.

    Inserting before counting means concurrent requests can't all slip under the limit.
    """
    attempt = LoginAttempt(identifier=identifier, ip=ip, succeeded=False)
    db.session.add(attempt)
    db.session.commit()
    window_start = utcnow() - LOGIN_WINDOW
    same_caller = (LoginAttempt.identifier == identifier, LoginAttempt.ip == ip)
    last_success = db.session.scalar(
        select(func.max(LoginAttempt.created_at)).where(
            *same_caller, LoginAttempt.succeeded.is_(True), LoginAttempt.created_at >= window_start
        )
    )
    if (
        _failures_since(last_success or window_start, *same_caller) > MAX_FAILED_LOGINS
        or _failures_since(window_start, LoginAttempt.ip == ip) > MAX_FAILED_LOGINS_PER_IP
    ):
        return None
    return attempt


def mark_login_succeeded(attempt: LoginAttempt) -> None:
    attempt.succeeded = True
    db.session.commit()


def login_required[F: Callable[..., Any]](view: F) -> F:
    return cast(F, flask_login.login_required(view))


def verified_required[F: Callable[..., Any]](view: F) -> F:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if not current_user.is_verified:
            return redirect(url_for("auth.verify_pending"))
        return view(*args, **kwargs)

    return login_required(cast(F, wrapped))
