import smtplib

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
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from werkzeug.wrappers import Response

from app.auth import login_required, verified_required
from app.extensions import db
from app.forms import GiftForm
from app.mail import send_email
from app.models import Donation, DonationStatus, PaymentMethod, Post, PostStatus, User, utcnow
from app.money import format_cents
from app.routes.posts import MAX_DB_INT, render_post

bp = Blueprint("gifts", __name__)


def send_gift_notice(donation: Donation) -> None:
    post = donation.post
    body = (
        f"Hi {post.user.username},\n\n{donation.donor.username} says they sent you "
        f"{format_cents(donation.amount_cents)} via {donation.method.label} "
        f'for "{post.title}".\n\nCheck the app, then confirm or dispute the gift here:\n'
        + url_for("gifts.index", _external=True)
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


MY_GIFTS_LIMIT = 50


def pending_for(user: User) -> list[Donation]:
    return list(
        db.session.scalars(
            select(Donation)
            .join(Donation.post)
            .options(joinedload(Donation.donor), joinedload(Donation.post))
            .where(Post.user_id == user.id, Donation.status == DonationStatus.PENDING)
            .order_by(Donation.created_at, Donation.id)
        )
    )


@bp.app_context_processor
def pending_gift_count() -> dict[str, int]:
    if not current_user.is_authenticated:
        return {}
    count = db.session.scalar(
        select(func.count(Donation.id))
        .join(Donation.post)
        .where(Post.user_id == current_user.id, Donation.status == DonationStatus.PENDING)
    )
    return {"pending_gift_count": count or 0}


@bp.get("/gifts")
@login_required
def index() -> str:
    user: User = current_user
    sent = db.session.scalars(
        select(Donation)
        .options(joinedload(Donation.post).joinedload(Post.user))
        .where(Donation.donor_id == user.id)
        .order_by(Donation.created_at.desc(), Donation.id.desc())
        .limit(MY_GIFTS_LIMIT)
    )
    return render_template(
        "gifts/index.html",
        to_confirm=pending_for(user),
        sent=list(sent),
        disputing=request.args.get("dispute", type=int),
    )


@bp.post("/gifts/<int:donation_id>/<any(confirm, dispute):action>")
@login_required
def resolve(donation_id: int, action: str) -> Response:
    # Lock the gift so a double tap can't confirm and dispute it at the same time.
    donation = (
        db.session.scalar(select(Donation).where(Donation.id == donation_id).with_for_update())
        if donation_id <= MAX_DB_INT
        else None
    )
    if donation is None or donation.post.user_id != current_user.id:
        abort(404)
    if donation.status != DonationStatus.PENDING:
        db.session.rollback()
        flash("That gift was already handled.", "info")
        return redirect(url_for("gifts.index"))
    confirmed = action == "confirm"
    donation.status = DonationStatus.CONFIRMED if confirmed else DonationStatus.DISPUTED
    donation.resolved_at = utcnow()
    db.session.commit()
    amount, donor = format_cents(donation.amount_cents), donation.donor.username
    if not confirmed:
        flash(f"Marked {amount} from {donor} as not received.", "info")
        return redirect(url_for("gifts.index"))
    # Re-read after the commit so gifts confirmed in parallel are counted too.
    post = donation.post
    if post.status == PostStatus.OPEN and post.raised_cents >= post.goal_cents:
        post.status = PostStatus.FUNDED
        db.session.commit()
        flash(f'Confirmed {amount} from {donor}. "{post.title}" is fully funded!', "success")
    else:
        flash(f"Confirmed {amount} from {donor}. Thanks for keeping it honest.", "success")
    return redirect(url_for("gifts.index"))
