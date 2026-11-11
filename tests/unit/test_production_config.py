import pytest

from app import DEV_SECRET_KEY, create_app

REAL_KEY = "a-random-value-that-is-long-enough-1234"  # noqa: S105 - a test value


def deployed(monkeypatch: pytest.MonkeyPatch, flask_env: str | None = None, **env: str) -> None:
    for key in ("FLASK_ENV", "FLASK_DEBUG", "SECRET_KEY", "APP_URL"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    if flask_env is not None:
        monkeypatch.setenv("FLASK_ENV", flask_env)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    # Keeps a developer's .env from filling in what the test removed.
    monkeypatch.setattr("app.load_dotenv", lambda: None)


@pytest.mark.parametrize("flask_env", [None, "production", "Production", " production", "staging"])
@pytest.mark.parametrize("key", [None, "", "change-me", DEV_SECRET_KEY, "x" * 31, " " * 40])
def test_anything_but_development_needs_a_real_key(
    monkeypatch: pytest.MonkeyPatch, flask_env: str | None, key: str | None
) -> None:
    env = {"APP_URL": "https://pay.example"}
    if key is not None:
        env["SECRET_KEY"] = key
    deployed(monkeypatch, flask_env, **env)
    with pytest.raises(RuntimeError, match="at least 32 characters"):
        create_app()


@pytest.mark.parametrize("url", [None, "http://pay.example"])
def test_anything_but_development_needs_an_https_app_url(
    monkeypatch: pytest.MonkeyPatch, url: str | None
) -> None:
    env = {"SECRET_KEY": REAL_KEY}
    if url is not None:
        env["APP_URL"] = url
    deployed(monkeypatch, **env)
    with pytest.raises(RuntimeError, match="APP_URL"):
        create_app()


def test_production_starts_with_real_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    deployed(monkeypatch, "production", SECRET_KEY=REAL_KEY, APP_URL="https://pay.example")
    assert create_app().config["SECRET_KEY"] == REAL_KEY


@pytest.mark.parametrize("flask_env", ["development", " Development "])
def test_development_keeps_the_fallback(monkeypatch: pytest.MonkeyPatch, flask_env: str) -> None:
    deployed(monkeypatch, flask_env)
    assert create_app().config["SECRET_KEY"] == DEV_SECRET_KEY


def test_debug_and_tests_keep_the_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    deployed(monkeypatch, FLASK_DEBUG="1")
    assert create_app().config["SECRET_KEY"] == DEV_SECRET_KEY
    monkeypatch.delenv("FLASK_DEBUG")
    assert create_app({"TESTING": True}).testing
