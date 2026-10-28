"""Pay My Bill application factory."""

import logging
import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


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
        MAIL_FROM=os.environ.get("MAIL_FROM", "Pay My Bill <no-reply@example.com>"),
    )
    if config:
        app.config.update(config)
    app.logger.setLevel(logging.INFO)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # type: ignore[method-assign]

    from app import models  # noqa: F401
    from app.extensions import csrf, db, login_manager, migrate

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from app import auth, seed  # noqa: F401

    seed.register(app)

    from app.routes.auth import bp as auth_bp
    from app.routes.health import bp as health_bp
    from app.routes.main import bp as main_bp
    from app.routes.posts import bp as posts_bp
    from app.routes.profile import bp as profile_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(posts_bp)

    from app.money import format_cents

    app.add_template_filter(format_cents, "cents")
    app.jinja_env.globals.update(
        MAX_GOAL=format_cents(models.MAX_GOAL_CENTS),
        MAX_OPEN_POSTS=models.MAX_OPEN_POSTS,
        PostStatus=models.PostStatus,
    )
    return app
