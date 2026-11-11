import stripe
from flask import Blueprint, abort, current_app, flash, redirect, url_for
from flask_login import current_user
from werkzeug.wrappers import Response

from app import stripe_pay
from app.auth import verified_required
from app.extensions import db
from app.urls import site_url

bp = Blueprint("stripe", __name__, url_prefix="/stripe")

STRIPE_DOWN = "Stripe isn't answering right now. Try again in a minute."


def _back() -> Response:
    # The top of the page, where the flash shows; the section anchor scrolled past it.
    return redirect(url_for("profile.edit"))


def _onboard() -> Response:
    if not stripe_pay.enabled():
        abort(404)
    try:
        account_id = stripe_pay.ensure_account(
            current_user,
            site_url("profile.show", username=current_user.username),
        )
        db.session.commit()
        url = stripe_pay.onboarding_url(
            account_id,
            refresh_url=site_url("stripe.refresh"),
            return_url=site_url("stripe.done"),
        )
    except stripe.StripeError:
        current_app.logger.exception("Stripe onboarding failed for user %s", current_user.id)
        flash(STRIPE_DOWN, "error")
        return _back()
    return redirect(url)


@bp.post("/connect")
@verified_required
def connect() -> Response:
    return _onboard()


@bp.get("/connect/refresh")
@verified_required
def refresh() -> Response:
    # Stripe sends people here when an onboarding link expires, so make a fresh one.
    return _onboard()


@bp.get("/connect/done")
@verified_required
def done() -> Response:
    if not stripe_pay.enabled():
        abort(404)
    try:
        ready = stripe_pay.refresh_ready(current_user)
        db.session.commit()
    except stripe.StripeError:
        current_app.logger.exception("Stripe status check failed for user %s", current_user.id)
        flash(STRIPE_DOWN, "error")
        return _back()
    if ready:
        flash("Stripe is connected. People can now chip in by card or Apple Pay.", "success")
    else:
        flash("Stripe still needs a few details. Finish setup to take card gifts.", "info")
    return _back()


@bp.post("/dashboard")
@verified_required
def dashboard() -> Response:
    if not stripe_pay.enabled() or current_user.stripe_account_id is None:
        abort(404)
    try:
        return redirect(stripe_pay.dashboard_url(current_user.stripe_account_id))
    except stripe.StripeError:
        current_app.logger.exception("Stripe dashboard link failed for user %s", current_user.id)
        flash(STRIPE_DOWN, "error")
        return _back()
