import pytest
from flask.testing import FlaskClient
from sqlalchemy import func, select

from app.extensions import db
from app.models import Donation, DonationStatus, PaymentMethod, Post, PostKind, PostStatus, User
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


def test_delete_post_without_confirmed_gifts(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster)
    add_gift(post, donor, DonationStatus.PENDING)
    post_id = post.id
    login_as(client, poster)
    assert client.post(f"/posts/{post_id}/delete").location == "/"
    assert count(Post) == 0
    assert count(Donation) == 0
    assert client.get(f"/posts/{post_id}").status_code == 404


def test_delete_post_with_confirmed_gifts_keeps_credit(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster)
    add_gift(post, donor, DonationStatus.CONFIRMED)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}?delete=1").get_data(as_text=True)
    assert "donors keep credit for their confirmed gifts" in page
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
