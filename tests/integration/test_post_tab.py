from flask.testing import FlaskClient

from app.extensions import db
from app.models import MAX_OPEN_POSTS, Post, PostKind, PostStatus
from tests.conftest import MakeUser, login_as


def test_post_tab_needs_login(client: FlaskClient) -> None:
    assert client.get("/posts/").location == "/login?next=/posts/"


def test_post_tab_lists_your_posts_with_create_at_top(
    client: FlaskClient, make_user: MakeUser
) -> None:
    user = make_user(venmo_handle="@alice-v")
    other = make_user(username="bob")
    for owner, title in ((user, "My rent"), (other, "Not mine")):
        db.session.add(
            Post(user=owner, kind=PostKind.NEED, title=title, body="x" * 20, goal_cents=5000)
        )
    db.session.commit()
    login_as(client, user)
    page = client.get("/posts/").get_data(as_text=True)
    assert page.index("Create new post") < page.index("My rent")
    assert 'href="/posts/new"' in page
    assert "Not mine" not in page
    assert 'href="/posts/" aria-current="page"' in page
    assert 'href="/posts/" aria-current="page"' in client.get("/posts/new").get_data(as_text=True)


def test_post_tab_at_limit_says_why(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user(venmo_handle="@alice-v")
    for n in range(MAX_OPEN_POSTS):
        db.session.add(
            Post(
                user=user,
                kind=PostKind.WANT,
                title=f"Post {n}",
                body="x" * 20,
                goal_cents=5000,
                status=PostStatus.OPEN,
            )
        )
    db.session.commit()
    login_as(client, user)
    page = client.get("/posts/").get_data(as_text=True)
    assert "Create new post" not in page
    assert f"You have {MAX_OPEN_POSTS} open posts" in page
