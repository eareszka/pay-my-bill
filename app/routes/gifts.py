import smtplib
from collections import defaultdict
from datetime import timedelta
from typing import Any

import click
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
from flask_login import current_user
from sqlalchemy import Select, func, select, update
from sqlalchemy.orm import joinedload
from werkzeug.wrappers import Response

from app.auth import login_required, verified_required
from app.extensions import db
from app.forms import GiftForm
from app.mail import send_email, send_later
from app.models import (
    LATE_GIFT_HOURS,
    PENDING_GIFT_DAYS,
    PUBLIC_STATUSES,
    UPDATE_DUE_DAYS,
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    PostStatus,
    User,
    gift_expiry_cutoff,
    utcnow,
)
from app.money import format_cents
from app.routes.posts import MAX_DB_INT, render_post, send_update_notice
from app.tokens import GIFT_ANSWER, make_token, read_token
from app.urls import site_url

bp = Blueprint("gifts", __name__)


def send_gift_notice(donation: Donation) -> None:
    post = donation.post
    body = (
        f"Hi {post.user.username},\n\n{donation.donor.username} says they sent you "
        f"{format_cents(donation.amount_cents)} via {donation.method.label} "
        f'for "{post.title}".\n\nCheck {donation.method.label}, then answer in one tap:\n'
        f"{answer_link(donation)}\n\n"
        f"Or see them on your profile: {site_url('gifts.index')}"
    )
    send_later(post.user.email, f"{donation.donor.username} sent you a gift", body)


@bp.post("/posts/<int:post_id>/gifts")
@verified_required
def create(post_id: int) -> Response | tuple[str, int]:
    # Lock the post so it can't close or get funded between this check and the insert.
    post = (
        db.session.scalar(select(Post).where(Post.id == post_id).with_for_update())
        if post_id <= MAX_DB_INT
        else None
    )
    if post is None or post.status not in PUBLIC_STATUSES:
        abort(404)
    if not post.takes_gifts:
        db.session.rollback()
        reason = (
            "This post was deleted"
            if post.is_deleted
            else f"This post closed more than {LATE_GIFT_HOURS} hours ago"
        )
        flash(f"{reason}, so a new gift can't be recorded.", "info")
        return redirect(url_for("posts.show", post_id=post_id))
    donor: User = current_user
    if donor.id == post.user_id:
        abort(403)
    if post.pending_gift_from(donor.id):
        db.session.rollback()
        flash(f"You already have a gift waiting for {post.user.username} to confirm.", "info")
        return redirect(url_for("posts.show", post_id=post.id))
    form = GiftForm.for_post(post)
    if not form.validate_on_submit():
        db.session.rollback()
        return render_post(post, form), 400
    donation = Donation(
        post=post,
        donor=donor,
        amount_cents=form.amount_cents,
        method=PaymentMethod(form.method.data),
    )
    db.session.add(donation)
    db.session.commit()
    send_gift_notice(donation)
    flash(
        f"Thanks! Your gift counts once {post.user.username} confirms it came through.", "success"
    )
    return redirect(url_for("posts.show", post_id=post.id))


MY_GIFTS_LIMIT = 50


def waiting_for(user: User) -> Select[Donation]:
    # Pending gifts to the user's posts; expired gifts and removed posts never count.
    return (
        select(Donation)
        .join(Donation.post)
        .where(
            Post.user_id == user.id,
            Post.status != PostStatus.REMOVED,
            Donation.status == DonationStatus.PENDING,
            Donation.created_at > gift_expiry_cutoff(),
        )
    )


def pending_for(user: User) -> list[Donation]:
    return list(
        db.session.scalars(
            waiting_for(user)
            .options(joinedload(Donation.donor), joinedload(Donation.post))
            .order_by(Donation.created_at, Donation.id)
        )
    )


@bp.app_context_processor
def pending_gift_count() -> dict[str, int]:
    if not current_user.is_authenticated:
        return {}
    count = db.session.scalar(
        select(func.count()).select_from(waiting_for(current_user).subquery())
    )
    return {"pending_gift_count": count or 0}


def sent_by(user: User) -> list[Donation]:
    return list(
        db.session.scalars(
            select(Donation)
            .options(joinedload(Donation.post).joinedload(Post.user))
            .where(Donation.donor_id == user.id)
            .order_by(Donation.created_at.desc(), Donation.id.desc())
            .limit(MY_GIFTS_LIMIT)
        )
    )


@bp.get("/gifts")
@login_required
def index() -> Response:
    # Gifts live on your profile now (#132); old links and emails land there.
    args: dict[str, Any] = {k: v for k, v in request.args.items() if k in ("dispute", "tab")}
    return redirect(url_for("profile.show", username=current_user.username, **args))


def locked_gift(donation_id: int, owner_id: int) -> Donation:
    # Lock the gift so a double tap can't confirm and dispute it at the same time.
    donation = (
        db.session.scalar(select(Donation).where(Donation.id == donation_id).with_for_update())
        if donation_id <= MAX_DB_INT
        else None
    )
    if (
        donation is None
        or donation.post.user_id != owner_id
        or donation.post.status == PostStatus.REMOVED
    ):
        db.session.rollback()
        abort(404)
    return donation


