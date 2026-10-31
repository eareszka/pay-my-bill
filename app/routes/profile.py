import smtplib

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, logout_user
from sqlalchemy import select
from werkzeug.security import check_password_hash
from werkzeug.wrappers import Response

from app.accounts import anonymize
from app.auth import begin_login_attempt, login_required, mark_login_succeeded
from app.extensions import db
from app.forms import DeleteAccountForm, ProfileForm
from app.mail import send_email
from app.models import User
from app.rewards import confirmed_gifts, progress

bp = Blueprint("profile", __name__)

DISPLAY_PREFIX = {"PayPal": "paypal.me/"}

HANDLE_FIELDS = {
    "cashapp_handle": "Cash App",
    "venmo_handle": "Venmo",
    "paypal_handle": "PayPal",
}


def send_handle_change_notice(
    user: User, changes: dict[str, tuple[str | None, str | None]]
) -> None:
    def show(label: str, handle: str | None) -> str:
        return DISPLAY_PREFIX.get(label, "") + handle if handle else "(none)"

    lines = [
        f"- {label}: {show(label, old)} -> {show(label, new)}"
        for label, (old, new) in changes.items()
    ]
    body = (
        f"Hi {user.username},\n\nThe payment handles on your Pay My Bill account just changed:\n"
        + "\n".join(lines)
        + "\n\nIf this wasn't you, change your password right away and contact us."
    )
    try:
        send_email(user.email, "Your payment handles changed", body)
    except (smtplib.SMTPException, OSError):
        current_app.logger.exception("Could not send the handle-change notice to user %s", user.id)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def edit() -> str | Response:
    user: User = current_user
    form = ProfileForm(obj=user)
    if form.validate_on_submit():
        changes: dict[str, tuple[str | None, str | None]] = {}
        for field, label in HANDLE_FIELDS.items():
            old, new = getattr(user, field), form[field].data or None
            if old != new:
                changes[label] = (old, new)
                setattr(user, field, new)
        user.city = form.city.data or None
        user.state = form.state.data or None
        db.session.commit()
        if changes:
            send_handle_change_notice(user, changes)
        flash("Profile saved.", "success")
        return redirect(url_for("profile.edit"))
    return render_template("profile/edit.html", form=form, delete_form=DeleteAccountForm())


@bp.post("/account/delete")
@login_required
def delete_account() -> str | Response | tuple[str, int]:
    user: User = current_user
    delete_form = DeleteAccountForm()
    if delete_form.validate_on_submit():
        # Same throttle as login, so a stolen session can't guess the password.
        attempt = begin_login_attempt(user.username, request.remote_addr)
        if attempt is None:
            delete_form.password.errors.append("Too many failed attempts. Try again later.")
        elif check_password_hash(user.password_hash, delete_form.password.data or ""):
            mark_login_succeeded(attempt)
            anonymize(user)
            db.session.commit()
            logout_user()
            flash("Your account was deleted.", "success")
            return redirect(url_for("main.index"))
        else:
            delete_form.password.errors.append("That password isn't right.")
    page = render_template("profile/edit.html", form=ProfileForm(obj=user), delete_form=delete_form)
    return page, 400


@bp.get("/u/<username>")
def show(username: str) -> str:
    user = db.session.scalar(select(User).where(User.username == username.lower()))
    if user is None or not user.is_verified:
        abort(404)
    return render_template("profile/show.html", user=user, progress=progress(confirmed_gifts(user)))
