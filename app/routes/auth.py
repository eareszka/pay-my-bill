from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from werkzeug.wrappers import Response

from app.auth import login_required
from app.extensions import db
from app.forms import EmptyForm, SignupForm
from app.mail import send_email
from app.models import User, utcnow
from app.tokens import VERIFY_EMAIL, VERIFY_MAX_AGE, make_token, read_token

bp = Blueprint("auth", __name__)


def send_verification(user: User) -> None:
    link = url_for("auth.verify", token=make_token(user.id, VERIFY_EMAIL), _external=True)
    send_email(
        user.email,
        "Verify your Pay My Bill email",
        f"Hi {user.username},\n\nConfirm your email to start posting and donating:\n{link}\n\n"
        "This link expires in 48 hours.",
    )


@bp.route("/signup", methods=["GET", "POST"])
def signup() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = SignupForm()
    if form.validate_on_submit():
        taken = db.session.scalars(
            select(User).where(
                or_(User.username == form.username.data, User.email == form.email.data)
            )
        ).all()
        for other in taken:
            if other.username == form.username.data:
                form.username.errors.append("That username is taken.")
            if other.email == form.email.data:
                form.email.errors.append("An account with that email already exists.")
        if not taken:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data or ""),
            )
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.username.errors.append("That username or email is already in use.")
            else:
                send_verification(user)
                login_user(user)
                flash("Account created. Check your email to verify it.", "success")
                return redirect(url_for("auth.verify_pending"))
    return render_template("auth/signup.html", form=form)


@bp.get("/verify/pending")
@login_required
def verify_pending() -> str | Response:
    if current_user.is_verified:
        return redirect(url_for("main.index"))
    return render_template("auth/verify_pending.html", form=EmptyForm())


@bp.post("/verify/resend")
@login_required
def verify_resend() -> Response:
    if EmptyForm().validate_on_submit() and not current_user.is_verified:
        send_verification(current_user)
        flash("We sent you a new verification link.", "success")
    return redirect(url_for("auth.verify_pending"))


@bp.get("/verify/<token>")
def verify(token: str) -> Response:
    user_id = read_token(token, VERIFY_EMAIL, VERIFY_MAX_AGE)
    user = db.session.get(User, user_id) if user_id is not None else None
    if user is None:
        flash("That verification link is invalid or has expired.", "error")
        return redirect(url_for("main.index"))
    if not user.is_verified:
        user.email_verified_at = utcnow()
        db.session.commit()
    flash("Your email is verified. Welcome!", "success")
    return redirect(url_for("main.index"))
