"""Thin wrapper around Stripe Connect (ADR 0014), so routes and tests share one seam."""

from decimal import ROUND_CEILING, Decimal

import stripe
from flask import current_app

from app.models import User


def enabled() -> bool:
    return bool(current_app.config["STRIPE_SECRET_KEY"])


def client() -> stripe.StripeClient:
    return stripe.StripeClient(current_app.config["STRIPE_SECRET_KEY"])


# Express dashboards with Stripe covering losses (Managed Risk) are a public preview,
# so account creation pins this version (ADR 0014).
EXPRESS_MANAGED_RISK_VERSION = "2026-10-28.preview"


def account_ready(account: stripe.Account) -> bool:
    # Direct charges need the account able to take card payments and pay out.
    # A new account may lack these keys, and StripeObject raises on a missing attribute.
    return bool(
        getattr(account, "charges_enabled", False) and getattr(account, "payouts_enabled", False)
    )


# Recipients are people taking gifts, not businesses, so we answer Stripe's business
# questions for them and onboarding only asks about the person and their bank (#98).
GIFT_MCC = "7299"  # Miscellaneous personal services
STATEMENT_DESCRIPTOR = "PAY MY BILL"
PRODUCT_DESCRIPTION = (
    "Personal gifts from friends and community members through Pay My Bill, where people "
    "post everyday wants and needs and others chip in by card. Nothing is sold."
)


def ensure_account(user: User, profile_url: str) -> str:
    if user.stripe_account_id is None:
        # Accounts v2: Stripe collects its fees from the recipient and covers losses
        # it can't recover (Managed Risk), and the recipient gets an Express dashboard.
        account = client().v2.core.accounts.create(
            params={
                "contact_email": user.email,
                "display_name": user.username,
                "dashboard": "express",
                "identity": {
                    "country": "US",
                    "entity_type": "individual",
                    "individual": {"email": user.email},
                },
                "defaults": {
                    "responsibilities": {
                        "fees_collector": "stripe",
                        "losses_collector": "stripe",
                    },
                    "profile": {
                        "business_url": profile_url,
                        "product_description": PRODUCT_DESCRIPTION,
                    },
                },
                "configuration": {
                    "merchant": {
                        "capabilities": {"card_payments": {"requested": True}},
                        "mcc": GIFT_MCC,
                        "statement_descriptor": {"descriptor": STATEMENT_DESCRIPTOR},
                        "support": {"url": profile_url},
                    }
                },
                "metadata": {"user_id": str(user.id)},
            },
            options={"stripe_version": EXPRESS_MANAGED_RISK_VERSION},
        )
        user.stripe_account_id = account.id
    return user.stripe_account_id


def onboarding_url(account_id: str, refresh_url: str, return_url: str) -> str:
    link = client().v2.core.account_links.create(
        params={
            "account": account_id,
            "use_case": {
                "type": "account_onboarding",
                "account_onboarding": {"return_url": return_url, "refresh_url": refresh_url},
            },
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
            # The fee gross-up assumes card pricing, so no Klarna, bank, or crypto.
            # Apple Pay and Google Pay are card wallets and still show.
            "allowed_payment_method_types": ["card"],
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
            # A direct charge on the recipient's account (Managed Risk, ADR 0014): Stripe
            # takes its fee from the charge, which the donor's extra covers, so the
            # recipient keeps the whole gift.
            "payment_intent_data": {"metadata": metadata},
            "metadata": metadata,
            "success_url": success_url,
            "cancel_url": cancel_url,
        },
        options={"stripe_account": destination},
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
