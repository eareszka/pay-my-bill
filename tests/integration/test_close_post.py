from datetime import timedelta

import pytest
from flask.testing import FlaskClient

from app.accounts import delete_post
from app.extensions import db
from app.models import (
    MAX_OPEN_POSTS,
    POST_OPEN_DAYS,
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    PostKind,
    PostStatus,
    User,
    as_utc,
    utcnow,
)
from tests.conftest import MakeUser, login_as


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g", rules_accepted_at=utcnow())


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def add_post(owner: User, age_days: float = 0, goal_cents: int = 9_000) -> Post:
    post = Post(
        user=owner,
        kind=PostKind.NEED,
        title="Short on rent",
        body="Hours got cut.",
        goal_cents=goal_cents,
        created_at=utcnow() - timedelta(days=age_days),
    )
    db.session.add(post)
    db.session.commit()
    return post


def add_gift(post: Post, donor: User, amount_cents: int = 2_000) -> Donation:
    gift = Donation(post=post, donor=donor, amount_cents=amount_cents, method=PaymentMethod.VENMO)
    db.session.add(gift)
    db.session.commit()
    return gift


def test_owner_gets_an_inline_confirm_before_closing(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f'href="/posts/{post.id}?close=1#delete">Close post</a>' in page
    assert "Yes, close it" not in page
    page = client.get(f"/posts/{post.id}?close=1").get_data(as_text=True)
    assert "Close this post?" in page
    assert f'action="/posts/{post.id}/close"' in page


def test_closing_takes_the_post_off_the_feed(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    login_as(client, poster)
    response = client.post(f"/posts/{post.id}/close", follow_redirects=True)
    page = response.get_data(as_text=True)
    assert "Your post is closed." in page
    assert "This post is closed." in page
    assert "Close post" not in page
    assert post.status is PostStatus.CLOSED
    assert post.closed_at is not None
    assert "Short on rent" not in client.get("/feed").get_data(as_text=True)


def test_only_the_owner_can_close(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    login_as(client, donor)
    assert "Close post" not in client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert client.post(f"/posts/{post.id}/close").status_code == 404
    assert post.status is PostStatus.OPEN


def test_closing_requires_login(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    assert client.post(f"/posts/{post.id}/close").status_code == 302
    assert post.status is PostStatus.OPEN


def test_closing_a_missing_post_is_404(client: FlaskClient, poster: User) -> None:
    login_as(client, poster)
    assert client.post("/posts/999/close").status_code == 404
    assert client.post(f"/posts/{2**31}/close").status_code == 404


def test_closing_twice_keeps_the_first_date(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    login_as(client, poster)
    client.post(f"/posts/{post.id}/close")
    closed_at = post.closed_at
    response = client.post(f"/posts/{post.id}/close", follow_redirects=True)
    assert "That post isn&#39;t open anymore." in response.get_data(as_text=True)
    assert post.closed_at == closed_at


def test_closed_post_offers_no_close_even_when_asked(client: FlaskClient, poster: User) -> None:
    post = add_post(poster, age_days=POST_OPEN_DAYS)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}?close=1").get_data(as_text=True)
    assert "Close this post?" not in page
    assert "Close post" not in page
    assert "Delete post" in page


@pytest.mark.parametrize(
    ("age_days", "is_open"), [(POST_OPEN_DAYS - 0.01, True), (POST_OPEN_DAYS, False)]
)
def test_post_closes_on_its_own_at_30_days(
    client: FlaskClient, poster: User, age_days: float, is_open: bool
) -> None:
    post = add_post(poster, age_days=age_days)
    assert post.is_open is is_open
    assert ("Short on rent" in client.get("/feed").get_data(as_text=True)) is is_open
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert ("Open until" in page) is is_open
    assert ("This post is closed" in page) is not is_open


def test_auto_closed_post_takes_no_gifts(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster, age_days=POST_OPEN_DAYS + 2)
    login_as(client, donor)
    response = client.post(
        f"/posts/{post.id}/gifts", data={"amount": "20", "method": PaymentMethod.VENMO.value}
    )
    assert "new gift can&#39;t be recorded" in client.get(response.location).get_data(as_text=True)
    assert post.donations == []


def test_auto_closed_post_frees_a_slot(client: FlaskClient, poster: User) -> None:
    for _ in range(MAX_OPEN_POSTS - 1):
        add_post(poster)
    add_post(poster, age_days=POST_OPEN_DAYS)
    login_as(client, poster)
    response = client.post(
        "/posts/new",
        data={"kind": "need", "title": "Phone bill", "body": "Need it for work.", "goal": "20"},
    )
    assert response.status_code == 302


def test_pending_review_post_still_takes_a_slot(client: FlaskClient, poster: User) -> None:
    for _ in range(MAX_OPEN_POSTS):
        db.session.add(
            Post(
                user=poster,
                kind=PostKind.WANT,
                title="Flagged",
                body="Waiting for review.",
                goal_cents=2_000,
                status=PostStatus.PENDING_REVIEW,
                created_at=utcnow() - timedelta(days=POST_OPEN_DAYS),
            )
        )
    db.session.commit()
    login_as(client, poster)
    response = client.post(
        "/posts/new",
        data={"kind": "need", "title": "Phone bill", "body": "Need it for work.", "goal": "20"},
    )
    assert response.status_code == 409


def test_gift_can_be_confirmed_after_closing(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster)
    gift = add_gift(post, donor)
    post.close()
    db.session.commit()
    login_as(client, poster)
    client.post(f"/gifts/{gift.id}/confirm")
    assert gift.status is DonationStatus.CONFIRMED
    assert post.status is PostStatus.CLOSED


def test_reaching_the_goal_after_auto_close_does_not_fund(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster, age_days=POST_OPEN_DAYS, goal_cents=2_000)
    gift = add_gift(post, donor)
    login_as(client, poster)
    client.post(f"/gifts/{gift.id}/confirm")
    assert gift.status is DonationStatus.CONFIRMED
    assert post.status is PostStatus.OPEN
    assert not post.is_open


def test_close_date_shown_is_the_last_full_day(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    assert post.last_open_day == post.closes_at - timedelta(days=1)
    day = post.last_open_day
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f"Open until {day:%b} {day.day}, {day.year}." in page


def test_funding_records_when_the_post_closed(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster, goal_cents=2_000)
    gift = add_gift(post, donor)
    login_as(client, poster)
    client.post(f"/gifts/{gift.id}/confirm")
    assert post.status is PostStatus.FUNDED
    assert post.closed_at is not None


def test_late_delete_keeps_the_auto_close_date(poster: User, donor: User) -> None:
    post = add_post(poster, age_days=POST_OPEN_DAYS + 10)
    add_gift(post, donor)
    expected = as_utc(post.created_at) + timedelta(days=POST_OPEN_DAYS)
    delete_post(post)
    db.session.commit()
    assert post.status is PostStatus.CLOSED
    assert post.closes_at == expected
