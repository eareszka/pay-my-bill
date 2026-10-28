import pytest
from flask.testing import FlaskClient
from sqlalchemy import select

from app.extensions import db
from app.models import MAX_GOAL_CENTS, MAX_OPEN_POSTS, Post, PostKind, PostStatus, User, utcnow
from tests.conftest import MakeUser, login_as

FORM = {
    "kind": "need",
    "title": "Car battery died",
    "body": "Need a new battery to get to work this week.",
    "goal": "$120",
    "accept_rules": "y",
}


@pytest.fixture
def poster(client: FlaskClient, make_user: MakeUser) -> User:
    user = make_user(venmo_handle="@alice-v")
    login_as(client, user)
    return user


def posts() -> list[Post]:
    return list(db.session.scalars(select(Post)))


def test_requires_login(client: FlaskClient) -> None:
    assert client.get("/posts/new").location == "/login?next=/posts/new"


def test_unverified_user_prompted_to_verify(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user(verified=False, venmo_handle="@alice-v"))
    assert client.get("/posts/new").location == "/verify/pending"
    assert client.post("/posts/new", data=FORM).location == "/verify/pending"
    assert posts() == []


def test_no_payment_handle_sent_to_profile(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user())
    resp = client.post("/posts/new", data=FORM)
    assert resp.location == "/profile"
    assert posts() == []


def test_form_renders_with_rules_checkbox(client: FlaskClient, poster: User) -> None:
    page = client.get("/posts/new").get_data(as_text=True)
    assert "Ask for a hand" in page
    assert "Community Rules" in page
    assert 'name="accept_rules"' in page


def test_rules_checkbox_hidden_once_accepted(client: FlaskClient, poster: User) -> None:
    poster.rules_accepted_at = utcnow()
    db.session.commit()
    page = client.get("/posts/new").get_data(as_text=True)
    assert 'name="accept_rules"' not in page
    client.post("/posts/new", data={**FORM, "accept_rules": ""})
    assert len(posts()) == 1


def test_create_open_post(client: FlaskClient, poster: User) -> None:
    resp = client.post("/posts/new", data=FORM, follow_redirects=True)
    assert b"Your post is live." in resp.data
    (post,) = posts()
    assert (post.kind, post.status, post.goal_cents) == (PostKind.NEED, PostStatus.OPEN, 12_000)
    assert post.user_id == poster.id
    assert poster.rules_accepted_at is not None


def test_first_post_requires_rules(client: FlaskClient, poster: User) -> None:
    resp = client.post("/posts/new", data={**FORM, "accept_rules": ""})
    assert b"You need to agree to the Community Rules" in resp.data
    assert posts() == []
    assert poster.rules_accepted_at is None


def test_goal_at_cap_allowed(client: FlaskClient, poster: User) -> None:
    client.post("/posts/new", data={**FORM, "goal": "1,000.00"})
    assert posts()[0].goal_cents == MAX_GOAL_CENTS


@pytest.mark.parametrize(
    ("goal", "message"),
    [
        ("1000.01", b"Goals are capped at $1,000."),
        ("$2,500", b"Goals are capped at $1,000."),
        ("0", b"more than $0"),
        ("lots", b"Enter a dollar amount"),
    ],
)
def test_bad_goal_rejected(client: FlaskClient, poster: User, goal: str, message: bytes) -> None:
    resp = client.post("/posts/new", data={**FORM, "goal": goal})
    assert message in resp.data
    assert posts() == []


@pytest.mark.parametrize(
    "overrides",
    [{"kind": "loan"}, {"kind": ""}, {"title": "  "}, {"body": "too short"}, {"title": "x" * 81}],
)
def test_invalid_fields_rejected(
    client: FlaskClient, poster: User, overrides: dict[str, str]
) -> None:
    assert client.post("/posts/new", data={**FORM, **overrides}).status_code == 200
    assert posts() == []


def test_third_open_post_rejected(client: FlaskClient, poster: User) -> None:
    client.post("/posts/new", data=FORM)
    client.post("/posts/new", data={**FORM, "title": "Help my startup"})
    assert [p.status for p in posts()] == [PostStatus.OPEN, PostStatus.PENDING_REVIEW]
    resp = client.post("/posts/new", data={**FORM, "title": "Third one"})
    assert resp.status_code == 409
    assert b"You already have 2 open posts" in resp.data
    assert len(posts()) == 2
    assert b"You already have 2 open posts" in client.get("/posts/new").data


def test_closed_posts_do_not_count(client: FlaskClient, poster: User) -> None:
    client.post("/posts/new", data=FORM)
    client.post("/posts/new", data=FORM)
    for post in posts():
        post.status = PostStatus.FUNDED
    db.session.commit()
    client.post("/posts/new", data=FORM)
    assert len(posts()) == 3


def test_fundraising_post_goes_to_review(client: FlaskClient, poster: User) -> None:
    resp = client.post(
        "/posts/new",
        data={**FORM, "title": "Small shop", "body": "Need seed money for my LLC inventory."},
        follow_redirects=True,
    )
    assert b"after a quick review" in resp.data
    assert posts()[0].status is PostStatus.PENDING_REVIEW


def test_rules_page(client: FlaskClient) -> None:
    page = client.get("/rules").get_data(as_text=True)
    assert "No business fundraising." in page


def test_rules_and_field_errors_reported_together(client: FlaskClient, poster: User) -> None:
    resp = client.post("/posts/new", data={**FORM, "accept_rules": "", "goal": "5000"})
    assert b"You need to agree to the Community Rules" in resp.data
    assert b"Goals are capped at $1,000." in resp.data


def test_limit_text_uses_constant(client: FlaskClient, poster: User) -> None:
    for _ in range(MAX_OPEN_POSTS):
        client.post("/posts/new", data=FORM)
    assert f"You already have {MAX_OPEN_POSTS} open posts".encode() in client.get("/posts/new").data
