from datetime import timedelta

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import ColumnElement, func, select
from werkzeug.wrappers import Response

from app.auth import verified_required
from app.extensions import db
from app.forms import ReportForm
from app.models import (
    MAX_DB_INT,
    LoginAttempt,
    Post,
    Report,
    ReportReason,
    User,
    as_utc,
    utcnow,
)
from app.routes.admin import notify_admins
from app.routes.posts import can_view

bp = Blueprint("reports", __name__, url_prefix="/report")

# One account can't flood the queue, and admins get at most one report email an hour;
# the queue holds the rest (#175).
MAX_REPORTS_PER_DAY = 10
REPORT_WINDOW = timedelta(days=1)
REPORT_EMAIL_GAP = timedelta(hours=1)
# A throttle row marks each report email; the colon keeps it apart from usernames.
REPORT_EMAIL_IDENTIFIER = "report-mail:"


def _reports_since(since: timedelta, *where: ColumnElement[bool]) -> int:
    query = select(func.count()).select_from(Report).where(Report.created_at >= utcnow() - since)
    return db.session.scalar(query.where(*where)) or 0


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
    if _already_reported(post=post, user=user):
        flash("Thanks. An admin will look at it.", "success")
        return
    if _reports_since(REPORT_WINDOW, Report.reporter_id == current_user.id) >= MAX_REPORTS_PER_DAY:
        flash(f"You've sent {MAX_REPORTS_PER_DAY} reports today. Try again tomorrow.", "error")
        return
    # At most one report email an hour, timed from the last email, so a steady trickle
    # of reports can't keep the admins from ever hearing.
    last_email = db.session.scalar(
        select(func.max(LoginAttempt.created_at)).where(
            LoginAttempt.identifier == REPORT_EMAIL_IDENTIFIER,
            # Only rows written here: a login typed as the marker stores the caller's IP
            # and a failure, so it can't pass for a sent email.
            LoginAttempt.ip.is_(None),
            LoginAttempt.succeeded.is_(True),
        )
    )
    email_admins = last_email is None or as_utc(last_email) <= utcnow() - REPORT_EMAIL_GAP
    if email_admins:
        db.session.add(LoginAttempt(identifier=REPORT_EMAIL_IDENTIFIER, ip=None, succeeded=True))
    reason = ReportReason(form.reason.data)
    db.session.add(
        Report(
            reporter_id=current_user.id,
            post=post,
            user=user,
            reason=reason,
            details=form.details.data,
        )
    )
    db.session.commit()
    if email_admins:
        notify_admins(
            "New report on Yearnly",
            f"{current_user.username} reported {target}: {reason.label}. Reports in the next "
            "hour won't email you; they wait in the queue.",
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
    if target is None or not target.is_verified or target.is_banned or target.id == current_user.id:
        abort(404)
    form = ReportForm()
    if form.validate_on_submit():
        _file(form, f"the user {target.username}", user=target)
        return redirect(url_for("profile.show", username=target.username))
    return render_template("reports/new.html", form=form, what=target.username)
