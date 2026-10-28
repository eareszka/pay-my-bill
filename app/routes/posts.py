from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import func, select
from werkzeug.wrappers import Response

from app.auth import verified_required
from app.extensions import db
from app.forms import PostForm
from app.models import MAX_OPEN_POSTS, Post, PostKind, PostStatus, User, utcnow
from app.moderation import is_flagged

bp = Blueprint("posts", __name__, url_prefix="/posts")

ACTIVE_STATUSES = (PostStatus.OPEN, PostStatus.PENDING_REVIEW)
PUBLIC_STATUSES = (PostStatus.OPEN, PostStatus.FUNDED, PostStatus.CLOSED)


def active_post_count(user: User) -> int:
    count = db.session.scalar(
        select(func.count())
        .select_from(Post)
        .where(Post.user_id == user.id, Post.status.in_(ACTIVE_STATUSES))
    )
    return count or 0


@bp.route("/new", methods=["GET", "POST"])
@verified_required
def new() -> str | Response | tuple[str, int]:
    user: User = current_user
    if not user.has_payment_handle:
        flash("Add a Cash App, Venmo, or PayPal handle so people can pay you.", "info")
        return redirect(url_for("profile.edit"))
    form = PostForm(require_rules=user.rules_accepted_at is None)
    if form.is_submitted():
        # Lock the user row so parallel submits can't all pass the open-post limit.
        db.session.execute(select(User.id).where(User.id == user.id).with_for_update())
    at_limit = active_post_count(user) >= MAX_OPEN_POSTS
    if not at_limit and form.validate_on_submit():
        if form.require_rules:
            user.rules_accepted_at = utcnow()
        flagged = is_flagged(form.title.data, form.body.data)
        post = Post(
            user=user,
            kind=PostKind(form.kind.data),
            title=form.title.data,
            body=form.body.data,
            goal_cents=form.goal_cents,
            status=PostStatus.PENDING_REVIEW if flagged else PostStatus.OPEN,
        )
        db.session.add(post)
        db.session.commit()
        if flagged:
            flash("Thanks! Your post will show in the feed after a quick review.", "info")
        else:
            flash("Your post is live.", "success")
        return redirect(url_for("posts.show", post_id=post.id))
    db.session.rollback()
    page = render_template("posts/new.html", form=form, at_limit=at_limit)
    return page, 409 if at_limit and form.is_submitted() else 200


def can_view(post: Post) -> bool:
    if post.status in PUBLIC_STATUSES:
        return True
    viewer: User | None = current_user if current_user.is_authenticated else None
    return viewer is not None and (viewer.id == post.user_id or viewer.is_admin)


@bp.get("/<int:post_id>")
def show(post_id: int) -> str:
    post = db.session.get(Post, post_id)
    if post is None or not can_view(post):
        abort(404)
    return render_template("posts/show.html", post=post)
