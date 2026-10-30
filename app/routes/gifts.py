import smtplib

from flask import Blueprint, abort, current_app, flash, redirect, url_for
from flask_login import current_user
from sqlalchemy import func, select
from werkzeug.wrappers import Response

from app.auth import verified_required
from app.extensions import db
from app.forms import GiftForm
from app.mail import send_email
from app.models import Donation, DonationStatus, PaymentMethod, Post, PostStatus, User
from app.money import format_cents
from app.payment_links import PAY_URLS
from app.routes.posts import MAX_DB_INT, render_post

bp = Blueprint("gifts", __name__)


def send_gift_notice(donation: Donation) -> None:
    post, label = donation.post, PAY_URLS[donation.method][0]
    body = (
        f"Hi {post.user.username},\n\n{donation.donor.username} says they sent you "
        f"{format_cents(donation.amount_cents)} via {label} "
        f'for "{post.title}".\n\nCheck the app, then confirm or dispute the gift here:\n'
        + url_for("posts.show", post_id=post.id, _external=True)
    )
    try:
        send_email(post.user.email, f"{donation.donor.username} sent you a gift", body)
    except (smtplib.SMTPException, OSError):
        current_app.logger.exception("Could not send the gift notice for donation %s", donation.id)


def has_pending_gift(donor: User, post: Post) -> bool:
    # One pending claim per donor per post keeps a poster's inbox from being flooded.
    count = db.session.scalar(
        select(func.count(Donation.id)).where(
            Donation.post_id == post.id,
            Donation.donor_id == donor.id,
            Donation.status == DonationStatus.PENDING,
        )
    )
    return bool(count)


@bp.post("/posts/<int:post_id>/gifts")
@verified_required
def create(post_id: int) -> Response | tuple[str, int]:
    # Lock the post so it can't close or get funded between this check and the insert.
    post = (
        db.session.scalar(select(Post).where(Post.id == post_id).with_for_update())
        if post_id <= MAX_DB_INT
        else None
    )
    if post is None or post.status != PostStatus.OPEN:
        abort(404)
    donor: User = current_user
    if donor.id == post.user_id:
        abort(403)
    if has_pending_gift(donor, post):
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
