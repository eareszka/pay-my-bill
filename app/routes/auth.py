import hmac
from functools import cache
from urllib.parse import urlsplit

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.wrappers import Response

from app.auth import (
    LOGIN_WINDOW,
    allow_verification_email,
    begin_login_attempt,
    login_required,
    mark_login_succeeded,
)
from app.extensions import db
from app.forms import EmptyForm, LoginForm, ResetPasswordForm, ResetRequestForm, SignupForm
from app.mail import send_later
from app.models import LoginAttempt, User, utcnow
from app.tokens import (
    RESET_MAX_AGE,
    RESET_PASSWORD,
    VERIFY_EMAIL,
    VERIFY_MAX_AGE,
    make_token,
    password_digest,
    read_token,
)

bp = Blueprint("auth", __name__)


@cache
def _dummy_hash() -> str:
    # Checked when no user matches, so a miss takes as long as a wrong password.
    return generate_password_hash("not-a-real-password")


def safe_next(target: str | None) -> str:
    if target and target.startswith("/") and "\\" not in target:
        parts = urlsplit(target)
        if not parts.scheme and not parts.netloc:
            return target
    return url_for("main.index")


def send_verification(user: User) -> bool:
    if not allow_verification_email(user.id):
        return False
    token = make_token(user.id, user.email, VERIFY_EMAIL)
    link = url_for("auth.verify", token=token, _external=True)
    send_later(
        user.email,
        "Verify your Pay My Bill email",
        f"Hi {user.username},\n\nConfirm your email to start posting and chipping in:\n{link}\n\n"
        "This link expires in 48 hours.",
    )
    return True


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
                adult_attested_at=utcnow(),
            )
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.username.errors.append("That username or email is already in use.")
            else:
                session.clear()
                login_user(user)
                # Verifying takes a trip to their email; afterwards, back to what they were doing.
                if request.args.get("next"):
                    session["after_verify"] = safe_next(request.args.get("next"))
                send_verification(user)
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
        if send_verification(current_user):
            flash("We sent you a new verification link.", "success")
        else:
            flash(
                "We've sent a few links already. Check your spam or junk folder, "
                "or try again in an hour.",
                "error",
            )
    return redirect(url_for("auth.verify_pending"))


@bp.get("/verify/<token>")
def verify(token: str) -> Response:
    payload = read_token(token, VERIFY_EMAIL, VERIFY_MAX_AGE)
    user = db.session.get(User, payload[0]) if payload else None
    if user is None or payload is None or user.email != payload[1]:
        flash("That verification link is invalid or has expired.", "error")
        return redirect(url_for("main.index"))
    if not user.is_verified:
        user.email_verified_at = utcnow()
        db.session.commit()
    flash("Your email is verified. Welcome!", "success")
    return redirect(session.pop("after_verify", url_for("main.index")))


@bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response | tuple[str, int, dict[str, str]]:
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.identifier.data or ""
        user = db.session.scalar(
            select(User).where(or_(User.username == identifier, User.email == identifier))
        )
        if user is not None:
            identifier = user.username
        attempt = begin_login_attempt(identifier, request.remote_addr)
        if attempt is None:
            form.password.errors.append("Too many failed attempts. Try again later.")
            retry_after = str(int(LOGIN_WINDOW.total_seconds()))
            return render_template("auth/login.html", form=form), 429, {"Retry-After": retry_after}
        password = form.password.data or ""
        ok = check_password_hash(user.password_hash if user else _dummy_hash(), password)
        if user is not None and ok and user.is_banned:
            form.password.errors.append("This account has been suspended.")
            return render_template("auth/login.html", form=form)
        if user is not None and ok:
            mark_login_succeeded(attempt)
            session.clear()
            login_user(user)
            next_page = safe_next(request.args.get("next"))
            if not user.is_verified and request.args.get("next"):
                session["after_verify"] = next_page
            return redirect(next_page)
        form.password.errors.append("Wrong username, email, or password.")
    return render_template("auth/login.html", form=form)


RESET_SENT = (
    "If an account uses that email, we sent it a link to reset the password. "
    "Not there after a minute? Check your spam or junk folder."
)


@bp.route("/reset", methods=["GET", "POST"])
def reset_request() -> str | Response | tuple[str, int, dict[str, str]]:
    form = ResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data or ""
        if begin_login_attempt(f"reset:{email}", request.remote_addr) is None:
            form.email.errors.append("Too many requests. Try again later.")
            retry_after = str(int(LOGIN_WINDOW.total_seconds()))
            return (
                render_template("auth/reset_request.html", form=form),
                429,
                {"Retry-After": retry_after},
            )
        user = db.session.scalar(select(User).where(User.email == email))
        if user is not None and not user.is_deleted:
            # Bound to a digest of the password hash, so the link stops working
            # once it's used without carrying the hash itself.
            token = make_token(user.id, password_digest(user.password_hash), RESET_PASSWORD)
            link = url_for("auth.reset_password", token=token, _external=True)
            send_later(
                user.email,
                "Reset your Pay My Bill password",
                f"Hi {user.username},\n\nSet a new password here:\n{link}\n\n"
                "This link expires in 1 hour and works once. If you didn't ask for it, "
                "you can ignore this email.",
            )
        flash(RESET_SENT, "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_request.html", form=form)


@bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token: str) -> str | Response:
    payload = read_token(token, RESET_PASSWORD, RESET_MAX_AGE)
    user = db.session.get(User, payload[0]) if payload else None
    if (
        user is None
        or payload is None
        or user.is_deleted
        or not hmac.compare_digest(password_digest(user.password_hash), payload[1])
    ):
        flash("That reset link is invalid, expired, or already used.", "error")
        return redirect(url_for("auth.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data or "")
        # Logs out everyone, including whoever signed up with this email before
        # its owner claimed it (#130).
        user.end_sessions()
        # The link came through their inbox, which proves the email. Whoever
        # set the account up before that may not be them, so their payment
        # handles and region go (#133).
        claimed = not user.is_verified
        if claimed:
            user.email_verified_at = utcnow()
            claimed = any(
                (user.cashapp_handle, user.venmo_handle, user.paypal_handle, user.city, user.state)
            )
            user.cashapp_handle = user.venmo_handle = user.paypal_handle = None
            user.city = user.state = None
        # Clears a lockout from the guesses that led here.
        db.session.add(
            LoginAttempt(identifier=user.username, ip=request.remote_addr, succeeded=True)
        )
        db.session.commit()
        send_later(
            user.email,
            "Your Pay My Bill password changed",
            f"Hi {user.username},\n\nYour password was just changed. If this wasn't you, "
            f"reset it again at {url_for('auth.reset_request', _external=True)} and tell us.",
        )
        logout_user()
        flash("Your password is changed. Log in with the new one.", "success")
        if claimed:
            flash(
                "This account was set up before you confirmed your email, so we cleared "
                "its payment handles and city. Add yours on your profile.",
                "info",
            )
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_form.html", form=form)


@bp.post("/logout")
def logout() -> Response:
    logout_user()
    flash("You're logged out.", "info")
    return redirect(url_for("main.index"))
