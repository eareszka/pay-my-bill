import pytest
from flask.testing import FlaskClient
from sqlalchemy import func, select

from app.extensions import db
from app.models import User


@pytest.mark.parametrize(
    ("path", "heading"), [("/terms", b"Terms of Service"), ("/privacy", b"Privacy Policy")]
)
def test_legal_pages_render(client: FlaskClient, path: str, heading: bytes) -> None:
    resp = client.get(path)
    assert resp.status_code == 200
    assert heading in resp.data
    assert b"never holds" in resp.data or b"never see" in resp.data


def test_footer_links_legal_pages(client: FlaskClient) -> None:
    resp = client.get("/rules")
    assert b'href="/terms"' in resp.data
    assert b'href="/privacy"' in resp.data


def test_signup_links_terms_and_requires_agreement(client: FlaskClient) -> None:
    page = client.get("/signup")
    assert b'href="/terms"' in page.data
    resp = client.post(
        "/signup",
        data={
            "username": "newbie",
            "email": "newbie@example.com",
            "password": "s3cret-pass",
            "confirm": "s3cret-pass",
        },
    )
    assert resp.status_code == 200
    assert b"agree to the Terms and Privacy Policy" in resp.data
    assert db.session.scalar(select(func.count()).select_from(User)) == 0
