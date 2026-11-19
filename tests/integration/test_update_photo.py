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
    assert "Remove update photo<" in page


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


def with_both(app: Flask, post: Post) -> tuple[Path, Path]:
    post.photo_key = photos.save(photos.process(jpeg()))
    post.update_body, post.update_posted_at = NOTE, utcnow()
    post.update_photo_key = photos.save(photos.process(jpeg("plum")))
    db.session.commit()
    return stored(app, post.photo_key), stored(app, post.update_photo_key)


def test_poster_removes_only_the_update_photo(
    app: Flask, client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    post = owing_post(poster, make_user("dev_tom"))
    cover, update = with_both(app, post)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f'action="/posts/{post.id}/update-photo/delete"' in page
    client.post(f"/posts/{post.id}/update-photo/delete")
    assert post.update_photo_key is None and not update.exists()
    assert post.photo_key and cover.exists()


def test_removing_post_photos_keeps_the_update_photo(
    app: Flask, client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    post = owing_post(poster, make_user("dev_tom"))
    cover, update = with_both(app, post)
    client.post(f"/posts/{post.id}/photo/delete")
    assert post.photo_key is None and not cover.exists()
    assert post.update_photo_key and update.exists()


def test_deleting_the_post_deletes_both(
    app: Flask, client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    post = owing_post(poster, make_user("dev_tom"))
    files = with_both(app, post)
    client.post(f"/posts/{post.id}/delete")
    assert not any(file.exists() for file in files)


def test_a_failed_commit_discards_the_stored_photo(
    app: Flask,
    client: FlaskClient,
    poster: User,
    make_user: MakeUser,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    post = owing_post(poster, make_user("dev_tom"))
    keys: list[str] = []
    save = photos.save
    monkeypatch.setattr(photos, "save", lambda data: keys.append(save(data)) or keys[-1])
    monkeypatch.setattr(db.session, "commit", MagicMock(side_effect=OSError("db down")))
    with pytest.raises(OSError):
        client.post(f"/posts/{post.id}/update", data={"note": NOTE, "photo": (jpeg(), "a.jpg")})
    assert keys and not stored(app, keys[0]).exists()


def test_photo_is_not_decoded_when_the_note_is_refused(
    client: FlaskClient, poster: User, make_user: MakeUser, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app import forms

    post = owing_post(poster, make_user("dev_tom"))
    process = MagicMock()
    monkeypatch.setattr(forms, "process", process)
    resp = client.post(
        f"/posts/{post.id}/update", data={"note": "Short", "photo": (jpeg(), "a.jpg")}
    )
    assert resp.status_code == 400
    process.assert_not_called()


def test_update_takes_a_one_photo_body(
    client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    post = owing_post(poster, make_user("dev_tom"))
    huge = io.BytesIO(b"\0" * (10 * 1024 * 1024))
    resp = client.post(f"/posts/{post.id}/update", data={"note": NOTE, "photo": (huge, "a.jpg")})
    assert resp.status_code == 413


@pytest.mark.parametrize(
    ("path", "gone", "kept"),
    [
        ("remove-update-photo", "update_photo_key", "photo_key"),
        ("remove-photo", "photo_key", "update_photo_key"),
    ],
)
def test_admin_removes_one_kind_of_photo(
    app: Flask, client: FlaskClient, make_user: MakeUser, path: str, gone: str, kept: str
) -> None:
    post = owing_post(make_user("maria_g"), make_user("dev_tom"))
    with_both(app, post)
    files = {name: stored(app, getattr(post, name)) for name in (gone, kept)}
    db.session.add(Report(reporter=make_user("ann"), post=post, reason=ReportReason.PHOTO))
    db.session.commit()
    login_as(client, make_user("boss", is_admin=True))
    queue = client.get("/admin").get_data(as_text=True)
    assert f'src="/media/{post.update_photo_key}"' in queue
    assert f'action="/admin/posts/{post.id}/remove-update-photo"' in queue
    client.post(f"/admin/posts/{post.id}/{path}")
    assert getattr(post, gone) is None and not files[gone].exists()
    assert getattr(post, kept) and files[kept].exists()
