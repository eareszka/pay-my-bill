from datetime import timedelta

import pytest
from flask.testing import FlaskClient

from app.extensions import db
from app.models import Post, PostKind, PostStatus, User, utcnow
from app.routes.main import PAGE_SIZE
from tests.conftest import MakeUser


def add_post(
    user: User,
    title: str,
    kind: PostKind = PostKind.NEED,
    status: PostStatus = PostStatus.OPEN,
    hours_ago: int = 0,
) -> Post:
    post = Post(
        user=user,
        kind=kind,
        title=title,
        body="A short story about it.",
        goal_cents=12_050,
        status=status,
        created_at=utcnow() - timedelta(hours=hours_ago),
    )
    db.session.add(post)
    db.session.commit()
    return post


def test_feed_shows_open_posts_newest_first(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user(city="Tampa", state="FL")
    add_post(user, "Older need", hours_ago=5)
    add_post(user, "Newest want", kind=PostKind.WANT, hours_ago=1)
    page = client.get("/").get_data(as_text=True)
    assert page.index("Newest want") < page.index("Older need")
    assert "$0</strong> of $120.50" in page
    assert 'class="chip chip-want">Want<' in page
    assert 'class="chip chip-need">Need<' in page
    assert "alice</a> · Tampa, FL" in page
    assert 'aria-valuenow="0"' in page


@pytest.mark.parametrize(
    "status", [PostStatus.PENDING_REVIEW, PostStatus.REMOVED, PostStatus.FUNDED, PostStatus.CLOSED]
)
def test_feed_hides_non_open_posts(
    client: FlaskClient, make_user: MakeUser, status: PostStatus
) -> None:
    add_post(make_user(), "Hidden post", status=status)
    page = client.get("/").get_data(as_text=True)
    assert "Hidden post" not in page
    assert "No open posts here yet." in page


@pytest.mark.parametrize(
    ("kind", "shown", "hidden"),
    [("want", "A want", "A need"), ("need", "A need", "A want")],
)
def test_feed_filters_by_kind(
    client: FlaskClient, make_user: MakeUser, kind: str, shown: str, hidden: str
) -> None:
    user = make_user()
    add_post(user, "A want", kind=PostKind.WANT)
    add_post(user, "A need", kind=PostKind.NEED)
    page = client.get(f"/?kind={kind}").get_data(as_text=True)
    assert shown in page
    assert hidden not in page
    assert f'href="/?kind={kind}" aria-current="page"' in page


def test_unknown_kind_shows_all(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user()
    add_post(user, "A want", kind=PostKind.WANT)
    add_post(user, "A need")
    page = client.get("/?kind=loan").get_data(as_text=True)
    assert "A want" in page
    assert "A need" in page


def test_feed_paginates(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user()
    for i in range(PAGE_SIZE + 1):
        add_post(user, f"Post number {i:02d}", hours_ago=i)
    first = client.get("/").get_data(as_text=True)
    assert "Post number 00" in first
    assert f"Post number {PAGE_SIZE:02d}" not in first
    assert "Older</a>" in first
    assert "Newer</a>" not in first
    second = client.get("/?page=2").get_data(as_text=True)
    assert f"Post number {PAGE_SIZE:02d}" in second
    assert "Newer</a>" in second
    assert "Older</a>" not in second
    for bad in ("0", "-3", "abc", "99999999999999999999"):
        assert client.get(f"/?page={bad}").status_code == 200


def test_page_past_end_links_back(client: FlaskClient, make_user: MakeUser) -> None:
    add_post(make_user(), "Only post")
    page = client.get("/?page=5&kind=need").get_data(as_text=True)
    assert "No more posts." in page
    assert 'href="/?kind=need&amp;page=4">Newer</a>' in page


def test_region_hidden_without_city(client: FlaskClient, make_user: MakeUser) -> None:
    add_post(make_user(state="FL"), "Post")
    page = client.get("/").get_data(as_text=True)
    assert "None" not in page
    assert 'href="/u/alice">alice</a></span>' in page


def test_empty_state_for_logged_out_visitor(client: FlaskClient) -> None:
    page = client.get("/").get_data(as_text=True)
    assert "No open posts here yet." in page
    assert "to post one" in page


def test_layout_has_mobile_viewport(client: FlaskClient) -> None:
    assert b'name="viewport" content="width=device-width, initial-scale=1"' in client.get("/").data
