"""Thin wrapper around Stripe Connect (ADR 0014), so routes and tests share one seam."""

from decimal import ROUND_CEILING, Decimal

import stripe
from flask import current_app
from stripe.params.checkout import SessionCreateParamsPaymentIntentData

from app.models import User
from app.money import format_cents


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


def _cents_up(value: Decimal) -> int:
    return int(value.to_integral_value(rounding=ROUND_CEILING))


def platform_fee_rate() -> Decimal:
    return Decimal(current_app.config["PLATFORM_FEE_RATE"])


def fee_terms() -> dict[str, str]:
    # The card form shows these and estimates what the recipient gets with them.
    rate = platform_fee_rate()
    return {
        "card_rate": str(CARD_FEE_RATE),
        "card_fixed": str(CARD_FEE_FIXED_CENTS),
        "platform_rate": str(rate),
        "platform_pct": f"{float(rate * 100):g}%",
    }


def split(paid_cents: int) -> tuple[int, int, int]:
    """Stripe's fee (US cards), Pay My Bill's fee, and what the recipient keeps (ADR 0016)."""
    stripe_fee = _cents_up(paid_cents * CARD_FEE_RATE) + CARD_FEE_FIXED_CENTS
    platform_fee = _cents_up(paid_cents * platform_fee_rate())
    return stripe_fee, platform_fee, paid_cents - stripe_fee - platform_fee


def checkout_url(
    *,
    post_id: int,
    title: str,
    donor_id: int,
    donor_email: str,
    recipient: str,
    destination: str,
    paid_cents: int,
    success_url: str,
    cancel_url: str,
) -> str:
    stripe_fee, platform_fee, net = split(paid_cents)
    metadata = {
        "post_id": str(post_id),
        "donor_id": str(donor_id),
        "gift_cents": str(net),
        "fee_cents": str(stripe_fee + platform_fee),
        "platform_fee_cents": str(platform_fee),
    }
    payment_intent: SessionCreateParamsPaymentIntentData = {"metadata": metadata}
    if platform_fee:
        payment_intent["application_fee_amount"] = platform_fee
    session = client().v1.checkout.sessions.create(
        params={
            "mode": "payment",
            # The fee estimate assumes card pricing, so no Klarna, bank, or crypto.
            # Apple Pay and Google Pay are card wallets and still show.
            "allowed_payment_method_types": ["card"],
            "customer_email": donor_email,
            "line_items": [
                {
                    "quantity": 1,
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": paid_cents,
                        "product_data": {
                            "name": f"Gift to {recipient}",
                            "description": f"For “{title}”. Card and Pay My Bill fees come "
                            f"out of it, so {recipient} gets about {format_cents(net)}.",
                        },
                    },
                }
            ],
            # A direct charge on the recipient's account (Managed Risk, ADR 0014): Stripe
            # takes its fee from the charge and Pay My Bill's application fee goes to the
            # platform, so the recipient keeps the rest (ADR 0016).
            "payment_intent_data": payment_intent,
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
