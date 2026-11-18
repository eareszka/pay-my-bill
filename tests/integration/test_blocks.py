import logging

import pytest
from flask.testing import FlaskClient
from sqlalchemy import func, select

from app.accounts import anonymize
from app.extensions import db
from app.models import Block, Post, ReactionKind, User
from tests.conftest import MakeUser, login_as
from tests.integration.test_gifts_page import add_post


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g")


@pytest.fixture
def viewer(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def block(blocker: User, blocked: User) -> None:
    db.session.add(Block(blocker_id=blocker.id, blocked_id=blocked.id))
    db.session.commit()


def blocks() -> int:
    return db.session.scalar(select(func.count()).select_from(Block)) or 0


EMPTY = "No open posts here yet."


def test_block_from_a_profile(client: FlaskClient, poster: User, viewer: User) -> None:
    login_as(client, viewer)
    page = client.get("/u/maria_g").get_data(as_text=True)
    assert 'action="/u/maria_g/block"' in page
    assert "They aren&#39;t told." in page or "They aren't told." in page
    resp = client.post("/u/maria_g/block")
    assert resp.location == "/u/maria_g"
    assert blocks() == 1
    page = client.get("/u/maria_g").get_data(as_text=True)
    assert "You blocked maria_g." in page
    assert "Unblock maria_g</button>" in page


def test_blocking_twice_keeps_one_block(client: FlaskClient, poster: User, viewer: User) -> None:
    login_as(client, viewer)
    client.post("/u/maria_g/block")
    client.post("/u/maria_g/block")
    assert blocks() == 1


def test_block_is_silent(
    client: FlaskClient, poster: User, viewer: User, caplog: pytest.LogCaptureFixture
) -> None:
    login_as(client, viewer)
    with caplog.at_level(logging.INFO):
        client.post("/u/maria_g/block")
    assert "maria_g@example.com" not in caplog.text


def test_cannot_block_yourself_or_nobody(client: FlaskClient, viewer: User) -> None:
    login_as(client, viewer)
    assert client.post("/u/dev_tom/block").status_code == 404
    assert client.post("/u/nobody/block").status_code == 404
    assert "/block" not in client.get("/u/dev_tom").get_data(as_text=True)


def test_blocking_needs_a_login(client: FlaskClient, poster: User) -> None:
    assert client.post("/u/maria_g/block").location.startswith("/login")
    assert 'action="/u/maria_g/block"' not in client.get("/u/maria_g").get_data(as_text=True)


def test_feed_hides_someone_i_blocked(client: FlaskClient, poster: User, viewer: User) -> None:
    add_post(poster)
    block(viewer, poster)
    login_as(client, viewer)
    assert EMPTY in client.get("/feed").get_data(as_text=True)


def test_feed_hides_someone_who_blocked_me(client: FlaskClient, poster: User, viewer: User) -> None:
    add_post(poster)
    block(poster, viewer)
    login_as(client, viewer)
    assert EMPTY in client.get("/feed").get_data(as_text=True)


def test_others_still_see_the_post(
    client: FlaskClient, poster: User, viewer: User, make_user: MakeUser
) -> None:
    add_post(poster)
    block(viewer, poster)
    login_as(client, make_user("kayla"))
    assert EMPTY not in client.get("/feed").get_data(as_text=True)


@pytest.mark.parametrize("direction", ["i_blocked", "they_blocked"])
def test_cannot_open_chip_in_or_react_across_a_block(
    client: FlaskClient,
    poster: User,
    viewer: User,
    direction: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    post = add_post(poster)
    post.update_body = "It went well, thank you all so much."
    db.session.commit()
    block(viewer, poster) if direction == "i_blocked" else block(poster, viewer)
    monkeypatch.setattr("app.stripe_pay.enabled", lambda: True)
    login_as(client, viewer)
    assert client.get(f"/posts/{post.id}").status_code == 404
    gift = client.post(f"/posts/{post.id}/gifts", data={"amount": "20", "method": "venmo"})
    assert gift.status_code == 404
    assert client.post(f"/posts/{post.id}/card", data={"amount": "20"}).status_code == 404
    kudos = client.post(f"/posts/{post.id}/react/{ReactionKind.KUDOS.value}", data={"on": "1"})
    assert kudos.status_code == 404
    assert post.donations == [] and post.reactions == []


def test_settings_lists_and_unblocks(client: FlaskClient, poster: User, viewer: User) -> None:
    post = add_post(poster)
    block(viewer, poster)
    login_as(client, viewer)
    page = client.get("/profile").get_data(as_text=True)
    assert "<span>maria_g</span>" in page
    resp = client.post("/u/maria_g/unblock", data={"next": "/profile#blocked"})
    assert resp.location == "/profile#blocked"
    assert blocks() == 0
    assert client.get(f"/posts/{post.id}").status_code == 200
    assert "You haven&#39;t blocked anyone." in client.get("/profile").get_data(
        as_text=True
    ) or "You haven't blocked anyone." in client.get("/profile").get_data(as_text=True)


def test_unblock_only_lifts_my_own_block(client: FlaskClient, poster: User, viewer: User) -> None:
    block(poster, viewer)
    login_as(client, viewer)
    resp = client.post("/u/maria_g/unblock")
    assert resp.location == "/u/maria_g"
    assert blocks() == 1


def test_deleting_an_account_drops_its_blocks(poster: User, viewer: User) -> None:
    block(viewer, poster)
    block(poster, viewer)
    anonymize(viewer)
    db.session.commit()
    assert blocks() == 0


def test_feed_query_outside_a_request_hides_nothing(poster: User, viewer: User) -> None:
    from app.top_spot import top_post

    post = add_post(poster)
    block(viewer, poster)
    assert db.session.get(Post, post.id) is not None
    assert top_post() in (None, post)


def test_block_from_a_post(client: FlaskClient, poster: User, viewer: User) -> None:
    post = add_post(poster)
    login_as(client, viewer)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert 'action="/u/maria_g/block"' in page
    client.post("/u/maria_g/block")
    assert client.get(f"/posts/{post.id}").status_code == 404
