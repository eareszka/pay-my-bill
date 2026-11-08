import smtplib
from typing import Any

import stripe
from flask import Blueprint, abort, current_app, flash, redirect, request, url_for
from flask_login import current_user
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from werkzeug.wrappers import Response

from app import stripe_pay
from app.auth import verified_required
from app.extensions import csrf, db
from app.forms import GiftForm
from app.mail import send_email
from app.models import (
    MIN_CARD_GIFT_CENTS,
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    User,
    utcnow,
)
from app.money import format_cents, parse_dollars
from app.routes.admin import notify_admins
from app.routes.gifts import count_confirmed
from app.routes.posts import MAX_DB_INT, can_view, render_post

bp = Blueprint("card", __name__)


def _card_error(post: Post, message: str) -> tuple[str, int]:
    return render_post(post, GiftForm.for_post(post), card_error=message), 400


@bp.post("/posts/<int:post_id>/card")
@verified_required
def checkout(post_id: int) -> Response | tuple[str, int]:
    post = db.session.get(Post, post_id) if post_id <= MAX_DB_INT else None
    if post is None or not can_view(post) or not stripe_pay.enabled():
        abort(404)
    recipient = post.user
    if recipient.id == current_user.id:
        abort(404)
    if not (post.is_open and recipient.stripe_ready and recipient.stripe_account_id):
        flash("This post isn't taking card gifts right now.", "info")
        return redirect(url_for("posts.show", post_id=post.id))
    limits = f"Enter an amount from {format_cents(MIN_CARD_GIFT_CENTS)} up to " + format_cents(
        post.goal_cents
    )
    try:
        gift_cents = parse_dollars(request.form.get("amount", ""))
    except ValueError:
        return _card_error(post, f"{limits}, like 20 or 12.50.")
    if not MIN_CARD_GIFT_CENTS <= gift_cents <= post.goal_cents:
        return _card_error(post, f"{limits}.")
    back = url_for("posts.show", post_id=post.id, _external=True)
    try:
        url = stripe_pay.checkout_url(
            post_id=post.id,
            title=post.title,
            donor_id=current_user.id,
            donor_email=current_user.email,
            recipient=recipient.username,
            destination=recipient.stripe_account_id,
            gift_cents=gift_cents,
            success_url=url_for("posts.show", post_id=post.id, paid=1, _external=True),
            cancel_url=back,
        )
    except stripe.StripeError:
        current_app.logger.exception("Stripe checkout failed for post %s", post.id)
        url = ""
    if not url:
        return _card_error(post, "Stripe isn't answering right now. Try again in a minute.")
    return redirect(url, code=303)


def _quiet_email(to: str, subject: str, body: str) -> None:
    try:
        send_email(to, subject, body)
    except (smtplib.SMTPException, OSError):
        current_app.logger.exception("Could not send %r", subject)


def record_card_gift(session: dict[str, Any]) -> None:
    if session.get("payment_status") != "paid":
        return
    if db.session.scalar(select(Donation.id).where(Donation.stripe_session_id == session["id"])):
        return
    meta = session.get("metadata") or {}
    post = db.session.get(Post, int(meta.get("post_id", 0)))
    donor = db.session.get(User, int(meta.get("donor_id", 0)))
    if post is None or donor is None:
        current_app.logger.error("Paid checkout %s has no matching post or donor", session["id"])
        return
    already_heard = donor in post.confirmed_donors
    # The processor verified the payment, so it counts without the recipient (ADR 0014).
    donation = Donation(
        post=post,
        donor=donor,
        amount_cents=int(meta["gift_cents"]),
        fee_cents=int(meta.get("fee_cents", 0)),
        method=PaymentMethod.CARD,
        status=DonationStatus.CONFIRMED,
        resolved_at=utcnow(),
        stripe_session_id=session["id"],
        stripe_payment_intent=session.get("payment_intent"),
    )
    db.session.add(donation)
    try:
        db.session.commit()
    except IntegrityError:
        # Stripe retried while the first delivery was still being saved.
        db.session.rollback()
        return
    post, funded = count_confirmed(donation, already_heard)
    amount = format_cents(donation.amount_cents)
    link = url_for("posts.show", post_id=post.id, _external=True)
    _quiet_email(
        post.user.email,
        f"{donor.username} sent you {amount}",
        f"Hi {post.user.username},\n\n{donor.username} chipped in {amount} by card for "
        f'"{post.title}". It already counts, and Stripe pays it out to your bank.'
        + ("\n\nYour post is fully funded!" if funded else "")
        + f"\n\n{link}",
    )
    _quiet_email(
        donor.email,
        f"Your {amount} gift to {post.user.username} went through",
        f'Hi {donor.username},\n\nYour {amount} gift for "{post.title}" went through '
        "and already counts toward your rewards. Thank you!\n\n" + link,
    )


def uncount_card_gift(payment_intent: str | None, why: str) -> None:
    donation = (
        db.session.scalar(select(Donation).where(Donation.stripe_payment_intent == payment_intent))
        if payment_intent
        else None
    )
    if donation is None or donation.status != DonationStatus.CONFIRMED:
        return
    donation.status = DonationStatus.DISPUTED
    db.session.commit()
    notify_admins(
        f"A card gift was {why}",
        f"{donation.donor.username}'s {format_cents(donation.amount_cents)} card gift to "
        f'{donation.post.user.username} for "{donation.post.title}" was {why}, so it no '
        "longer counts. Check Stripe for details.",
    )


def update_account(account: stripe.Account) -> None:
    user = db.session.scalar(select(User).where(User.stripe_account_id == account.id))
    if user is not None:
        user.stripe_ready = stripe_pay.account_ready(account)
        db.session.commit()


@bp.post("/stripe/webhook")
@csrf.exempt  # type: ignore[untyped-decorator]
def webhook() -> tuple[str, int]:
    if not current_app.config["STRIPE_WEBHOOK_SECRET"]:
        abort(404)
    try:
        event = stripe_pay.parse_event(
            request.get_data(), request.headers.get("Stripe-Signature", "")
        )
    except (ValueError, stripe.SignatureVerificationError):
        return "bad signature", 400
    obj = event.data.object
    match event.type:
        case "checkout.session.completed" | "checkout.session.async_payment_succeeded":
            record_card_gift(obj.to_dict())
        case "charge.refunded":
            uncount_card_gift(obj.to_dict().get("payment_intent"), "refunded")
        case "charge.dispute.created":
            uncount_card_gift(obj.to_dict().get("payment_intent"), "disputed by the card holder")
        case "account.updated":
            update_account(stripe.Account.construct_from(obj.to_dict(), None))
    return "ok", 200
