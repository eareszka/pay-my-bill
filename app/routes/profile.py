import stripe
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

from app import photos, stripe_pay
from app.accounts import anonymize
from app.auth import begin_login_attempt, login_required, mark_login_succeeded
from app.extensions import db
from app.forms import DeleteAccountForm, ProfileForm
from app.mail import send_later
from app.models import (
    DELETED_POST_BODY,
    DELETED_POST_TITLE,
    PUBLIC_STATUSES,
    Post,
    PostStatus,
    User,
)
from app.rewards import badges, confirmed_gifts, follow_through, progress, streak
from app.routes import gifts as gift_routes

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
    send_later(user.email, "Your payment handles changed", body)


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
    if stripe_pay.enabled() and user.stripe_account_id and not user.stripe_ready:
        # Onboarding can finish later from Stripe's side, so check again while it's pending.
        try:
            stripe_pay.refresh_ready(user)
            db.session.commit()
        except stripe.StripeError:
            current_app.logger.exception("Stripe status check failed for user %s", user.id)
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
            photo_keys = anonymize(user)
            db.session.commit()
            for key in photo_keys:
                photos.discard(key)
            logout_user()
            flash("Your account was deleted.", "success")
            return redirect(url_for("main.index"))
        else:
            delete_form.password.errors.append("That password isn't right.")
    page = render_template("profile/edit.html", form=ProfileForm(obj=user), delete_form=delete_form)
    return page, 400


PROFILE_POST_LIMIT = 20


@bp.get("/u/<username>")
def show(username: str) -> str:
    user = db.session.scalar(select(User).where(User.username == username.lower()))
    is_owner = user is not None and current_user.is_authenticated and current_user.id == user.id
    if user is None or not (user.is_verified or is_owner):
        abort(404)
    gifts = confirmed_gifts(user)
    stats = progress(gifts)
    shown = [*PUBLIC_STATUSES, PostStatus.PENDING_REVIEW] if is_owner else PUBLIC_STATUSES
    posts = db.session.scalars(
        select(Post)
        .where(
            Post.user_id == user.id,
            Post.status.in_(shown),
            ~((Post.title == DELETED_POST_TITLE) & (Post.body == DELETED_POST_BODY)),
        )
        .order_by(Post.created_at.desc(), Post.id.desc())
        .limit(PROFILE_POST_LIMIT)
    ).all()
    tab = "chipped" if is_owner and request.args.get("tab") == "chipped" else "posts"
    return render_template(
        "profile/show.html",
        user=user,
        progress=stats,
        streak=streak(gifts),
        badges=badges(user, gifts, stats.people_helped),
        follow_through=follow_through(user),
        posts=posts,
        is_owner=is_owner,
        post_limit=PROFILE_POST_LIMIT,
        tab=tab,
        to_confirm=gift_routes.pending_for(user) if is_owner and tab == "posts" else [],
        sent=gift_routes.sent_by(user) if is_owner and tab == "chipped" else [],
        sent_limit=gift_routes.MY_GIFTS_LIMIT,
        disputing=request.args.get("dispute", type=int),
    )
