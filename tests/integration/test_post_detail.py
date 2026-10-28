import pytest
from flask.testing import FlaskClient

from app.extensions import db
from app.models import Post, PostKind, PostStatus, User
from tests.conftest import MakeUser, login_as


def add_post(owner: User, status: PostStatus = PostStatus.OPEN) -> Post:
    post = Post(
        user=owner,
        kind=PostKind.NEED,
        title="Electric bill help",
        body="AC broke in August.\nThe bill came in high.",
        goal_cents=25_000,
        status=status,
    )
    db.session.add(post)
    db.session.commit()
    return post


@pytest.fixture
def owner(make_user: MakeUser) -> User:
    return make_user(
        "maria_g", city="Tampa", state="FL", cashapp_handle="$mariag", paypal_handle="MariaG"
    )


def test_open_post_shows_story_poster_goal_progress_and_handles(
    client: FlaskClient, owner: User
) -> None:
    post = add_post(owner)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "<h1>Electric bill help</h1>" in page
    assert "AC broke in August.\nThe bill came in high." in page
    assert 'href="/u/maria_g">maria_g</a> · Tampa, FL' in page
    assert "<strong>$0</strong> raised of $250" in page
    assert 'aria-valuenow="0"' in page
    assert "Chip in" in page
    assert "$mariag" in page
    assert "paypal.me/MariaG" in page


def test_body_is_escaped(client: FlaskClient, owner: User) -> None:
    post = add_post(owner)
    post.body = "<script>alert(1)</script> please help"
    db.session.commit()
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


@pytest.mark.parametrize("status", [PostStatus.FUNDED, PostStatus.CLOSED])
def test_finished_posts_are_public_without_handles(
    client: FlaskClient, owner: User, status: PostStatus
) -> None:
    post = add_post(owner, status)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f"This post is {status.value}" in page
    assert "Chip in" not in page


@pytest.mark.parametrize("status", [PostStatus.PENDING_REVIEW, PostStatus.REMOVED])
@pytest.mark.parametrize(
    ("viewer", "expected"), [(None, 404), ("other", 404), ("owner", 200), ("admin", 200)]
)
def test_hidden_post_visibility(
    client: FlaskClient,
    make_user: MakeUser,
    owner: User,
    status: PostStatus,
    viewer: str | None,
    expected: int,
) -> None:
    post = add_post(owner, status)
    if viewer == "owner":
        login_as(client, owner)
    elif viewer == "other":
        login_as(client, make_user("bob"))
    elif viewer == "admin":
        login_as(client, make_user("root", is_admin=True))
    resp = client.get(f"/posts/{post.id}")
    assert resp.status_code == expected
    if expected == 200:
        assert b"Only you and moderators can see" in resp.data
        assert b"Chip in" not in resp.data


def test_missing_post_404(client: FlaskClient) -> None:
    assert client.get("/posts/999").status_code == 404


def test_feed_card_links_to_detail(client: FlaskClient, owner: User) -> None:
    post = add_post(owner)
    assert f'href="/posts/{post.id}">Electric bill help</a>'.encode() in client.get("/").data


def test_new_post_redirects_to_detail(client: FlaskClient, owner: User) -> None:
    login_as(client, owner)
    resp = client.post(
        "/posts/new",
        data={
            "kind": "want",
            "title": "Concert tickets",
            "body": "My favorite band is touring.",
            "goal": "80",
            "accept_rules": "y",
        },
    )
    post = db.session.scalars(db.select(Post)).one()
    assert resp.location == f"/posts/{post.id}"
