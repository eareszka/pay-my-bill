import smtplib

from flask import Blueprint, abort, current_app, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload
from werkzeug.wrappers import Response

from app.accounts import delete_post
from app.auth import login_required, verified_required
from app.extensions import db
from app.forms import GiftForm, PostForm, ResultsUpdateForm
from app.mail import send_email
from app.models import MAX_OPEN_POSTS, Post, PostKind, PostStatus, User, open_posts, utcnow
from app.moderation import is_flagged
from app.payment_links import pay_options

bp = Blueprint("posts", __name__, url_prefix="/posts")

PUBLIC_STATUSES = (PostStatus.OPEN, PostStatus.FUNDED, PostStatus.CLOSED)
MAX_DB_INT = 2**31 - 1


def active_post_count(user: User) -> int:
    count = db.session.scalar(
        select(func.count())
        .select_from(Post)
        .where(
            Post.user_id == user.id,
            or_(open_posts(), Post.status == PostStatus.PENDING_REVIEW),
        )
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
    post = (
        db.session.get(Post, post_id, options=[joinedload(Post.user)])
        if post_id <= MAX_DB_INT
        else None
    )
    if post is None or not can_view(post):
        abort(404)
    return render_post(post, GiftForm.for_post(post))


def render_post(post: Post, form: GiftForm, update_form: ResultsUpdateForm | None = None) -> str:
    return render_template(
        "posts/show.html",
        post=post,
        pay_options=pay_options(post.user),
        form=form,
        update_form=update_form or ResultsUpdateForm(formdata=None),
    )


def own_post_for_update(post_id: int) -> Post:
    # Lock the post so a gift confirmed or recorded at the same moment can't be lost.
    post = (
        db.session.scalars(
            select(Post)
            .where(Post.id == post_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        ).one_or_none()
        if post_id <= MAX_DB_INT
        else None
    )
    if post is None or post.user_id != current_user.id:
        db.session.rollback()
        abort(404)
    return post


@bp.post("/<int:post_id>/close")
@login_required
def close(post_id: int) -> Response:
    post = own_post_for_update(post_id)
    if post.is_open:
        post.close()
        db.session.commit()
        flash("Your post is closed.", "success")
    else:
        db.session.rollback()
        flash("That post isn't open anymore.", "info")
    return redirect(url_for("posts.show", post_id=post_id))


def send_update_notices(post: Post) -> None:
    link = url_for("posts.show", post_id=post.id, _external=True)
    for donor in post.confirmed_donors:
        if donor.is_deleted:
            continue
        body = (
            f"Hi {donor.username},\n\n{post.user.username} shared how it went "
            f'on "{post.title}", a post you chipped in on.\n\nRead it here:\n{link}'
        )
        try:
            send_email(donor.email, f"{post.user.username} shared how it went", body)
        except (smtplib.SMTPException, OSError):
            current_app.logger.exception(
                "Could not send the update notice for post %s to user %s", post.id, donor.id
            )


@bp.post("/<int:post_id>/update")
@login_required
def update(post_id: int) -> Response | tuple[str, int]:
    post = own_post_for_update(post_id)
    if not post.owes_update:
        db.session.rollback()
        flash("This post doesn't need an update.", "info")
        return redirect(url_for("posts.show", post_id=post_id))
    form = ResultsUpdateForm()
    if not form.validate_on_submit():
        db.session.rollback()
        return render_post(post, GiftForm.for_post(post), form), 400
    post.update_body = form.note.data
    post.update_posted_at = utcnow()
    db.session.commit()
    send_update_notices(post)
    flash("Thanks for sharing how it went. Everyone who chipped in was emailed.", "success")
    return redirect(url_for("posts.show", post_id=post_id))


@bp.post("/<int:post_id>/delete")
@login_required
def delete(post_id: int) -> Response:
    delete_post(own_post_for_update(post_id))
    db.session.commit()
    flash("Your post was deleted.", "success")
    return redirect(url_for("main.index"))
