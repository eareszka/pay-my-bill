from flask.testing import FlaskClient

from app.extensions import db
from app.models import Post, PostCategory, PostKind, PostStatus, User
from tests.conftest import MakeUser, login_as


def make_post(user: User, status: PostStatus = PostStatus.OPEN) -> Post:
    post = Post(
        user=user,
        kind=PostKind.NEED,
        category=PostCategory.BILLS,
        title="Power bill",
        body="The power bill came in high this month.",
        goal_cents=8_000,
        status=status,
    )
    db.session.add(post)
    db.session.commit()
    return post


def share_link(post: Post) -> str:
    # The bare post address from APP_URL: no sharer, no token, no query string.
    return f'data-share="http://localhost/posts/{post.id}" data-share-title="Power bill"'


def test_feed_and_post_page_share_the_bare_link(client: FlaskClient, make_user: MakeUser) -> None:
    post = make_post(make_user("maria_g"))
    login_as(client, make_user("dev_tom"))
    for path in ("/feed", f"/posts/{post.id}"):
        page = client.get(path).get_data(as_text=True)
        assert share_link(post) in page, path
        assert "dev_tom" not in page.split("data-share=")[1].split(">")[0]
        assert "js/share.js" in page


def test_a_post_waiting_for_review_has_no_share(client: FlaskClient, make_user: MakeUser) -> None:
    poster = make_user("maria_g")
    post = make_post(poster, PostStatus.PENDING_REVIEW)
    login_as(client, poster)
    assert "data-share" not in client.get(f"/posts/{post.id}").get_data(as_text=True)
