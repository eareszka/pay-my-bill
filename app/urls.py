from typing import Any

from flask import current_app, url_for


def site_url(endpoint: str, **values: Any) -> str:
    """An absolute link built from APP_URL, never the request's Host header (#150).

    Links go into emails and to Stripe, so a forged Host must not steer them.
    """
    base: str = current_app.config["APP_URL"]
    return base.rstrip("/") + url_for(endpoint, **values)
