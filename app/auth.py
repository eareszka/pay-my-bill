from collections.abc import Callable
from functools import wraps
from typing import Any, cast

import flask_login
from flask import redirect, url_for
from flask_login import current_user

from app.extensions import db, login_manager
from app.models import User


def load_user(user_id: str) -> User | None:
    try:
        return db.session.get(User, int(user_id))
    except ValueError:
        return None


login_manager.user_loader(load_user)


def login_required[F: Callable[..., Any]](view: F) -> F:
    return cast(F, flask_login.login_required(view))


def verified_required[F: Callable[..., Any]](view: F) -> F:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if not current_user.is_verified:
            return redirect(url_for("auth.verify_pending"))
        return view(*args, **kwargs)

    return login_required(cast(F, wrapped))
