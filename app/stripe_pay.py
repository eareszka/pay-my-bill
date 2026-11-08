"""Thin wrapper around Stripe Connect (ADR 0014), so routes and tests share one seam."""

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
