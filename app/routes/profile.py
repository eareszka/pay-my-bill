import smtplib

from flask import Blueprint, abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import select
from werkzeug.wrappers import Response

from app.auth import login_required
from app.extensions import db
from app.forms import ProfileForm
from app.mail import send_email
from app.models import User

bp = Blueprint("profile", __name__)

HANDLE_FIELDS = {
    "cashapp_handle": "Cash App",
    "venmo_handle": "Venmo",
    "paypal_handle": "PayPal",
}


def send_handle_change_notice(
    user: User, changes: dict[str, tuple[str | None, str | None]]
) -> None:
    lines = [
        f"- {label}: {old or '(none)'} -> {new or '(none)'}"
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
    return render_template("profile/edit.html", form=form)


@bp.get("/u/<username>")
def show(username: str) -> str:
    user = db.session.scalar(select(User).where(User.username == username.lower()))
    if user is None:
        abort(404)
    return render_template("profile/show.html", user=user)
