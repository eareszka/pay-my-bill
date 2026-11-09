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
from app.mail import send_later
from app.models import (
    MIN_CARD_GIFT_CENTS,
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    PostStatus,
    User,
    as_utc,
    post_open_cutoff,
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
        # The recipient's account may have lost card payments since we last looked.
        try:
            stripe_pay.refresh_ready(recipient)
            db.session.commit()
        except stripe.StripeError:
            current_app.logger.exception("Stripe status check failed for user %s", recipient.id)
    if not url:
        return _card_error(post, "Stripe isn't answering right now. Try again in a minute.")
    return redirect(url, code=303)


def _meta_int(meta: dict[str, Any], key: str) -> int | None:
    value = str(meta.get(key, ""))
    return int(value) if value.isdigit() else None


def record_card_gift(session: dict[str, Any], account: str | None) -> None:
    if session.get("payment_status") != "paid":
        return
    if db.session.scalar(select(Donation.id).where(Donation.stripe_session_id == session["id"])):
        return
    meta = session.get("metadata") or {}
    post_id, donor_id, gift_cents = (
        _meta_int(meta, "post_id"),
        _meta_int(meta, "donor_id"),
        _meta_int(meta, "gift_cents"),
    )
    post = db.session.get(Post, post_id) if post_id else None
    donor = db.session.get(User, donor_id) if donor_id else None
    if post is None or donor is None or not gift_cents:
        # Acknowledged so Stripe stops retrying; admins can match it up from Stripe.
        current_app.logger.error("Paid checkout %s has unusable metadata", session["id"])
        return
    if account is None or account != post.user.stripe_account_id:
        # Direct charges land on the recipient's account, so the event must come from the
        # account of the post it claims to pay for, or the money went to someone else.
        current_app.logger.error(
            "Paid checkout %s came from %s, not the recipient of post %s",
            session["id"],
            account,
            post.id,
        )
        return
    already_heard = donor in post.confirmed_donors
    # The processor verified the payment, so it counts without the recipient (ADR 0014).
    donation = Donation(
        post=post,
        donor=donor,
        amount_cents=gift_cents,
        fee_cents=_meta_int(meta, "fee_cents") or 0,
        method=PaymentMethod.CARD,
        status=DonationStatus.CONFIRMED,
        resolved_at=utcnow(),
        stripe_session_id=session["id"],
        stripe_payment_intent=session.get("payment_intent"),
    )
    db.session.add(donation)
    try:
        db.session.flush()
    except IntegrityError:
        # Stripe retried while the first delivery was still being saved.
        db.session.rollback()
        return
    # One commit for the gift and its effect on the post, so a failure here leaves
    # nothing saved and Stripe's retry records it from scratch.
    post, funded = count_confirmed(donation, already_heard)
    amount = format_cents(donation.amount_cents)
    link = url_for("posts.show", post_id=post.id, _external=True)
    send_later(
        post.user.email,
        f"{donor.username} sent you {amount}",
        f"Hi {post.user.username},\n\n{donor.username} chipped in {amount} by card for "
        f'"{post.title}". It already counts, and Stripe pays it out to your bank.'
        + ("\n\nYour post is fully funded!" if funded else "")
        + f"\n\n{link}",
    )
    send_later(
        donor.email,
        f"Your {amount} gift to {post.user.username} went through",
        f'Hi {donor.username},\n\nYour {amount} gift for "{post.title}" went through '
        "and already counts toward your rewards. Thank you!\n\n" + link,
    )


def _card_gift(payment_intent: str | None) -> Donation | None:
    if not payment_intent:
        return None
    return db.session.scalar(
        select(Donation).where(
            Donation.stripe_payment_intent == payment_intent,
            Donation.method == PaymentMethod.CARD,
        )
    )


def _describe(donation: Donation) -> str:
    return (
        f"{donation.donor.username}'s {format_cents(donation.amount_cents)} card gift to "
        f'{donation.post.user.username} for "{donation.post.title}"'
    )


def uncount_card_gift(payment_intent: str | None, why: str) -> None:
    donation = _card_gift(payment_intent)
    if donation is None or donation.status != DonationStatus.CONFIRMED:
        return
    donation.status = DonationStatus.DISPUTED
    post = donation.post
    if post.status == PostStatus.FUNDED and post.raised_cents < post.goal_cents:
        # It was funded with money that's gone, so it goes back to taking gifts while
        # its 30 days last, and otherwise just counts as closed.
        if as_utc(post.created_at) > post_open_cutoff():
            post.status, post.closed_at = PostStatus.OPEN, None
        else:
            post.status = PostStatus.CLOSED
    db.session.commit()
    notify_admins(
        f"A card gift was {why}",
        f"{_describe(donation)} was {why}, so it no longer counts. Check Stripe for details.",
    )


def partly_refunded(charge: dict[str, Any]) -> None:
    donation = _card_gift(charge.get("payment_intent"))
    if donation is not None:
        refunded = format_cents(int(charge.get("amount_refunded") or 0))
        notify_admins(
            "A card gift was partly refunded",
            f"{refunded} of {_describe(donation)} was refunded. The gift still counts in full; "
            "check Stripe if that's wrong.",
        )


def dispute_won(payment_intent: str | None) -> None:
    donation = _card_gift(payment_intent)
    if donation is None or donation.status != DonationStatus.DISPUTED:
        return
    already_heard = donation.donor in donation.post.confirmed_donors
    donation.status = DonationStatus.CONFIRMED
    db.session.flush()
    count_confirmed(donation, already_heard)
    notify_admins(
        "A card dispute was won", f"{_describe(donation)} was disputed and won, so it counts again."
    )


def update_account(account: stripe.Account) -> None:
    user = db.session.scalar(select(User).where(User.stripe_account_id == account.id))
    if user is not None:
        user.stripe_ready = stripe_pay.account_ready(account)
        db.session.commit()


@bp.post("/stripe/webhook")
@csrf.exempt  # type: ignore[untyped-decorator]
def webhook() -> tuple[str, int]:
    if not stripe_pay.webhook_secrets():
        abort(404)
    try:
        event = stripe_pay.parse_event(
            request.get_data(), request.headers.get("Stripe-Signature", "")
        )
    except (ValueError, stripe.SignatureVerificationError):
        return "bad signature", 400
    obj = event.data.object.to_dict()
    match event.type:
        case "checkout.session.completed" | "checkout.session.async_payment_succeeded":
            record_card_gift(obj, getattr(event, "account", None))
        case "charge.refunded" if obj.get("refunded"):
            uncount_card_gift(obj.get("payment_intent"), "refunded")
        case "charge.refunded":
            partly_refunded(obj)
        case "charge.dispute.created":
            uncount_card_gift(obj.get("payment_intent"), "disputed by the card holder")
        case "charge.dispute.closed" if obj.get("status") == "won":
            dispute_won(obj.get("payment_intent"))
        case "account.updated":
            update_account(stripe.Account.construct_from(obj, None))
    return "ok", 200
