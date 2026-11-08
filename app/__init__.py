"""Pay My Bill application factory."""

import logging
import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


def database_url(raw: str) -> str:
    """Pin Postgres URLs to psycopg 3, whatever scheme the host hands us."""
    scheme, sep, rest = raw.partition("://")
    if sep and scheme.lower().split("+")[0] in {"postgres", "postgresql"}:
        return f"postgresql+psycopg://{rest}"
    return raw


def format_date(value: datetime) -> str:
    return f"{value:%b} {value.day}, {value.year}"


def create_app(config: dict[str, Any] | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-not-secret"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///pay_my_bill.db"),
        MAIL_SERVER=os.environ.get("MAIL_SERVER", ""),
        MAIL_PORT=int(os.environ.get("MAIL_PORT") or 587),
        MAIL_USERNAME=os.environ.get("MAIL_USERNAME", ""),
        MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", ""),
        BREVO_API_KEY=os.environ.get("BREVO_API_KEY", ""),
        MAIL_FROM=os.environ.get("MAIL_FROM", "Pay My Bill <no-reply@example.com>"),
        # Base URL for links in emails sent outside a request (the reminder command).
        APP_URL=os.environ.get("APP_URL", "http://localhost:5000"),
        CONTACT_EMAIL=os.environ.get("CONTACT_EMAIL", "support@example.com"),
        # Donors leave for their payment app mid-form, so tokens last for the session.
        WTF_CSRF_TIME_LIMIT=None,
    )
    if config:
        app.config.update(config)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url(app.config["SQLALCHEMY_DATABASE_URI"])
    app.logger.setLevel(logging.INFO)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # type: ignore[method-assign]

    from app import models  # noqa: F401
    from app.extensions import csrf, db, login_manager, migrate

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from app import auth, errors, seed  # noqa: F401

    seed.register(app)
    errors.register(app)

    from app.routes.admin import bp as admin_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.gifts import bp as gifts_bp
    from app.routes.health import bp as health_bp
    from app.routes.leaders import bp as leaders_bp
    from app.routes.main import bp as main_bp
    from app.routes.posts import bp as posts_bp
    from app.routes.profile import bp as profile_bp
    from app.routes.reports import bp as reports_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(gifts_bp)
    app.register_blueprint(leaders_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)

    from app.money import format_cents

    app.add_template_filter(format_cents, "cents")
    app.add_template_filter(format_date, "date")
    app.jinja_env.globals.update(
        MAX_GOAL=format_cents(models.MAX_GOAL_CENTS),
        MAX_OPEN_POSTS=models.MAX_OPEN_POSTS,
        PostStatus=models.PostStatus,
        DonationStatus=models.DonationStatus,
        ReactionKind=models.ReactionKind,
        LEGAL_UPDATED="November 8, 2026",
        CONTACT_EMAIL=app.config["CONTACT_EMAIL"],
    )
    return app
