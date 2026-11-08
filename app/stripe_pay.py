"""Thin wrapper around Stripe Connect (ADR 0014), so routes and tests share one seam."""

from decimal import ROUND_CEILING, Decimal

import stripe
from flask import current_app

from app.models import User


def enabled() -> bool:
    return bool(current_app.config["STRIPE_SECRET_KEY"])


def client() -> stripe.StripeClient:
    return stripe.StripeClient(current_app.config["STRIPE_SECRET_KEY"])


def account_ready(account: stripe.Account) -> bool:
    # Destination charges need the connected account able to take transfers and pay out.
    # A new account may lack these keys, and StripeObject raises on a missing attribute.
    capabilities = getattr(account, "capabilities", None)
    transfers = getattr(capabilities, "transfers", None)
    return bool(account.details_submitted and account.payouts_enabled and transfers == "active")


def ensure_account(user: User) -> str:
    if user.stripe_account_id is None:
        account = client().v1.accounts.create(
            params={
                "type": "express",
                "country": "US",
                "email": user.email,
                "capabilities": {"transfers": {"requested": True}},
                "business_type": "individual",
                "business_profile": {"product_description": "Personal gifts on Pay My Bill"},
                "metadata": {"user_id": str(user.id)},
            }
        )
        user.stripe_account_id = account.id
    return user.stripe_account_id


def onboarding_url(account_id: str, refresh_url: str, return_url: str) -> str:
    link = client().v1.account_links.create(
        params={
            "account": account_id,
            "refresh_url": refresh_url,
            "return_url": return_url,
            "type": "account_onboarding",
        }
    )
    return link.url


def refresh_ready(user: User) -> bool:
    if user.stripe_account_id is None:
        return False
    user.stripe_ready = account_ready(client().v1.accounts.retrieve(user.stripe_account_id))
    return user.stripe_ready


def dashboard_url(account_id: str) -> str:
    return client().v1.accounts.login_links.create(account_id).url


CARD_FEE_RATE = Decimal("0.029")
CARD_FEE_FIXED_CENTS = 30


def charge_for(gift_cents: int) -> int:
    """What the donor pays so the recipient still gets the whole gift after Stripe's fee."""
    total = (gift_cents + CARD_FEE_FIXED_CENTS) / (1 - CARD_FEE_RATE)
    return int(total.to_integral_value(rounding=ROUND_CEILING))


def checkout_url(
    *,
    post_id: int,
    title: str,
    donor_id: int,
    donor_email: str,
    recipient: str,
    destination: str,
    gift_cents: int,
    success_url: str,
    cancel_url: str,
) -> str:
    total = charge_for(gift_cents)
    metadata = {
        "post_id": str(post_id),
        "donor_id": str(donor_id),
        "gift_cents": str(gift_cents),
        "fee_cents": str(total - gift_cents),
    }
    session = client().v1.checkout.sessions.create(
        params={
            "mode": "payment",
            "customer_email": donor_email,
            "line_items": [
                {
                    "quantity": 1,
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": total,
                        "product_data": {
                            "name": f"Gift to {recipient}",
                            "description": f"For “{title}”. Includes the card fee, so "
                            f"{recipient} gets the full gift.",
                        },
                    },
                }
            ],
            # A destination charge: the recipient gets exactly the gift, and the fee
            # covers Stripe's cut on the platform side (ADR 0014).
            "payment_intent_data": {
                "transfer_data": {"destination": destination, "amount": gift_cents},
                "metadata": metadata,
            },
            "metadata": metadata,
            "success_url": success_url,
            "cancel_url": cancel_url,
        }
    )
    return session.url or ""


def webhook_secrets() -> list[str]:
    # Stripe signs connected-account events (account.updated) on a separate Connect
    # endpoint with its own secret, so both point here.
    keys = ("STRIPE_WEBHOOK_SECRET", "STRIPE_CONNECT_WEBHOOK_SECRET")
    return [current_app.config[key] for key in keys if current_app.config[key]]


def parse_event(payload: bytes, signature: str) -> stripe.Event:
    error: stripe.SignatureVerificationError | None = None
    for secret in webhook_secrets():
        try:
            event: stripe.Event = stripe.Webhook.construct_event(payload, signature, secret)
        except stripe.SignatureVerificationError as exc:
            error = exc
        else:
            return event
    assert error is not None  # noqa: S101 - callers check webhook_secrets() first
    raise error
