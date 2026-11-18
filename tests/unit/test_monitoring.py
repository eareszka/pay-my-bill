from unittest.mock import MagicMock

import pytest

from app import create_app, monitoring
from tests.unit.test_production_config import REAL_KEY, deployed


def test_scrub_drops_everything_personal() -> None:
    event = {
        "request": {
            "url": "https://yearnly.app/reset/abc.def-123",
            "method": "POST",
            "data": {"password": "hunter22"},
            "cookies": {"session": "s3cret"},
            "headers": {"Authorization": "x"},
            "query_string": "token=abc",
            "env": {"REMOTE_ADDR": "1.2.3.4"},
        },
        "user": {"ip_address": "1.2.3.4"},
    }
    scrubbed = monitoring.scrub(event, None)
    assert scrubbed["request"] == {"url": "https://yearnly.app/reset/[token]", "method": "POST"}
    assert "user" not in scrubbed


@pytest.mark.parametrize(
    ("url", "clean"),
    [
        ("https://yearnly.app/verify/tok", "https://yearnly.app/verify/[token]"),
        (
            "https://yearnly.app/gifts/answer/tok/confirm",
            "https://yearnly.app/gifts/answer/[token]/confirm",
        ),
        ("https://yearnly.app/posts/4", "https://yearnly.app/posts/4"),
    ],
)
def test_scrub_cuts_tokens_out_of_urls(url: str, clean: str) -> None:
    assert monitoring.scrub({"request": {"url": url}}, None)["request"]["url"] == clean


def test_no_dsn_means_no_sentry(monkeypatch: pytest.MonkeyPatch) -> None:
    init = MagicMock()
    monkeypatch.setattr("sentry_sdk.init", init)
    assert monitoring.init("", "https://yearnly.app") is False
    init.assert_not_called()


def test_production_reports_errors_and_hides_sql_values(monkeypatch: pytest.MonkeyPatch) -> None:
    init = MagicMock()
    monkeypatch.setattr("sentry_sdk.init", init)
    deployed(
        monkeypatch,
        SECRET_KEY=REAL_KEY,
        APP_URL="https://yearnly.app",
        SENTRY_DSN="https://key@o1.ingest.sentry.io/1",
    )
    app = create_app()
    assert app.config["SQLALCHEMY_ENGINE_OPTIONS"]["hide_parameters"] is True
    kwargs = init.call_args.kwargs
    assert kwargs["dsn"] == "https://key@o1.ingest.sentry.io/1"
    assert kwargs["send_default_pii"] is False
    assert kwargs["max_request_body_size"] == "never"
    assert kwargs["before_send"] is monitoring.scrub


def test_development_never_reports(monkeypatch: pytest.MonkeyPatch) -> None:
    init = MagicMock()
    monkeypatch.setattr("sentry_sdk.init", init)
    deployed(monkeypatch, "development", SENTRY_DSN="https://key@o1.ingest.sentry.io/1")
    create_app()
    init.assert_not_called()
