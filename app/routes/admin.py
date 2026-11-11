import click
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from sqlalchemy import or_, select, update
from sqlalchemy.orm import joinedload
from werkzeug.wrappers import Response

from app import photos
from app.auth import admin_required
from app.extensions import db
from app.forms import EmptyForm
from app.mail import send_later
from app.models import Post, PostStatus, Report, ReportReason, User, utcnow

bp = Blueprint("admin", __name__, url_prefix="/admin")


def notify_admins(subject: str, body: str) -> None:
    admins = db.session.scalars(select(User).where(User.is_admin.is_(True))).all()
    link = url_for("admin.queue", _external=True)
    for admin in admins:
        send_later(admin.email, subject, f"{body}\n\nReview it: {link}")


def _resolve(*where: object, resolution: str) -> None:
    db.session.execute(
        update(Report)
        .where(Report.resolved_at.is_(None), *where)  # type: ignore[arg-type]
        .values(resolved_at=utcnow(), resolution=resolution)
    )


def _post(post_id: int) -> Post:
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    return post


@bp.get("")
@admin_required
def queue() -> str:
    flagged = db.session.scalars(
        select(Post)
        .options(joinedload(Post.user))
        .where(Post.status == PostStatus.PENDING_REVIEW)
        .order_by(Post.created_at)
    ).all()
    reports = db.session.scalars(
        select(Report)
        .options(joinedload(Report.reporter), joinedload(Report.post), joinedload(Report.user))
        .where(Report.resolved_at.is_(None))
        .order_by(Report.created_at)
    ).all()
    return render_template("admin/queue.html", flagged=flagged, reports=reports, form=EmptyForm())


@bp.post("/posts/<int:post_id>/approve")
@admin_required
def approve(post_id: int) -> Response:
    post = _post(post_id)
    if post.status == PostStatus.PENDING_REVIEW:
        post.status = PostStatus.OPEN
        # Its 30 days start now, so time in review doesn't use up the window (#68).
        post.created_at = utcnow()
        _resolve(Report.post_id == post.id, resolution="approved")
        db.session.commit()
        flash(f"Approved “{post.title}”.", "success")
    return redirect(url_for("admin.queue"))


@bp.post("/posts/<int:post_id>/remove")
@admin_required
def remove(post_id: int) -> Response:
    post = _post(post_id)
    post.status = PostStatus.REMOVED
    # A removed post's photo goes too, or its URL stays public (#144).
    photo_key, post.photo_key = post.photo_key, None
    _resolve(Report.post_id == post.id, resolution="removed")
    db.session.commit()
    photos.discard(photo_key)
    flash(f"Removed “{post.title}”.", "success")
    return redirect(url_for("admin.queue"))


@bp.post("/posts/<int:post_id>/remove-photo")
@admin_required
def remove_photo(post_id: int) -> Response:
    post = _post(post_id)
    photo_key, post.photo_key = post.photo_key, None
    _resolve(
        Report.post_id == post.id, Report.reason == ReportReason.PHOTO, resolution="photo_removed"
    )
    db.session.commit()
    photos.discard(photo_key)
    flash(f"Removed the photo from “{post.title}”.", "success")
    return redirect(url_for("admin.queue"))


@bp.post("/users/<int:user_id>/ban")
@admin_required
def ban(user_id: int) -> Response:
    user = db.session.get(User, user_id)
    if user is None or user.is_admin:
        abort(404)
    user.banned_at = utcnow()
    photo_keys: list[str] = []
    # Every post goes, closed and funded ones too, so gifts to them stop
    # counting toward anyone's rewards (#147).
    for post in user.posts:
        post.status = PostStatus.REMOVED
        if post.photo_key:
            photo_keys.append(post.photo_key)
            post.photo_key = None
    _resolve(
        or_(Report.user_id == user.id, Report.post_id.in_([p.id for p in user.posts])),
        resolution="banned",
    )
    db.session.commit()
    for key in photo_keys:
        photos.discard(key)
    flash(f"Banned {user.username}. Their posts and profile are hidden.", "success")
    return redirect(url_for("admin.queue"))


@bp.post("/reports/<int:report_id>/dismiss")
@admin_required
def dismiss(report_id: int) -> Response:
    _resolve(Report.id == report_id, resolution="dismissed")
    db.session.commit()
    flash("Report dismissed.", "success")
    return redirect(url_for("admin.queue"))


@bp.cli.command("grant")
@click.argument("email")
def grant_command(email: str) -> None:
    """Make the account with this email an admin."""
    user = db.session.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None:
        raise click.ClickException(f"No account uses {email}.")
    user.is_admin = True
    db.session.commit()
    click.echo(f"{user.username} is now an admin.")
