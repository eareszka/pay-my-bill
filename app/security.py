from urllib.parse import urlsplit

from flask import Flask
from werkzeug.wrappers import Response

# Card gifts, Connect onboarding, and the Express dashboard post to us, then
# redirect to Stripe. Chrome checks form-action on every hop, and Stripe may
# bounce between its own hosts, so any Stripe host is allowed.
STRIPE_FORM_TARGETS = "https://*.stripe.com"
HSTS = "max-age=31536000; includeSubDomains"


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}" if parts.scheme and parts.netloc else ""


def content_security_policy(photo_url: str) -> str:
    images = " ".join(filter(None, ("'self'", _origin(photo_url))))
    return "; ".join(
        (
            "default-src 'self'",
            f"img-src {images}",
            # The progress meter sets its fill with a style attribute.
            "style-src 'self'",
            "style-src-attr 'unsafe-inline'",
            "script-src 'self'",
            "object-src 'none'",
            "base-uri 'none'",
            f"form-action 'self' {STRIPE_FORM_TARGETS}",
            "frame-ancestors 'none'",
        )
    )


def init_app(app: Flask) -> None:
    https = app.config["APP_URL"].startswith("https://")
    policy = content_security_policy(app.config["R2_PUBLIC_URL"])

    @app.after_request
    def headers(response: Response) -> Response:
        response.headers.setdefault("Content-Security-Policy", policy)
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        if https:
            response.headers.setdefault("Strict-Transport-Security", HSTS)
        return response
