"""Pay My Bill application factory."""

import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask


def create_app(config: dict[str, Any] | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-not-secret"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///pay_my_bill.db"),
    )
    if config:
        app.config.update(config)

    from app import models  # noqa: F401
    from app.extensions import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    from app import seed

    seed.register(app)

    from app.routes.health import bp as health_bp

    app.register_blueprint(health_bp)
    return app