def settle(donation: Donation, action: str) -> tuple[str, str]:
    """Confirm or dispute a locked gift; returns the message and its flash category."""
    if donation.status != DonationStatus.PENDING:
        db.session.rollback()
        return "That gift was already handled.", "info"
    if action == "confirm" and donation.is_expired:
        db.session.rollback()
        return f"That gift expired after {PENDING_GIFT_DAYS} days, so it can't count.", "info"
    confirmed = action == "confirm"
    already_heard = donation.donor in donation.post.confirmed_donors
    donation.status = DonationStatus.CONFIRMED if confirmed else DonationStatus.DISPUTED
    donation.resolved_at = utcnow()
    db.session.commit()
    amount, donor = format_cents(donation.amount_cents), donation.donor.username
    if not confirmed:
        return f"Marked {amount} from {donor} as not received.", "info"
    post, funded = count_confirmed(donation, already_heard)
    if funded:
        return f'Confirmed {amount} from {donor}. "{post.title}" is fully funded!', "success"
    if post.owes_update:
        return (
            f"Confirmed {amount} from {donor}. You have {UPDATE_DUE_DAYS} days "
            "to post a results update.",
            "success",
        )
    return f"Confirmed {amount} from {donor}. Thanks for keeping it honest.", "success"


def count_confirmed(donation: Donation, already_heard: bool) -> tuple[Post, bool]:
    """Apply a just-committed confirmation to its post; returns the post and if it's funded."""
    # Lock the post as create() does, and re-read it after the commit so gifts
    # confirmed in parallel count and a post closed meanwhile stays closed.
    post = db.session.scalars(
        select(Post)
        .where(Post.id == donation.post_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    ).one()
    funded = post.is_open and post.raised_cents >= post.goal_cents
    if funded:
        post.close(PostStatus.FUNDED)
    if post.owes_update:
        # The confirmation may have moved the deadline, so remind against the new one.
        post.update_reminders_sent = 0
    db.session.commit()
    if post.update_body and not already_heard:
        # The update went out before this gift counted, so this donor hasn't heard.
        send_update_notice(post, donation.donor)
    return post, funded


@bp.post("/gifts/<int:donation_id>/<any(confirm, dispute):action>")
@login_required
def resolve(donation_id: int, action: str) -> Response:
    flash(*settle(locked_gift(donation_id, current_user.id), action))
    return redirect(url_for("profile.show", username=current_user.username))


def answer_link(donation: Donation) -> str:
    token = make_token(donation.id, str(donation.post.user_id), GIFT_ANSWER)
    return site_url("gifts.answer", token=token)


def answer_target(token: str) -> tuple[int, int]:
    payload = read_token(token, GIFT_ANSWER, PENDING_GIFT_DAYS * 24 * 3600)
    if payload is None or not payload[1].isdigit():
        abort(404)
    return payload[0], int(payload[1])


@bp.get("/gifts/answer/<token>")
def answer(token: str) -> str:
    # The link came to the poster's inbox, so it works without logging in. Showing the
    # question first keeps email scanners that open links from answering it.
    donation_id, owner_id = answer_target(token)
    donation = locked_gift(donation_id, owner_id)
    db.session.rollback()
    return render_template("gifts/answer.html", donation=donation, token=token)


@bp.post("/gifts/answer/<token>/<any(confirm, dispute):action>")
def answer_post(token: str, action: str) -> str:
    donation_id, owner_id = answer_target(token)
    message, category = settle(locked_gift(donation_id, owner_id), action)
    return render_template("gifts/answered.html", message=message, category=category)


REMIND_AFTER_DAYS = 3


def send_reminders() -> int:
    """Email each poster once about gifts pending for 3+ days; returns emails sent."""
    now = utcnow()
    due = db.session.scalars(
        select(Donation)
        .join(Donation.post)
        .options(joinedload(Donation.donor), joinedload(Donation.post).joinedload(Post.user))
        .where(
            Donation.status == DonationStatus.PENDING,
            Donation.reminded_at.is_(None),
            Donation.created_at <= now - timedelta(days=REMIND_AFTER_DAYS),
            Donation.created_at > gift_expiry_cutoff(now),
            Post.status != PostStatus.REMOVED,
        )
        .order_by(Donation.created_at, Donation.id)
    ).all()
    by_poster: defaultdict[User, list[Donation]] = defaultdict(list)
    for gift in due:
        by_poster[gift.post.user].append(gift)
    link = current_app.config["APP_URL"].rstrip("/") + "/gifts"
    emails = []
    for poster, gifts in by_poster.items():
        if poster.is_deleted:
            continue
        lines = "\n".join(
            f"- {format_cents(g.amount_cents)} via {g.method.label} "
            f'from {g.donor.username} for "{g.post.title}"'
            for g in gifts
        )
        body = (
            f"Hi {poster.username},\n\n"
            f"These gifts are still waiting for you to confirm:\n{lines}\n\n"
            f"Check your payment app, then confirm or dispute them here:\n{link}\n\n"
            f"Gifts nobody confirms expire after {PENDING_GIFT_DAYS} days, "
            "and the donor gets no credit."
        )
        emails.append((poster.id, poster.email, body, [g.id for g in gifts]))
    # End the read transaction before slow SMTP sends; mark each poster as soon as
    # their email goes out so a later failure can't cause a repeat.
    db.session.rollback()
    sent = 0
    for poster_id, address, body, gift_ids in emails:
        try:
            send_email(address, "Gifts waiting for you to confirm", body)
        except (smtplib.SMTPException, OSError):
            current_app.logger.exception("Could not send the gift reminder to user %s", poster_id)
            continue
        db.session.execute(
            update(Donation).where(Donation.id.in_(gift_ids)).values(reminded_at=now)
        )
        db.session.commit()
        sent += 1
    return sent


@bp.cli.command("remind")
def remind_command() -> None:
    """Email posters about gifts waiting 3+ days to be confirmed (run daily)."""
    click.echo(f"Reminder emails sent: {send_reminders()}")
