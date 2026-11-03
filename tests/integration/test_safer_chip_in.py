from datetime import timedelta

import pytest
from flask.testing import FlaskClient

from app.accounts import delete_post
from app.extensions import db
from app.models import (
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    PostKind,
    PostStatus,
    User,
    utcnow,
)
from app.tokens import VERIFY_EMAIL, make_token
from tests.conftest import PASSWORD, MakeUser, login_as

GIFT = {"amount": "20", "method": "venmo"}


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g", cashapp_handle="$mariag")


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def add_post(owner: User, closed_hours_ago: float | None = None) -> Post:
    post = Post(user=owner, kind=PostKind.NEED, title="Rent", body="Short.", goal_cents=30_000)
    if closed_hours_ago is not None:
        post.status = PostStatus.CLOSED
        post.closed_at = utcnow() - timedelta(hours=closed_hours_ago)
    db.session.add(post)
    db.session.commit()
    return post


def test_visitor_is_warned_before_the_pay_buttons(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert page.index("Log in first") < page.index('class="pay-buttons"')
    assert f'href="/login?next=/posts/{post.id}">Log in first' in page
    assert "Already paid?" in page


def test_login_and_signup_keep_the_way_back(client: FlaskClient) -> None:
    assert 'href="/signup?next=/posts/1"' in client.get("/login?next=/posts/1").get_data(
        as_text=True
    )
    assert 'href="/login?next=/posts/1"' in client.get("/signup?next=/posts/1").get_data(
        as_text=True
    )


def test_verifying_returns_to_the_post(client: FlaskClient, make_user: MakeUser) -> None:
    client.post(
        "/signup?next=/posts/7",
        data={
            "username": "new_one",
            "email": "new@example.com",
            "password": "s3cret-pass",
            "confirm": "s3cret-pass",
            "adult": "y",
        },
    )
    user = db.session.query(User).filter_by(username="new_one").one()
    token = make_token(user.id, user.email, VERIFY_EMAIL)
    assert client.get(f"/verify/{token}").location.endswith("/posts/7")


def test_signup_ignores_an_off_site_next(client: FlaskClient) -> None:
    client.post(
        "/signup?next=https://evil.example/",
        data={
            "username": "new_one",
            "email": "new@example.com",
            "password": "s3cret-pass",
            "confirm": "s3cret-pass",
            "adult": "y",
        },
    )
    user = db.session.query(User).filter_by(username="new_one").one()
    token = make_token(user.id, user.email, VERIFY_EMAIL)
    assert "evil.example" not in client.get(f"/verify/{token}").location


def test_placeholder_is_replaced_by_a_hint(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "placeholder" not in page
    assert "Any amount up to $300." in page
    assert '<label for="method">Paid with</label>' in page


def test_one_app_is_preselected(client: FlaskClient, make_user: MakeUser, donor: User) -> None:
    post = add_post(make_user("solo", venmo_handle="@solo-one"))
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "Choose app" not in page


def test_waiting_gift_replaces_the_form(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    db.session.add(Donation(post=post, donor=donor, amount_cents=2_000, method=PaymentMethod.VENMO))
    db.session.commit()
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "Your $20 gift is waiting for maria_g to confirm." in page
    assert 'class="pay-buttons"' not in page


@pytest.mark.parametrize(
    "gift",
    [
        {"status": DonationStatus.CONFIRMED},
        {"status": DonationStatus.PENDING, "created_at": utcnow() - timedelta(days=20)},
    ],
)
def test_finished_gift_does_not_block_another(
    client: FlaskClient, poster: User, donor: User, gift: dict[str, object]
) -> None:
    post = add_post(poster)
    db.session.add(
        Donation(post=post, donor=donor, amount_cents=2_000, method=PaymentMethod.VENMO, **gift)
    )
    db.session.commit()
    login_as(client, donor)
    assert 'class="pay-buttons"' in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_gift_can_be_recorded_within_a_day_of_closing(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster, closed_hours_ago=23)
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "This post just closed." in page
    assert 'class="pay-buttons"' not in page
    assert client.post(f"/posts/{post.id}/gifts", data=GIFT).status_code == 302
    assert len(post.donations) == 1


def test_gift_is_refused_after_a_day(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster, closed_hours_ago=25)
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert 'id="chip-in"' not in page
    assert "isn't taking gifts" in page
    client.post(f"/posts/{post.id}/gifts", data=GIFT)
    assert post.donations == []


def test_auto_closed_post_gets_the_same_day(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    post.created_at = utcnow() - timedelta(days=30, hours=23)
    db.session.commit()
    login_as(client, donor)
    assert client.post(f"/posts/{post.id}/gifts", data=GIFT).status_code == 302
    assert len(post.donations) == 1


def test_deleted_post_takes_no_late_gifts(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    db.session.add(
        Donation(
            post=post,
            donor=donor,
            amount_cents=500,
            method=PaymentMethod.VENMO,
            status=DonationStatus.CONFIRMED,
        )
    )
    delete_post(post)
    db.session.commit()
    login_as(client, donor)
    client.post(f"/posts/{post.id}/gifts", data=GIFT)
    assert len(post.donations) == 1


def test_owner_gets_no_late_form(client: FlaskClient, poster: User) -> None:
    post = add_post(poster, closed_hours_ago=1)
    login_as(client, poster)
    assert 'id="chip-in"' not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_late_visitor_is_told_to_log_in(client: FlaskClient, poster: User) -> None:
    post = add_post(poster, closed_hours_ago=1)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "Log in first" not in page
    assert "to record your gift so it counts." in page


def test_unverified_donor_is_told_before_paying(
    client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    post = add_post(poster)
    login_as(client, make_user("new_one", verified=False))
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert page.index("Verify your email first") < page.index('class="pay-buttons"')


def test_unverified_login_keeps_the_way_back(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user("new_one", verified=False)
    client.post("/login?next=/posts/7", data={"identifier": "new_one", "password": PASSWORD})
    token = make_token(user.id, user.email, VERIFY_EMAIL)
    assert client.get(f"/verify/{token}").location.endswith("/posts/7")


def test_waiting_gift_stays_visible_after_the_window(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster, closed_hours_ago=48)
    db.session.add(Donation(post=post, donor=donor, amount_cents=2_000, method=PaymentMethod.VENMO))
    db.session.commit()
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "gift is waiting for maria_g" in page
    assert "You can chip in again" not in page


def test_deleted_post_says_why_a_gift_is_refused(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster)
    db.session.add(
        Donation(
            post=post,
            donor=donor,
            amount_cents=500,
            method=PaymentMethod.VENMO,
            status=DonationStatus.CONFIRMED,
        )
    )
    delete_post(post)
    db.session.commit()
    login_as(client, donor)
    response = client.post(f"/posts/{post.id}/gifts", data=GIFT, follow_redirects=True)
    assert "This post was deleted, so a new gift" in response.get_data(as_text=True)


def test_closed_post_without_handles_does_not_promise_a_return(
    client: FlaskClient, make_user: MakeUser, donor: User
) -> None:
    post = add_post(make_user("no_handles"), closed_hours_ago=1)
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "no longer lists a payment app" in page
    assert "Check back soon" not in page
