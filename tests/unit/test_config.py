import pytest

from app import create_app, database_url


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("postgres://u:p@h:5432/db", "postgresql+psycopg://u:p@h:5432/db"),
        ("postgresql://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg2://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("postgresql+psycopg://u:p@h/db", "postgresql+psycopg://u:p@h/db"),
        ("sqlite:///pay_my_bill.db", "sqlite:///pay_my_bill.db"),
    ],
)
def test_database_url(raw: str, expected: str) -> None:
    assert database_url(raw) == expected


def test_app_boots_against_postgres_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:1/db")
    app = create_app()
    assert app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql+psycopg://")
