from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import select
from werkzeug.wrappers import Response

from app.auth import verified_required
from app.extensions import db
from app.forms import ReportForm
from app.models import Post, Report, ReportReason, User
from app.routes.admin import notify_admins
from app.routes.posts import MAX_DB_INT, can_view

bp = Blueprint("reports", __name__, url_prefix="/report")


def _already_reported(*, post: Post | None = None, user: User | None = None) -> bool:
    query = select(Report.id).where(
        Report.reporter_id == current_user.id, Report.resolved_at.is_(None)
    )
    if post is not None:
        query = query.where(Report.post_id == post.id)
    elif user is not None:
        query = query.where(Report.user_id == user.id)
    return db.session.scalar(query) is not None


def _file(
    form: ReportForm, target: str, *, post: Post | None = None, user: User | None = None
) -> None:
    if not _already_reported(post=post, user=user):
        db.session.add(
            Report(
                reporter_id=current_user.id,
                post=post,
                user=user,
                reason=ReportReason(form.reason.data),
                details=form.details.data,
            )
        )
        db.session.commit()
        notify_admins(
            "New report on Pay My Bill",
            f"{current_user.username} reported {target}: {ReportReason(form.reason.data).label}.",
        )
    flash("Thanks. An admin will look at it.", "success")


@bp.route("/post/<int:post_id>", methods=["GET", "POST"])
@verified_required
def post(post_id: int) -> str | Response:
    target = db.session.get(Post, post_id) if post_id <= MAX_DB_INT else None
    if target is None or not can_view(target) or target.user_id == current_user.id:
        abort(404)
    form = ReportForm()
    if form.validate_on_submit():
        _file(form, f"the post “{target.title}”", post=target)
        return redirect(url_for("posts.show", post_id=target.id))
    return render_template("reports/new.html", form=form, what=f"“{target.title}”")


@bp.route("/user/<username>", methods=["GET", "POST"])
@verified_required
def user(username: str) -> str | Response:
    target = db.session.scalar(select(User).where(User.username == username.lower()))
    if target is None or not target.is_verified or target.id == current_user.id:
        abort(404)
    form = ReportForm()
    if form.validate_on_submit():
        _file(form, f"the user {target.username}", user=target)
        return redirect(url_for("profile.show", username=target.username))
    return render_template("reports/new.html", form=form, what=target.username)
