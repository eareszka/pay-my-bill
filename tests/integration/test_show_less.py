import re
from datetime import timedelta

import pytest
from flask.testing import FlaskClient
from sqlalchemy import select

from app.accounts import anonymize
from app.extensions import db
from app.models import Post, PostCategory, PostKind, PostStatus, User, utcnow
from app.show_less import COOKIE, parse
from tests.conftest import PASSWORD, MakeUser, login_as
from tests.integration.test_create_post import FORM
from tests.integration.test_signup import FORM as SIGNUP


@pytest.fixture(autouse=True)
def no_top_pick(monkeypatch: pytest.MonkeyPatch) -> None:
    # The follow-through pick (ADR 0013) has its own tests; here the stack is plain.
    monkeypatch.setattr("app.routes.main.top_post", lambda kind: None)


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g")


@pytest.fixture
def viewer(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def add_post(owner: User, title: str, category: PostCategory, days_old: int = 0) -> Post:
    post = Post(
        user=owner,
        kind=PostKind.NEED,
        category=category,
        title=title,
        body="Short.",
        goal_cents=10_000,
        created_at=utcnow() - timedelta(days=days_old),
    )
    db.session.add(post)
    db.session.commit()
    return post


@pytest.fixture
def stack(poster: User) -> tuple[Post, Post]:
    # Without a choice, the newer rent post comes first.
    return add_post(poster, "Bills", PostCategory.BILLS, 2), add_post(
        poster, "Rent", PostCategory.RENT
    )


def shown(client: FlaskClient, query: str = "") -> str:
    page = client.get(f"/feed{query}").get_data(as_text=True)
    return re.findall(r'<h2 class="card-title">.*?</span>(.*?)</a>', page)[0]


def show_less(client: FlaskClient, category: str = "rent", next_: str = "/feed?undo=rent"):  # type: ignore[no-untyped-def]
    return client.post(f"/feed/less/{category}", data={"next": next_})


def test_new_posts_need_a_category(client: FlaskClient, poster: User) -> None:
    login_as(client, poster)
    page = client.get("/posts/new").get_data(as_text=True)
    assert 'name="category" value=""' not in page
    assert 'name="category" value="fun" required> 🎮 Fun and games' in page
    resp = client.post("/posts/new", data={**FORM, "category": ""})
    assert "Choose a category." in resp.get_data(as_text=True)
    client.post("/posts/new", data={**FORM, "category": "loans"})
    assert poster.posts == []
    client.post("/posts/new", data={**FORM, "category": "health"})
    assert poster.posts[0].category is PostCategory.HEALTH


def test_posts_without_a_category_are_other(poster: User) -> None:
    post = Post(user=poster, kind=PostKind.WANT, title="Game", body="A new game.", goal_cents=5_000)
    db.session.add(post)
    db.session.commit()
    assert post.category is PostCategory.OTHER


def test_poster_can_change_the_category(client: FlaskClient, poster: User) -> None:
    post = add_post(poster, "Rent", PostCategory.RENT)
    login_as(client, poster)
    data = {
        "kind": "need",
        "category": "bills",
        "title": "Rent",
        "body": "Short on rent this month.",
        "goal": "100",
    }
    client.post(f"/posts/{post.id}/edit", data=data)
    assert post.category is PostCategory.BILLS


def test_show_less_moves_a_category_later(
    client: FlaskClient, viewer: User, stack: tuple[Post, Post]
) -> None:
    login_as(client, viewer)
    assert shown(client) == "Rent"
    assert "Show less Rent and housing</button>" in client.get("/feed").get_data(as_text=True)
    resp = show_less(client)
    assert resp.location == "/feed?undo=rent"
    assert viewer.show_less == "rent"
    assert shown(client) == "Bills"
    assert shown(client, "?n=2") == "Rent"


def test_undo_right_away(client: FlaskClient, viewer: User, stack: tuple[Post, Post]) -> None:
    login_as(client, viewer)
    show_less(client)
    page = client.get("/feed?undo=rent").get_data(as_text=True)
    assert "You&#39;ll see Rent and housing posts later" in page or (
        "You'll see Rent and housing posts later" in page
    )
    assert 'action="/feed/more/rent"' in page
    assert "Show less Bills and utilities</button>" in page
    client.post("/feed/more/rent", data={"next": "/feed"})
    assert viewer.show_less is None
    assert shown(client) == "Rent"


def test_undo_notice_needs_a_real_choice(
    client: FlaskClient, viewer: User, stack: tuple[Post, Post]
) -> None:
    login_as(client, viewer)
    for query in ("?undo=rent", "?undo=nope"):
        assert "show-less-note" not in client.get(f"/feed{query}").get_data(as_text=True)


def test_first_ticket_stays_the_follow_through_pick(
    client: FlaskClient, viewer: User, stack: tuple[Post, Post], monkeypatch: pytest.MonkeyPatch
) -> None:
    bills, rent = stack
    monkeypatch.setattr("app.routes.main.top_post", lambda kind: rent)
    login_as(client, viewer)
    show_less(client)
    assert shown(client) == "Rent"
    assert shown(client, "?n=2") == "Bills"


def test_never_hides_a_post(client: FlaskClient, viewer: User, stack: tuple[Post, Post]) -> None:
    login_as(client, viewer)
    show_less(client, "rent")
    show_less(client, "bills")
    assert "1 of 2" in client.get("/feed").get_data(as_text=True)
    assert {shown(client), shown(client, "?n=2")} == {"Rent", "Bills"}


def test_unknown_category_is_404(client: FlaskClient, viewer: User) -> None:
    login_as(client, viewer)
    assert show_less(client, "loans").status_code == 404
    assert client.post("/feed/more/loans").status_code == 404


def test_next_must_stay_on_the_site(client: FlaskClient, viewer: User) -> None:
    login_as(client, viewer)
    assert show_less(client, next_="https://evil.example/").location == "/feed"


def test_logged_out_choice_lives_in_a_cookie(client: FlaskClient, stack: tuple[Post, Post]) -> None:
    resp = show_less(client)
    assert f"{COOKIE}=rent" in resp.headers["Set-Cookie"]
    assert "HttpOnly" in resp.headers["Set-Cookie"]
    assert shown(client) == "Bills"
    client.post("/feed/more/rent", data={"next": "/feed"})
    assert shown(client) == "Rent"


def test_a_tampered_cookie_is_ignored(client: FlaskClient, stack: tuple[Post, Post]) -> None:
    client.set_cookie(COOKIE, "loans,,<script>")
    assert shown(client) == "Rent"
    assert parse("rent,loans,RENT") == {PostCategory.RENT}


def test_cookie_joins_the_account_at_log_in(client: FlaskClient, viewer: User) -> None:
    viewer.show_less = "fun"
    db.session.commit()
    client.set_cookie(COOKIE, "rent,bogus")
    resp = client.post("/login", data={"identifier": "dev_tom", "password": PASSWORD})
    assert resp.status_code == 302
    assert viewer.show_less == "fun,rent"
    assert f"{COOKIE}=;" in resp.headers["Set-Cookie"]


def test_log_in_without_the_cookie_keeps_the_account_choice(
    client: FlaskClient, viewer: User
) -> None:
    viewer.show_less = "fun"
    db.session.commit()
    resp = client.post("/login", data={"identifier": "dev_tom", "password": PASSWORD})
    assert COOKIE not in resp.headers.get("Set-Cookie", "")
    assert viewer.show_less == "fun"


def test_undo_later_from_the_profile(client: FlaskClient, viewer: User) -> None:
    viewer.show_less = "rent,fun"
    db.session.commit()
    login_as(client, viewer)
    page = client.get("/u/dev_tom").get_data(as_text=True)
    assert "Showing you less" in page
    assert page.index("Rent and housing</span>") < page.index("Fun and games</span>")
    assert 'action="/feed/more/fun"' in page
    resp = client.post("/feed/more/fun", data={"next": "/u/dev_tom"})
    assert resp.location == "/u/dev_tom"
    assert viewer.show_less == "rent"


def test_visitors_never_see_the_choice(client: FlaskClient, viewer: User) -> None:
    viewer.show_less = "rent"
    db.session.commit()
    assert "Showing you less" not in client.get("/u/dev_tom").get_data(as_text=True)


def test_cookie_joins_the_account_at_sign_up(client: FlaskClient) -> None:
    client.set_cookie(COOKIE, "rent")
    resp = client.post("/signup", data=SIGNUP)
    assert resp.status_code == 302
    user = db.session.scalar(select(User).where(User.username == "new_user"))
    assert user is not None and user.show_less == "rent"
    assert f"{COOKIE}=;" in resp.headers["Set-Cookie"]


def test_no_show_less_on_the_follow_through_pick(
    client: FlaskClient, viewer: User, stack: tuple[Post, Post], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.routes.main.top_post", lambda kind: stack[1])
    login_as(client, viewer)
    assert 'class="show-less"' not in client.get("/feed").get_data(as_text=True)
    assert 'class="show-less"' in client.get("/feed?n=2").get_data(as_text=True)


def test_moving_a_post_to_another_category_is_not_an_edit(
    client: FlaskClient, poster: User
) -> None:
    post = add_post(poster, "Launch day bus fare", PostCategory.RENT)
    post.body = "Bus fare to my first shift."
    db.session.commit()
    login_as(client, poster)
    data = {
        "kind": "need",
        "category": "transport",
        "title": "Launch day bus fare",
        "body": "Bus fare to my first shift.",
        "goal": "100",
    }
    client.post(f"/posts/{post.id}/edit", data=data)
    assert post.category is PostCategory.TRANSPORT
    assert post.edited_at is None
    assert post.status is PostStatus.OPEN


def test_deleting_an_account_clears_the_choice(viewer: User) -> None:
    viewer.show_less = "rent"
    anonymize(viewer)
    db.session.commit()
    assert viewer.show_less is None


def test_privacy_names_the_show_less_cookie(client: FlaskClient) -> None:
    page = client.get("/privacy").get_data(as_text=True)
    assert "We use two cookies" in page
    assert "The only cookie" not in page
