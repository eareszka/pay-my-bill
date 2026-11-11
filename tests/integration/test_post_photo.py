import io
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from flask import Flask
from flask.testing import FlaskClient
from PIL import Image
from sqlalchemy import select

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
)
from tests.conftest import PASSWORD, MakeUser, login_as

FORM = {
    "kind": "want",
    "title": "New running shoes",
    "body": "Training for my first 5K and my shoes are done.",
    "goal": "$90",
    "accept_rules": "y",
}


def jpeg() -> io.BytesIO:
    out = io.BytesIO()
    Image.new("RGB", (60, 40), "teal").save(out, "JPEG")
    out.seek(0)
    return out


def photo_dir(app: Flask) -> Path:
    return Path(app.config["PHOTO_DIR"])


def stored(app: Flask, post: Post) -> Path:
    assert post.photo_key
    return photo_dir(app) / post.photo_key


@pytest.fixture
def poster(client: FlaskClient, make_user: MakeUser) -> User:
    user = make_user("maria_g", venmo_handle="@maria-g")
    login_as(client, user)
    return user


def only_post() -> Post:
    return db.session.scalars(select(Post)).one()


def with_photo(app: Flask, user: User, title: str = "Shoes") -> Post:
    post = Post(user=user, kind=PostKind.WANT, title=title, body="For a 5K.", goal_cents=9_000)
    post.photo_key = photos.save(photos.process(jpeg()))
    db.session.add(post)
    db.session.commit()
    assert stored(app, post).exists()
    return post


def test_new_post_with_a_photo_shows_it(app: Flask, client: FlaskClient, poster: User) -> None:
    resp = client.post(
        "/posts/new",
        data={**FORM, "photo": (jpeg(), "shoes.jpg")},
        content_type="multipart/form-data",
    )
    post = only_post()
    assert resp.location == f"/posts/{post.id}"
    assert post.photo_key and post.photo_key.endswith(".webp")
    assert stored(app, post).read_bytes()[8:12] == b"WEBP"
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f'src="/media/{post.photo_key}" alt="Photo from maria_g"' in page
    assert "Remove photo" in page
    feed = client.get("/").get_data(as_text=True)
    assert f'<img class="ticket-photo" src="/media/{post.photo_key}"' in feed
    assert "has-photo" in feed


def test_photo_is_optional(client: FlaskClient, poster: User) -> None:
    client.post("/posts/new", data=FORM, content_type="multipart/form-data")
    post = only_post()
    assert post.photo_key is None
    assert "has-photo" not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_form_asks_for_a_photo_as_multipart(client: FlaskClient, poster: User) -> None:
    page = client.get("/posts/new").get_data(as_text=True)
    assert 'enctype="multipart/form-data"' in page
    assert 'accept="image/jpeg,image/png,image/webp"' in page
    assert "We remove its location data." in page


