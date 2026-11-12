from flask import Flask
from flask.testing import FlaskClient

from app.door_photos import DOOR_PHOTOS, door_photos
from app.extensions import db
from app.models import Post, PostKind, PostStatus, Report, ReportReason, User, utcnow
from tests.conftest import MakeUser


def add_posts(user: User, count: int, status: PostStatus = PostStatus.OPEN, tag: str = "") -> None:
    for n in range(count):
        db.session.add(
            Post(
                user=user,
                kind=PostKind.NEED,
                title=f"Ask {n}",
                body="Short on rent this month.",
                goal_cents=10_000,
                status=status,
                photo_key=f"posts/{tag}{n:032x}",
            )
        )
    db.session.commit()


def test_a_door_with_enough_photos_shows_the_newest(app: Flask, make_user: MakeUser) -> None:
    add_posts(make_user("maria_g"), DOOR_PHOTOS + 2)
    keys = door_photos(funded=False)
    assert len(keys) == DOOR_PHOTOS
    assert keys[0].endswith(f"{DOOR_PHOTOS + 1:032x}")


def test_a_door_with_too_few_photos_stays_plain(app: Flask, make_user: MakeUser) -> None:
    add_posts(make_user("maria_g"), DOOR_PHOTOS - 1)
    assert door_photos(funded=False) == []


def test_the_ask_door_uses_funded_posts_only(app: Flask, make_user: MakeUser) -> None:
    user = make_user("maria_g")
    add_posts(user, DOOR_PHOTOS)
    assert door_photos(funded=True) == []
    add_posts(user, DOOR_PHOTOS, PostStatus.FUNDED, tag="f")
    assert len(door_photos(funded=True)) == DOOR_PHOTOS


def test_unsafe_posts_never_reach_the_doors(app: Flask, make_user: MakeUser) -> None:
    good = make_user("maria_g")
    add_posts(good, DOOR_PHOTOS - 1)
    add_posts(make_user("new_k", verified=False), 1, tag="u")
    add_posts(make_user("gone_b", banned_at=utcnow()), 1, tag="b")
    add_posts(good, 1, tag="r")
    reported = db.session.query(Post).filter(Post.photo_key.endswith(f"r{0:032x}")).one()
    db.session.add(Report(reporter=good, post=reported, reason=ReportReason.PHOTO))
    db.session.add(Post(user=good, kind=PostKind.NEED, title="No photo", body="y", goal_cents=100))
    db.session.commit()
    removed = make_user("del_q")
    removed.email = "del_q@deleted.invalid"
    add_posts(removed, 1, tag="d")
    assert door_photos(funded=False) == []


def test_the_doors_show_their_photos(client: FlaskClient, make_user: MakeUser) -> None:
    page = client.get("/").get_data(as_text=True)
    assert "home-mosaic" not in page
    user = make_user("maria_g")
    add_posts(user, DOOR_PHOTOS)
    page = client.get("/").get_data(as_text=True)
    assert page.count('<span class="home-mosaic" aria-hidden="true">') == 1
    assert page.count('alt="" decoding="async"') == DOOR_PHOTOS
    assert page.count('loading="lazy"') == DOOR_PHOTOS - 3
    assert "These asks got there." not in page
    add_posts(user, DOOR_PHOTOS, PostStatus.FUNDED, tag="f")
    page = client.get("/").get_data(as_text=True)
    assert page.count('<span class="home-mosaic" aria-hidden="true">') == 2
    assert "These asks got there." in page


def test_a_reported_account_keeps_all_its_photos_off(app: Flask, make_user: MakeUser) -> None:
    poster = make_user("maria_g")
    add_posts(poster, DOOR_PHOTOS)
    reporter = make_user("sam_k")
    db.session.add(Report(reporter=reporter, user_id=poster.id, reason=ReportReason.SCAM))
    db.session.commit()
    assert door_photos(funded=False) == []


def test_a_report_on_another_post_keeps_the_account_off(app: Flask, make_user: MakeUser) -> None:
    poster = make_user("maria_g")
    reporter = make_user("sam_k")
    add_posts(poster, DOOR_PHOTOS)
    add_posts(poster, 1, PostStatus.CLOSED, tag="c")
    assert door_photos(funded=False) != []
    old = db.session.query(Post).filter(Post.status == PostStatus.CLOSED).one()
    db.session.add(Report(reporter=reporter, post=old, reason=ReportReason.SCAM))
    db.session.commit()
    assert door_photos(funded=False) == []


def test_story_steps_carry_their_doors_photos(client: FlaskClient, make_user: MakeUser) -> None:
    assert "home-mosaic" not in client.get("/how/help").get_data(as_text=True)
    user = make_user("maria_g")
    add_posts(user, DOOR_PHOTOS)
    keys = door_photos(funded=False)
    first = client.get("/how/help").get_data(as_text=True)
    second = client.get("/how/help/2").get_data(as_text=True)
    third = client.get("/how/help/3").get_data(as_text=True)
    for page in (first, second, third):
        assert page.count('alt="" decoding="async"') == 3
    assert all(key in first for key in keys[:3]) and keys[3] not in first
    assert all(key in second for key in keys[3:]) and keys[0] not in second
    assert all(key in third for key in keys[:3])
    assert "home-mosaic" not in client.get("/how/ask").get_data(as_text=True)
    add_posts(user, DOOR_PHOTOS, PostStatus.FUNDED, tag="f")
    assert client.get("/how/ask/3").get_data(as_text=True).count('alt="" decoding="async"') == 3
