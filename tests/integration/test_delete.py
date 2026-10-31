import logging
from datetime import timedelta

import pytest
from flask.testing import FlaskClient
from sqlalchemy import func, select

from app.extensions import db
from app.models import (
    Donation,
    DonationStatus,
    LoginAttempt,
    PaymentMethod,
    Post,
    PostKind,
    PostStatus,
    User,
)
from tests.conftest import PASSWORD, MakeUser, login_as


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", city="Tampa", state="FL", venmo_handle="@maria-g")


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def add_post(owner: User, title: str = "Rent") -> Post:
    post = Post(
        user=owner, kind=PostKind.NEED, title=title, body="Short on rent.", goal_cents=9_000
    )
    db.session.add(post)
    db.session.commit()
    return post


def add_gift(post: Post, donor: User, status: DonationStatus) -> Donation:
    gift = Donation(
        post=post, donor=donor, amount_cents=2_000, method=PaymentMethod.VENMO, status=status
    )
    db.session.add(gift)
    db.session.commit()
    return gift


def count(model: type) -> int:
    return db.session.scalar(select(func.count()).select_from(model)) or 0


def test_owner_sees_inline_delete_confirm(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f'href="/posts/{post.id}?delete=1#delete">Delete post</a>' in page
    assert "Yes, delete" not in page
    page = client.get(f"/posts/{post.id}?delete=1").get_data(as_text=True)
    assert "Delete this post? It's removed for good." in page
    assert f'action="/posts/{post.id}/delete"' in page


def test_others_see_no_delete(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}?delete=1").get_data(as_text=True)
    assert "Delete post" not in page
    assert "Yes, delete" not in page


def test_delete_post_without_gifts(client: FlaskClient, poster: User) -> None:
    post_id = add_post(poster).id
    login_as(client, poster)
    assert client.post(f"/posts/{post_id}/delete").location == "/"
    assert count(Post) == 0
    assert client.get(f"/posts/{post_id}").status_code == 404


def test_pending_gift_keeps_donor_record(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    gift = add_gift(post, donor, DonationStatus.PENDING)
    login_as(client, poster)
    client.post(f"/posts/{post.id}/delete")
    assert (post.title, post.status) == ("Deleted post", PostStatus.CLOSED)
    assert gift.status is DonationStatus.PENDING
    assert count(Donation) == 1


@pytest.mark.parametrize("status", [PostStatus.REMOVED, PostStatus.FUNDED])
def test_delete_keeps_moderation_and_funded_status(
    client: FlaskClient, poster: User, donor: User, status: PostStatus
) -> None:
    post = add_post(poster)
    add_gift(post, donor, DonationStatus.CONFIRMED)
    post.status = status
    db.session.commit()
    login_as(client, poster)
    client.post(f"/posts/{post.id}/delete")
    assert post.title == "Deleted post"
    assert post.status is status


def test_deleted_post_hides_delete_control(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    add_gift(post, donor, DonationStatus.CONFIRMED)
    login_as(client, poster)
    client.post(f"/posts/{post.id}/delete")
    assert "Delete post" not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_delete_post_with_confirmed_gifts_keeps_credit(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster)
    add_gift(post, donor, DonationStatus.CONFIRMED)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}?delete=1").get_data(as_text=True)
    assert "donors keep credit for their gifts" in page
    client.post(f"/posts/{post.id}/delete")
    assert (post.title, post.body, post.status) == (
        "Deleted post",
        "The poster deleted this post.",
        PostStatus.CLOSED,
    )
    assert post.raised_cents == 2_000
    assert "Short on rent." not in client.get(f"/posts/{post.id}").get_data(as_text=True)


@pytest.mark.parametrize("who", ["donor", "nobody"])
def test_only_owner_can_delete_post(
    client: FlaskClient, poster: User, donor: User, who: str
) -> None:
    post = add_post(poster)
    if who == "donor":
        login_as(client, donor)
        assert client.post(f"/posts/{post.id}/delete").status_code == 404
        assert client.post(f"/posts/{2**31}/delete").status_code == 404
    else:
        assert client.post(f"/posts/{post.id}/delete").location.startswith("/login")
    assert count(Post) == 1


def test_account_delete_asks_for_password(client: FlaskClient, poster: User) -> None:
    login_as(client, poster)
    page = client.get("/profile").get_data(as_text=True)
    assert 'href="/profile?delete=1#delete">Delete my account</a>' in page
    assert "Your password" not in page
    page = client.get("/profile?delete=1").get_data(as_text=True)
    assert "Donors keep credit for gifts you confirmed." in page
    assert 'action="/account/delete"' in page


def test_wrong_password_keeps_account(client: FlaskClient, poster: User) -> None:
    login_as(client, poster)
    resp = client.post("/account/delete", data={"password": "wrong-password"})
    assert resp.status_code == 400
    assert "That password isn&#39;t right." in resp.get_data(as_text=True)
    assert poster.username == "maria_g"


def test_delete_account_anonymizes_and_logs_out(
    client: FlaskClient, poster: User, donor: User
) -> None:
    plain = add_post(poster, "Plain")
    funded = add_post(poster, "Funded")
    add_gift(funded, donor, DonationStatus.CONFIRMED)
    plain_id, poster_id = plain.id, poster.id
    login_as(client, poster)
    resp = client.post("/account/delete", data={"password": PASSWORD})
    assert resp.location == "/"
    user = db.session.get(User, poster_id)
    assert user is not None
    assert user.username == f"deleted-{poster_id}"
    assert user.email == f"deleted-{poster_id}@deleted.invalid"
    assert not any(
        (user.email_verified_at, user.city, user.state, user.venmo_handle, user.cashapp_handle)
    )
    assert db.session.get(Post, plain_id) is None
    assert funded.title == "Deleted post"
    assert funded.raised_cents == 2_000
    assert client.get("/u/maria_g").status_code == 404
    assert client.get("/profile").location.startswith("/login")
    login = client.post("/login", data={"identifier": "maria_g", "password": PASSWORD})
    assert "Wrong username, email, or password." in login.get_data(as_text=True)


def test_deleted_account_sessions_end(
    client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    other_device = client.application.test_client()
    login_as(client, poster)
    client.post("/account/delete", data={"password": PASSWORD})
    login_as(other_device, poster)
    assert other_device.get("/profile").location.startswith("/login")


def test_delete_account_is_rate_limited(client: FlaskClient, poster: User) -> None:
    login_as(client, poster)
    for _ in range(6):
        client.post("/account/delete", data={"password": "wrong-password"})
    resp = client.post("/account/delete", data={"password": PASSWORD})
    assert "Too many failed attempts." in resp.get_data(as_text=True)
    assert poster.username == "maria_g"


def test_delete_account_clears_login_history(client: FlaskClient, poster: User) -> None:
    db.session.add(LoginAttempt(identifier="maria_g", ip="1.2.3.4", succeeded=False))
    db.session.add(LoginAttempt(identifier="maria_g@example.com", ip="1.2.3.4", succeeded=False))
    db.session.commit()
    login_as(client, poster)
    client.post("/account/delete", data={"password": PASSWORD})
    identifiers = set(db.session.scalars(select(LoginAttempt.identifier)))
    assert not identifiers & {"maria_g", "maria_g@example.com"}


def test_reminders_skip_deleted_posters(
    client: FlaskClient, poster: User, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    post = add_post(poster)
    gift = add_gift(post, donor, DonationStatus.PENDING)
    gift.created_at = gift.created_at - timedelta(days=4)
    db.session.commit()
    login_as(client, poster)
    client.post("/account/delete", data={"password": PASSWORD})
    with caplog.at_level(logging.INFO):
        result = client.application.test_cli_runner().invoke(args=["gifts", "remind"])
    assert result.output == "Reminder emails sent: 0\n"
    assert "deleted.invalid" not in caplog.text