def test_unreadable_photo_keeps_the_form(client: FlaskClient, poster: User) -> None:
    resp = client.post(
        "/posts/new",
        data={**FORM, "photo": (io.BytesIO(b"not a photo"), "shoes.jpg")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert "That file isn&#39;t a photo we can read." in resp.get_data(as_text=True)
    assert db.session.scalars(select(Post)).first() is None


def test_storage_failure_keeps_the_form(
    client: FlaskClient, poster: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(photos, "save", MagicMock(side_effect=OSError("bucket down")))
    resp = client.post(
        "/posts/new",
        data={**FORM, "photo": (jpeg(), "shoes.jpg")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 503
    assert "We couldn&#39;t save that photo." in resp.get_data(as_text=True)
    assert db.session.scalars(select(Post)).first() is None


def test_request_too_large_is_refused(client: FlaskClient, poster: User) -> None:
    resp = client.post(
        "/posts/new",
        data={**FORM, "photo": (io.BytesIO(b"\0" * (10 * 1024 * 1024)), "huge.jpg")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 413


def test_media_serves_local_photos_only(app: Flask, client: FlaskClient, poster: User) -> None:
    post = with_photo(app, poster)
    resp = client.get(f"/media/{post.photo_key}")
    assert resp.status_code == 200
    assert resp.mimetype == "image/webp"
    assert client.get("/media/posts/" + "0" * 32 + ".webp").status_code == 404
    assert client.get("/media/../instance/secret.webp").status_code == 404
    assert client.get("/media/posts/abc.png").status_code == 404
    app.extensions["photo_store"] = photos.R2Store(MagicMock(), "b", "https://p.example.com")
    assert client.get(f"/media/{post.photo_key}").status_code == 404


def test_poster_can_remove_their_photo(app: Flask, client: FlaskClient, poster: User) -> None:
    post = with_photo(app, poster)
    file = stored(app, post)
    resp = client.post(f"/posts/{post.id}/photo/delete")
    assert resp.location == f"/posts/{post.id}"
    assert post.photo_key is None
    assert not file.exists()


def test_others_cannot_remove_a_photo(app: Flask, client: FlaskClient, make_user: MakeUser) -> None:
    post = with_photo(app, make_user("maria_g"))
    login_as(client, make_user("dev_tom"))
    assert client.post(f"/posts/{post.id}/photo/delete").status_code == 404
    assert post.photo_key is not None


def test_deleting_a_post_deletes_its_photo(app: Flask, client: FlaskClient, poster: User) -> None:
    post = with_photo(app, poster)
    file = stored(app, post)
    client.post(f"/posts/{post.id}/delete")
    assert not file.exists()


def test_scrubbed_post_loses_its_photo(
    app: Flask, client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    post = with_photo(app, poster)
    file = stored(app, post)
    gift = Donation(
        donor=make_user("dev_tom"),
        amount_cents=1_000,
        method=PaymentMethod.VENMO,
        status=DonationStatus.CONFIRMED,
    )
    post.donations.append(gift)
    db.session.commit()
    client.post(f"/posts/{post.id}/delete")
    assert post.title == "Deleted post"
    assert post.photo_key is None
    assert not file.exists()


def test_deleting_an_account_deletes_its_photos(
    app: Flask, client: FlaskClient, poster: User
) -> None:
    files = [stored(app, with_photo(app, poster, title)) for title in ("One", "Two")]
    client.post("/account/delete", data={"password": PASSWORD})
    assert not any(file.exists() for file in files)


def test_photo_can_be_reported(app: Flask, client: FlaskClient, make_user: MakeUser) -> None:
    post = with_photo(app, make_user("maria_g"))
    login_as(client, make_user("dev_tom"))
    page = client.get(f"/report/post/{post.id}").get_data(as_text=True)
    assert "Inappropriate photo" in page
    client.post(f"/report/post/{post.id}", data={"reason": "photo"})
    report = db.session.scalars(select(Report)).one()
    assert report.reason is ReportReason.PHOTO


def test_admin_removes_a_reported_photo(
    app: Flask, client: FlaskClient, make_user: MakeUser
) -> None:
    post = with_photo(app, make_user("maria_g"))
    file = stored(app, post)
    reporter = make_user("dev_tom")
    db.session.add_all(
        [
            Report(reporter=reporter, post=post, reason=ReportReason.PHOTO),
            Report(reporter=reporter, post=post, reason=ReportReason.SCAM),
        ]
    )
    db.session.commit()
    login_as(client, make_user("boss", is_admin=True))
    queue = client.get("/admin").get_data(as_text=True)
    assert f'class="admin-photo" src="/media/{post.photo_key}"' in queue
    assert f'action="/admin/posts/{post.id}/remove-photo"' in queue
    resp = client.post(f"/admin/posts/{post.id}/remove-photo", follow_redirects=True)
    assert "Removed the photo from" in resp.get_data(as_text=True)
    assert post.photo_key is None
    assert not file.exists()
    open_reasons = [r.reason for r in db.session.scalars(select(Report)) if r.resolved_at is None]
    assert open_reasons == [ReportReason.SCAM]


def test_flagged_post_shows_its_photo_to_admins(
    app: Flask, client: FlaskClient, make_user: MakeUser
) -> None:
    from app.models import PostStatus

    post = with_photo(app, make_user("maria_g"))
    post.status = PostStatus.PENDING_REVIEW
    db.session.commit()
    login_as(client, make_user("boss", is_admin=True))
    assert f'src="/media/{post.photo_key}"' in client.get("/admin").get_data(as_text=True)


def test_feed_loads_the_visible_photo_first(app: Flask, client: FlaskClient, poster: User) -> None:
    shown = with_photo(app, poster, "Shown first")
    waiting = with_photo(app, poster, "Waiting underneath")
    page = client.get("/").get_data(as_text=True)
    first = shown if f'src="/media/{shown.photo_key}" alt="" decoding="sync"' in page else waiting
    other = waiting if first is shown else shown
    assert f'<link rel="preload" as="image" href="/media/{first.photo_key}"' in page
    assert f'src="/media/{first.photo_key}" alt="" decoding="sync" fetchpriority="high"' in page
    template = page[page.index('<template id="deck-under-next">') :]
    assert f'src="/media/{other.photo_key}" alt="" decoding="async">' in template


def test_removing_a_post_deletes_its_photo(
    app: Flask, client: FlaskClient, make_user: MakeUser
) -> None:
    post = with_photo(app, make_user("maria_g"))
    file, url = stored(app, post), f"/media/{post.photo_key}"
    assert client.get(url).status_code == 200
    login_as(client, make_user("boss", is_admin=True))
    client.post(f"/admin/posts/{post.id}/remove")
    assert post.photo_key is None
    assert not file.exists()
    assert client.get(url).status_code == 404


def test_a_ban_deletes_the_photos_of_removed_posts(
    app: Flask, client: FlaskClient, make_user: MakeUser
) -> None:
    owner = make_user("maria_g")
    post = with_photo(app, owner)
    file = stored(app, post)
    login_as(client, make_user("boss", is_admin=True))
    client.post(f"/admin/users/{owner.id}/ban")
    assert post.photo_key is None
    assert not file.exists()


def test_a_ban_deletes_photos_on_closed_posts_too(
    app: Flask, client: FlaskClient, make_user: MakeUser
) -> None:
    from app.models import PostStatus

    owner = make_user("maria_g")
    post = with_photo(app, owner)
    post.status = PostStatus.CLOSED
    db.session.commit()
    file = stored(app, post)
    login_as(client, make_user("boss", is_admin=True))
    client.post(f"/admin/users/{owner.id}/ban")
    assert post.status is PostStatus.REMOVED
    assert not file.exists()


def test_a_cluster_ban_deletes_the_puppets_photos(
    app: Flask, client: FlaskClient, make_user: MakeUser
) -> None:
    from tests.integration.test_farm_flags import puppets
    from tests.integration.test_leaders import give, person

    farmer = person(make_user, "farmer")
    ring = puppets(make_user, 3)
    for puppet in ring:
        give(farmer, puppet, cents=1)
    files = [stored(app, with_photo(app, puppet)) for puppet in ring]
    login_as(client, make_user("boss", is_admin=True))
    ids = ",".join(str(p.id) for p in ring)
    client.post(f"/admin/users/{farmer.id}/ban-cluster?ids={ids}")
    assert all(p.is_banned for p in ring)
    assert not any(f.exists() for f in files)


def test_only_the_new_post_form_takes_a_large_body(client: FlaskClient, poster: User) -> None:
    two_mb = io.BytesIO(b"\0" * (2 * 1024 * 1024))
    resp = client.post(
        "/posts/new",
        data={**FORM, "photo": (two_mb, "big.jpg")},
        content_type="multipart/form-data",
    )
    # Read and refused as a photo, not cut off for size.
    assert resp.status_code == 200
    assert "isn&#39;t a photo we can read" in resp.get_data(as_text=True)
    resp = client.post("/profile", data={"city": "x" * (2 * 1024 * 1024)})
    assert resp.status_code == 413


def test_large_photo_passes_csrf_on(tmp_path: Path) -> None:
    # CSRF reads the form before any view runs, so the larger limit must already be
    # in place by then (#155). Other tests run with CSRF off and can't see this.
    import os
    import re

    from werkzeug.security import generate_password_hash

    from app import create_app
    from app.models import utcnow

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "PHOTO_DIR": str(tmp_path),
            "R2_BUCKET": "",
            "MAIL_ASYNC": False,
        }
    )
    with app.app_context():
        db.create_all()
        db.session.add(
            User(
                username="maria_g",
                email="maria@example.com",
                password_hash=generate_password_hash(PASSWORD),
                email_verified_at=utcnow(),
                venmo_handle="@maria-g",
            )
        )
        db.session.commit()
    client = app.test_client()

    def token(path: str) -> str:
        found = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', client.get(path).text)
        assert found is not None
        return found.group(1)

    client.post(
        "/login",
        data={"identifier": "maria_g", "password": PASSWORD, "csrf_token": token("/login")},
    )
    noisy = io.BytesIO()
    Image.frombytes("RGB", (1200, 1200), os.urandom(1200 * 1200 * 3)).save(
        noisy, "JPEG", quality=95
    )
    assert noisy.tell() > 1024 * 1024
    noisy.seek(0)
    resp = client.post(
        "/posts/new",
        data={**FORM, "csrf_token": token("/posts/new"), "photo": (noisy, "big.jpg")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 302
    with app.app_context():
        assert db.session.scalars(select(Post)).one().photo_key
