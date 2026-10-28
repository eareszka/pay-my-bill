from collections.abc import Callable
from datetime import timedelta
from functools import wraps
from typing import Any, cast

import flask_login
from flask import redirect, url_for
from flask_login import current_user
from sqlalchemy import func, select

from app.extensions import db, login_manager
from app.models import LoginAttempt, User, utcnow

MAX_FAILED_LOGINS = 5
LOGIN_WINDOW = timedelta(minutes=15)


def load_user(user_id: str) -> User | None:
    try:
        return db.session.get(User, int(user_id))
    except ValueError:
        return None


login_manager.user_loader(load_user)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def is_locked_out(identifier: str) -> bool:
    failures = db.session.scalar(
        select(func.count())
        .select_from(LoginAttempt)
        .where(
            LoginAttempt.identifier == identifier,
            LoginAttempt.succeeded.is_(False),
            LoginAttempt.created_at >= utcnow() - LOGIN_WINDOW,
        )
    )
    return (failures or 0) >= MAX_FAILED_LOGINS


def record_login_attempt(identifier: str, ip: str | None, succeeded: bool) -> None:
    db.session.add(LoginAttempt(identifier=identifier, ip=ip, succeeded=succeeded))
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
