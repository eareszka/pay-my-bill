from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import func, select
from werkzeug.wrappers import Response

from app.auth import verified_required
from app.extensions import db
from app.forms import PostForm
from app.models import Post, PostKind, PostStatus, User, utcnow
from app.moderation import is_flagged

bp = Blueprint("posts", __name__, url_prefix="/posts")

MAX_OPEN_POSTS = 2
ACTIVE_STATUSES = (PostStatus.OPEN, PostStatus.PENDING_REVIEW)


def active_post_count(user: User) -> int:
    count = db.session.scalar(
        select(func.count())
        .select_from(Post)
        .where(Post.user_id == user.id, Post.status.in_(ACTIVE_STATUSES))
    )
    return count or 0


@bp.route("/new", methods=["GET", "POST"])
@verified_required
def new() -> str | Response:
    user: User = current_user
    if not user.has_payment_handle:
        flash("Add a Cash App, Venmo, or PayPal handle so people can pay you.", "info")
        return redirect(url_for("profile.edit"))
    form = PostForm()
    needs_rules = user.rules_accepted_at is None
    at_limit = active_post_count(user) >= MAX_OPEN_POSTS
    if not at_limit and form.validate_on_submit():
        if needs_rules and not form.accept_rules.data:
            form.accept_rules.errors.append("You need to agree to the Community Rules to post.")
        else:
            if needs_rules:
                user.rules_accepted_at = utcnow()
            flagged = is_flagged(form.title.data, form.body.data)
            db.session.add(
                Post(
                    user=user,
                    kind=PostKind(form.kind.data),
                    title=form.title.data,
                    body=form.body.data,
                    goal_cents=form.goal_cents,
                    status=PostStatus.PENDING_REVIEW if flagged else PostStatus.OPEN,
                )
            )
            db.session.commit()
            if flagged:
                flash(
                    "Your post is waiting for review because it may be business or investment "
                    "fundraising, which isn't allowed. We'll check it soon.",
                    "info",
                )
            else:
                flash("Your post is live.", "success")
            return redirect(url_for("main.index"))
    status = 409 if at_limit and form.is_submitted() else 200
    page = render_template("posts/new.html", form=form, needs_rules=needs_rules, at_limit=at_limit)
    return Response(page, status=status)
