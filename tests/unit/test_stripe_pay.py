import stripe
from flask import Flask

from app import stripe_pay


def test_client_uses_configured_key(app: Flask) -> None:
    app.config["STRIPE_SECRET_KEY"] = "sk_test_fake"  # noqa: S105 - test fixture
    assert isinstance(stripe_pay.client(), stripe.StripeClient)
    assert stripe_pay.enabled()
