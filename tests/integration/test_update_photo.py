import io
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import photos
from app.extensions import db
from app.models import (
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    PostKind,
    Report,
    ReportReason,
    User,
    utcnow,
)
from tests.conftest import MakeUser, jpeg, login_as

NOTE = "Made rent on time. Thank you all so much."


@pytest.fixture
def poster(client: FlaskClient, make_user: MakeUser) -> User:
    user = make_user("maria_g", venmo_handle="@maria-g")
    login_as(client, user)
    return user


def owing_post(owner: User, donor: User) -> Post:
    post = Post(user=owner, kind=PostKind.NEED, title="Rent", body="Short.", goal_cents=9_000)
    post.donations.append(
        Donation(
            donor=donor,
            amount_cents=2_000,
            method=PaymentMethod.VENMO,
            status=DonationStatus.CONFIRMED,
            resolved_at=utcnow(),
        )
    )
    db.session.add(post)
    db.session.commit()
    post.close()
    db.session.commit()
    return post


def stored(app: Flask, key: str | None) -> Path:
    assert key
    return Path(app.config["PHOTO_DIR"]) / key


def test_update_can_carry_a_photo(
    app: Flask, client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    post = owing_post(poster, make_user("dev_tom"))
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert 'enctype="multipart/form-data"' in page
    assert "Never a receipt." in page
    resp = client.post(f"/posts/{post.id}/update", data={"note": NOTE, "photo": (jpeg(), "a.jpg")})
    assert resp.status_code == 302
    assert stored(app, post.update_photo_key).read_bytes()[8:12] == b"WEBP"
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f'class="update-photo" src="/media/{post.update_photo_key}"' in page
    assert "Remove photo<" in page


def test_photo_stays_optional(client: FlaskClient, poster: User, make_user: MakeUser) -> None:
    post = owing_post(poster, make_user("dev_tom"))
    client.post(f"/posts/{post.id}/update", data={"note": NOTE, "photo": (io.BytesIO(), "")})
    assert post.update_body == NOTE
    assert post.update_photo_key is None


def test_bad_photo_keeps_the_update_unposted(
    client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    post = owing_post(poster, make_user("dev_tom"))
    resp = client.post(
        f"/posts/{post.id}/update",
        data={"note": NOTE, "photo": (io.BytesIO(b"\0" * (2 * 1024 * 1024)), "big.jpg")},
    )
    # Read in full (not cut off for size) and refused as a photo.
    assert resp.status_code == 400
    assert "isn&#39;t a photo we can read" in resp.get_data(as_text=True)
    assert post.update_body is None


def test_storage_failure_keeps_the_update_unposted(
    client: FlaskClient, poster: User, make_user: MakeUser, monkeypatch: pytest.MonkeyPatch
) -> None:
    post = owing_post(poster, make_user("dev_tom"))
    monkeypatch.setattr(photos, "save", MagicMock(side_effect=OSError("bucket down")))
    resp = client.post(f"/posts/{post.id}/update", data={"note": NOTE, "photo": (jpeg(), "a.jpg")})
    assert resp.status_code == 503
    assert "We couldn&#39;t save that photo." in resp.get_data(as_text=True)
    assert post.update_body is None


@pytest.mark.parametrize("path", ["photo/delete", "delete"])
def test_removing_photos_or_the_post_deletes_the_update_photo(
    app: Flask, client: FlaskClient, poster: User, make_user: MakeUser, path: str
) -> None:
    post = owing_post(poster, make_user("dev_tom"))
    client.post(f"/posts/{post.id}/update", data={"note": NOTE, "photo": (jpeg(), "a.jpg")})
    file = stored(app, post.update_photo_key)
    client.post(f"/posts/{post.id}/{path}")
    assert post.update_photo_key is None
    assert not file.exists()


def test_admin_sees_and_removes_the_update_photo(
    app: Flask, client: FlaskClient, make_user: MakeUser
) -> None:
    post = owing_post(make_user("maria_g"), make_user("dev_tom"))
    post.update_body = NOTE
    post.update_photo_key = photos.save(photos.process(jpeg()))
    db.session.add(Report(reporter=make_user("ann"), post=post, reason=ReportReason.PHOTO))
    db.session.commit()
    file = stored(app, post.update_photo_key)
    login_as(client, make_user("boss", is_admin=True))
    queue = client.get("/admin").get_data(as_text=True)
    assert f'src="/media/{post.update_photo_key}"' in queue
    assert "Remove photo<" in queue
    client.post(f"/admin/posts/{post.id}/remove-photo")
    assert post.update_photo_key is None
    assert not file.exists()
