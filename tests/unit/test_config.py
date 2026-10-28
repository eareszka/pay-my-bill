import pytest

from app import create_app, database_url
from app.extensions import db


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("postgres://u:p@h:5432/db", "postgresql+psycopg://u:p@h:5432/db"),
        ("postgresql://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("POSTGRES://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg2://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("sqlite:///pay_my_bill.db", "sqlite:///pay_my_bill.db"),
        ("sqlite:///:memory:", "sqlite:///:memory:"),
    ],
)
def test_database_url(raw: str, expected: str) -> None:
    assert database_url(raw) == expected


def test_env_postgres_url_uses_psycopg3(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:1/db")
    app = create_app()
    with app.app_context():
        assert db.engine.dialect.driver == "psycopg"


def test_config_override_is_normalized_too() -> None:
    app = create_app({"SQLALCHEMY_DATABASE_URI": "postgres://u:p@localhost:1/db"})
    with app.app_context():
        assert db.engine.dialect.driver == "psycopg"
