from pathlib import Path

import pytest
from flask.testing import FlaskClient

from app import create_app
from app.security import content_security_policy


def test_every_response_sends_security_headers(client: FlaskClient) -> None:
    for path in ("/", "/login", "/no-such-page"):
        headers = client.get(path).headers
        policy = headers["Content-Security-Policy"]
        assert "script-src 'self'" in policy
        assert "frame-ancestors 'none'" in policy
        assert "form-action 'self' https://*.stripe.com;" in policy
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["Referrer-Policy"] == "same-origin"
        # Tests run on http://localhost, so no HSTS.
        assert "Strict-Transport-Security" not in headers


def test_photos_may_come_from_the_r2_origin() -> None:
    policy = content_security_policy("https://pub-abc.r2.dev/some/path")
    assert "img-src 'self' https://pub-abc.r2.dev;" in policy
    assert "img-src 'self';" in content_security_policy("")


@pytest.mark.parametrize(
    ("app_url", "secure"), [("https://pay.example", True), ("http://localhost:5000", False)]
)
def test_cookie_and_hsts_follow_app_url(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, app_url: str, secure: bool
) -> None:
    monkeypatch.setenv("APP_URL", app_url)
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "PHOTO_DIR": str(tmp_path),
        }
    )
    assert app.config["SESSION_COOKIE_SECURE"] is secure
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    # CSRF is on here, so the login form writes a session cookie.
    resp = app.test_client().get("/login")
    cookie = resp.headers["Set-Cookie"]
    assert "SameSite=Lax" in cookie
    assert ("; Secure" in cookie) is secure
    assert ("Strict-Transport-Security" in resp.headers) is secure
    if secure:
        assert resp.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
