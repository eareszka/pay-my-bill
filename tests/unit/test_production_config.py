import pytest

from app import DEV_SECRET_KEY, create_app

REAL_KEY = "a-long-random-value"  # noqa: S105 - a test value


def production(monkeypatch: pytest.MonkeyPatch, **env: str) -> None:
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    for key in ("SECRET_KEY", "APP_URL"):
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    # Keeps a developer's .env from filling in what the test removed.
    monkeypatch.setattr("app.load_dotenv", lambda: None)


@pytest.mark.parametrize("key", [None, "change-me", "dev-only-not-secret", ""])
def test_production_needs_a_real_secret_key(
    monkeypatch: pytest.MonkeyPatch, key: str | None
) -> None:
    env = {"APP_URL": "https://pay.example"}
    if key is not None:
        env["SECRET_KEY"] = key
    production(monkeypatch, **env)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app()


@pytest.mark.parametrize("url", [None, "http://pay.example"])
def test_production_needs_an_https_app_url(
    monkeypatch: pytest.MonkeyPatch, url: str | None
) -> None:
    env = {"SECRET_KEY": REAL_KEY}
    if url is not None:
        env["APP_URL"] = url
    production(monkeypatch, **env)
    with pytest.raises(RuntimeError, match="APP_URL"):
        create_app()


def test_production_starts_with_real_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    production(monkeypatch, SECRET_KEY=REAL_KEY, APP_URL="https://pay.example")
    assert create_app().config["SECRET_KEY"] == REAL_KEY


def test_development_and_tests_keep_the_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    production(monkeypatch)
    monkeypatch.setenv("FLASK_ENV", "development")
    assert create_app().config["SECRET_KEY"] == DEV_SECRET_KEY
    monkeypatch.setenv("FLASK_ENV", "production")
    assert create_app({"TESTING": True}).testing
