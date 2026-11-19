from flask.testing import FlaskClient

from app.extensions import db
from app.models import MAX_OPEN_POSTS, Post, PostKind, PostStatus
from tests.conftest import MakeUser, login_as


def add_post(user_id: int, title: str, status: PostStatus = PostStatus.OPEN) -> None:
    db.session.add(
        Post(
            user_id=user_id,
            kind=PostKind.NEED,
            title=title,
            body="A story long enough.",
            goal_cents=5000,
            status=status,
        )
    )
    db.session.commit()


def test_requires_login(client: FlaskClient) -> None:
    assert client.get("/posts/").location == "/login?next=/posts/"


def test_lists_your_posts_under_create_new(client: FlaskClient, make_user: MakeUser) -> None:
    me, other = make_user("me"), make_user("other")
    add_post(me.id, "Mine in review", PostStatus.PENDING_REVIEW)
    add_post(other.id, "Not mine")
    login_as(client, me)
    page = client.get("/posts/").get_data(as_text=True)
    assert page.index("Create new post") < page.index("Mine in review")
    assert 'href="/posts/new"' in page
    assert "Not mine" not in page
    assert '<a href="/posts/" aria-current="page"' in page


def test_at_the_limit_says_why(client: FlaskClient, make_user: MakeUser) -> None:
    me = make_user()
    for n in range(MAX_OPEN_POSTS):
        add_post(me.id, f"Open {n}")
    login_as(client, me)
    page = client.get("/posts/").get_data(as_text=True)
    assert "Create new post" not in page
    assert f"You have {MAX_OPEN_POSTS} open posts" in page


def test_tab_stays_current_on_the_questions(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user(venmo_handle="@me"))
    page = client.get("/posts/new").get_data(as_text=True)
    assert '<a href="/posts/" aria-current="page"' in page
