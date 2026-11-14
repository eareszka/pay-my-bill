"""Yearnly application factory."""

import logging
import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix


def database_url(raw: str) -> str:
    """Pin Postgres URLs to psycopg 3, whatever scheme the host hands us."""
    scheme, sep, rest = raw.partition("://")
    if sep and scheme.lower().split("+")[0] in {"postgres", "postgresql"}:
        return f"postgresql+psycopg://{rest}"
    return raw


DEV_SECRET_KEY = "dev-only-not-secret"  # noqa: S105 - the local-only fallback
# Long enough that a placeholder, typo, or test value can't sign real sessions.
MIN_SECRET_KEY_LENGTH = 32
DEV_HINT = "For local work, set FLASK_ENV=development (see .env.example)."


def is_development(app: Flask) -> bool:
    return (
        app.testing or app.debug or os.environ.get("FLASK_ENV", "").strip().lower() == "development"
    )


def check_production(config: dict[str, Any]) -> None:
    """Refuse to start with forgeable or http-only settings (#152).

    Runs everywhere but clear development, so a deploy that forgets one more
    variable fails loudly instead of running on the local fallback key.
    """
    if len(config["SECRET_KEY"].strip()) < MIN_SECRET_KEY_LENGTH:
        raise RuntimeError(
            f"Set SECRET_KEY to a random value of at least {MIN_SECRET_KEY_LENGTH} characters. "
            + DEV_HINT
        )
    if not str(config["APP_URL"]).startswith("https://"):
        raise RuntimeError("Set APP_URL to the site's https address. " + DEV_HINT)


def format_date(value: datetime) -> str:
    return f"{value:%b} {value.day}, {value.year}"


def create_app(config: dict[str, Any] | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app_url = os.environ.get("APP_URL", "http://localhost:5000")
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", DEV_SECRET_KEY),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///pay_my_bill.db"),
        MAIL_SERVER=os.environ.get("MAIL_SERVER", ""),
        MAIL_PORT=int(os.environ.get("MAIL_PORT") or 587),
        MAIL_USERNAME=os.environ.get("MAIL_USERNAME", ""),
        MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", ""),
        BREVO_API_KEY=os.environ.get("BREVO_API_KEY", ""),
        # Request-path email goes to a background thread; tests send inline.
        MAIL_ASYNC=os.environ.get("MAIL_ASYNC", "1") != "0",
        MAIL_FROM=os.environ.get("MAIL_FROM", "Yearnly <no-reply@example.com>"),
        # The site address every absolute link is built from (app/urls.py), never the Host header.
        APP_URL=app_url,
        # Secure wherever the site is served over HTTPS; local http dev still works.
        SESSION_COOKIE_SECURE=app_url.startswith("https://"),
        SESSION_COOKIE_SAMESITE="Lax",
        CONTACT_EMAIL=os.environ.get("CONTACT_EMAIL", "support@example.com"),
        STRIPE_SECRET_KEY=os.environ.get("STRIPE_SECRET_KEY", ""),
        STRIPE_WEBHOOK_SECRET=os.environ.get("STRIPE_WEBHOOK_SECRET", ""),
        STRIPE_CONNECT_WEBHOOK_SECRET=os.environ.get("STRIPE_CONNECT_WEBHOOK_SECRET", ""),
        # Yearnly's cut of each card gift (ADR 0016); 0 turns it off.
        PLATFORM_FEE_RATE=os.environ.get("PLATFORM_FEE_RATE") or "0.01",
        # Post photos go to Cloudflare R2 when a bucket is set, else to PHOTO_DIR (ADR 0015).
        R2_ACCOUNT_ID=os.environ.get("R2_ACCOUNT_ID", ""),
        R2_ACCESS_KEY_ID=os.environ.get("R2_ACCESS_KEY_ID", ""),
        R2_SECRET_ACCESS_KEY=os.environ.get("R2_SECRET_ACCESS_KEY", ""),
        R2_BUCKET=os.environ.get("R2_BUCKET", ""),
        R2_PUBLIC_URL=os.environ.get("R2_PUBLIC_URL", ""),
        PHOTO_DIR=os.environ.get("PHOTO_DIR", ""),
        # Forms are small; the photo upload raises its own limit (#155).
        MAX_CONTENT_LENGTH=1024 * 1024,
        # Donors leave for their payment app mid-form, so tokens last for the session.
        WTF_CSRF_TIME_LIMIT=None,
    )
    if config:
        app.config.update(config)
    if not is_development(app):
        check_production(app.config)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url(app.config["SQLALCHEMY_DATABASE_URI"])
    app.logger.setLevel(logging.INFO)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # type: ignore[method-assign]

    from app import models  # noqa: F401
    from app.stripe_pay import parse_fee_rate

    parse_fee_rate(str(app.config["PLATFORM_FEE_RATE"]))
    from app.extensions import csrf, db, login_manager, migrate
    from app.photos import MAX_UPLOAD_BYTES

    @app.before_request
    def photo_upload_limit() -> None:
        # The new-post form is the only one with a photo, so the only one allowed a large
        # body. Registered before CSRF, which reads the form in its own before_request (#155).
        if request.endpoint == "posts.new":
            request.max_content_length = MAX_UPLOAD_BYTES

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from app import auth, errors, photos, security, seed  # noqa: F401

    photos.init_app(app)
    security.init_app(app)

    seed.register(app)
    errors.register(app)

    from app.routes.admin import bp as admin_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.card_gifts import bp as card_bp
    from app.routes.gifts import bp as gifts_bp
    from app.routes.health import bp as health_bp
    from app.routes.leaders import bp as leaders_bp
    from app.routes.main import bp as main_bp
    from app.routes.posts import bp as posts_bp
    from app.routes.profile import bp as profile_bp
    from app.routes.reports import bp as reports_bp
    from app.routes.stripe_connect import bp as stripe_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(gifts_bp)
    app.register_blueprint(leaders_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(stripe_bp)
    app.register_blueprint(card_bp)

    from app import stripe_pay
    from app.money import format_cents

    app.add_template_filter(format_cents, "cents")
    app.add_template_filter(format_date, "date")
    app.jinja_env.globals.update(
        MAX_GOAL=format_cents(models.MAX_GOAL_CENTS),
        MAX_OPEN_POSTS=models.MAX_OPEN_POSTS,
        PostStatus=models.PostStatus,
        DonationStatus=models.DonationStatus,
        ReactionKind=models.ReactionKind,
        LEGAL_UPDATED="November 12, 2026",
        CONTACT_EMAIL=app.config["CONTACT_EMAIL"],
        stripe_enabled=stripe_pay.enabled,
    )
    return app
