import click
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import or_, select, update
from sqlalchemy.orm import joinedload
from werkzeug.wrappers import Response

from app import photos
from app.auth import admin_required
from app.extensions import db
from app.farm_flags import CLUSTER_SIZE, suspected_farms
from app.forms import EmptyForm
from app.mail import send_later
from app.models import (
    MAX_DB_INT,
    AdminAction,
    Post,
    PostStatus,
    Report,
    ReportReason,
    User,
    utcnow,
)
from app.urls import site_url

bp = Blueprint("admin", __name__, url_prefix="/admin")


def notify_admins(subject: str, body: str) -> None:
    admins = db.session.scalars(select(User).where(User.is_admin.is_(True))).all()
    link = site_url("admin.queue")
    for admin in admins:
        send_later(admin.email, subject, f"{body}\n\nReview it: {link}")


def _resolve(*where: object, resolution: str) -> None:
    db.session.execute(
        update(Report)
        .where(Report.resolved_at.is_(None), *where)  # type: ignore[arg-type]
        .values(resolved_at=utcnow(), resolution=resolution)
    )


def _post(post_id: int) -> Post:
    post = db.session.get(Post, post_id) if post_id <= MAX_DB_INT else None
    if post is None:
        abort(404)
    return post


def _log(action: str, target: str) -> None:
    """Record an admin action; it commits with the change it describes."""
    admin_id = current_user.id if current_user and current_user.is_authenticated else None
    db.session.add(AdminAction(admin_id=admin_id, action=action, target=target[:200]))


def _about(post: Post) -> str:
    return f"post {post.id} by {post.user.username}: {post.title}"


RECENT_ACTIONS = 25


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
    actions = db.session.scalars(
        select(AdminAction)
        .options(joinedload(AdminAction.admin))
        .order_by(AdminAction.created_at.desc(), AdminAction.id.desc())
        .limit(RECENT_ACTIONS)
    ).all()
    return render_template(
        "admin/queue.html",
        flagged=flagged,
        reports=reports,
        farms=suspected_farms(),
        cluster_size=CLUSTER_SIZE,
        actions=actions,
        form=EmptyForm(),
    )


@bp.post("/posts/<int:post_id>/approve")
@admin_required
def approve(post_id: int) -> Response:
    post = _post(post_id)
    if post.status == PostStatus.PENDING_REVIEW:
        post.status = PostStatus.OPEN
        # Its 30 days start now, so time in review doesn't use up the window (#68).
        post.created_at = utcnow()
        _resolve(Report.post_id == post.id, resolution="approved")
        _log("approve", _about(post))
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
    _log("remove post", _about(post))
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
    _log("remove photo", _about(post))
    db.session.commit()
    photos.discard(photo_key)
    flash(f"Removed the photo from “{post.title}”.", "success")
    return redirect(url_for("admin.queue"))


def _ban(user: User) -> list[str]:
    """Ban the user. Returns photo keys to discard once the change commits."""
    user.banned_at = utcnow()
    _log("ban", f"user {user.username}")
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
    return photo_keys


@bp.post("/users/<int:user_id>/ban")
@admin_required
def ban(user_id: int) -> Response:
    user = db.session.get(User, user_id) if user_id <= MAX_DB_INT else None
    if user is None or user.is_admin:
        abort(404)
    photo_keys = _ban(user)
    db.session.commit()
    for key in photo_keys:
        photos.discard(key)
    flash(f"Banned {user.username}. Their posts and profile are hidden.", "success")
    return redirect(url_for("admin.queue"))


@bp.post("/users/<int:user_id>/ban-cluster")
@admin_required
def ban_cluster(user_id: int) -> Response:
    # Recomputed here, so only accounts the queue still flags are banned.
    flag = next((f for f in suspected_farms() if f.donor.id == user_id), None)
    if flag is None:
        abort(404)
    # Only the accounts the admin saw, never one that joined the cluster since.
    seen = {int(id_) for id_ in request.args.get("ids", "").split(",") if id_.isdigit()}
    cluster = [u for u in flag.cluster if u.id in seen]
    targets = [u for u in (flag.donor, *cluster) if not u.is_admin and not u.is_banned]
    photo_keys = [key for user in targets for key in _ban(user)]
    db.session.commit()
    for key in photo_keys:
        photos.discard(key)
    flash(f"Banned {', '.join(u.username for u in targets)}.", "success")
    return redirect(url_for("admin.queue"))


@bp.post("/reports/<int:report_id>/dismiss")
@admin_required
def dismiss(report_id: int) -> Response:
    report = db.session.get(Report, report_id) if report_id <= MAX_DB_INT else None
    if report is None:
        abort(404)
    _resolve(Report.id == report.id, resolution="dismissed")
    if report.post:
        target = _about(report.post)
    else:
        target = f"user {report.user.username}" if report.user else "a user"
    _log("dismiss report", f"report {report.id} on {target}")
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
    _log("grant admin", f"user {user.username}")
    db.session.commit()
    click.echo(f"{user.username} is now an admin.")


@bp.cli.command("revoke")
@click.argument("email")
def revoke_command(email: str) -> None:
    """Take admin away from the account with this email."""
    user = db.session.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None:
        raise click.ClickException(f"No account uses {email}.")
    if not user.is_admin:
        raise click.ClickException(f"{user.username} isn't an admin.")
    user.is_admin = False
    _log("revoke admin", f"user {user.username}")
    db.session.commit()
    click.echo(f"{user.username} is no longer an admin.")
    if not db.session.scalar(select(User.id).where(User.is_admin.is_(True))):
        click.echo("Warning: no admins are left, so nobody can open /admin.", err=True)
