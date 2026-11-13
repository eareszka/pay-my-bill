import os
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User, utcnow

# A developer's .env must never reach real services from tests. load_dotenv() never
# overrides variables that are already set, so blanking them here wins.
for _key in (
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "STRIPE_CONNECT_WEBHOOK_SECRET",
    "PLATFORM_FEE_RATE",
    "BREVO_API_KEY",
    "MAIL_SERVER",
    "R2_BUCKET",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
):
    os.environ[_key] = ""
# Tests run as local development; the production checks have their own tests.
os.environ["FLASK_ENV"] = "development"

PASSWORD = "correct-horse"  # noqa: S105 - test fixture


@pytest.fixture
def app(tmp_path: Path) -> Iterator[Flask]:
    app = create_app(
        {
            "PHOTO_DIR": str(tmp_path / "photos"),
            "R2_BUCKET": "",
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "MAIL_ASYNC": False,
            "SERVER_NAME": "localhost",
            "APP_URL": "http://localhost",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


MakeUser = Callable[..., User]


@pytest.fixture
def make_user(app: Flask) -> MakeUser:
    def make(username: str = "alice", verified: bool = True, **fields: object) -> User:
        user = User(
            username=username,
            email=f"{username}@example.com",
            password_hash=generate_password_hash(PASSWORD),
            email_verified_at=utcnow() if verified else None,
            **fields,
        )
        db.session.add(user)
        db.session.commit()
        return user

    return make


def login_as(client: FlaskClient, user: User) -> None:
    with client.session_transaction() as session:
        session["_user_id"] = user.get_id()
        session["_fresh"] = True
