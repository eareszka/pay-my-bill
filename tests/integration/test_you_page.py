from datetime import timedelta
from typing import Any

import pytest
from flask.testing import FlaskClient

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
from tests.conftest import MakeUser, login_as


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g")


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom", cashapp_handle="$devtom")


def add_post(owner: User, title: str = "Rent", **fields: Any) -> Post:
    post = Post(
        user=owner, kind=PostKind.NEED, title=title, body="Short.", goal_cents=9_000, **fields
    )
    db.session.add(post)
    db.session.commit()
    return post


def add_gift(post: Post, donor: User, **fields: Any) -> Donation:
    fields.setdefault("status", DonationStatus.PENDING)
    gift = Donation(
        post=post, donor=donor, amount_cents=2_000, method=PaymentMethod.VENMO, **fields
    )
    db.session.add(gift)
    db.session.commit()
    return gift


def test_you_opens_your_profile_with_the_badge(
    client: FlaskClient, poster: User, donor: User
) -> None:
    add_gift(add_post(poster), donor)
    login_as(client, poster)
    page = client.get("/feed").get_data(as_text=True)
    assert 'class="nav-user" href="/u/maria_g"' in page
    you = page.split('class="nav-user"')[1].split("</a>")[0]
    assert '<span class="badge" aria-hidden="true">1</span>' in you
    assert 'href="/gifts"' not in page


def test_owner_sees_tabs_settings_and_to_confirm(
    client: FlaskClient, poster: User, donor: User
) -> None:
    add_gift(add_post(poster), donor)
    login_as(client, poster)
    page = client.get("/u/maria_g").get_data(as_text=True)
    assert 'aria-current="page"' in page.split('aria-label="Main"')[1]
    assert '<a href="/u/maria_g" aria-current="page">Posts</a>' in page
    assert '<a href="/u/maria_g?tab=chipped">Chipped in</a>' in page
    assert 'href="/profile">Settings</a>' in page
    assert page.index("To confirm") < page.index("Your posts")


def test_chipped_in_tab_lists_my_gifts(client: FlaskClient, poster: User, donor: User) -> None:
    add_gift(add_post(poster, "Textbook"), donor, status=DonationStatus.CONFIRMED)
    login_as(client, donor)
    page = client.get("/u/dev_tom?tab=chipped").get_data(as_text=True)
    assert '<a href="/u/dev_tom?tab=chipped" aria-current="page">Chipped in</a>' in page
    assert ">Textbook</a>" in page
    assert 'chip-confirmed">Confirmed' in page
    assert "Your posts" not in page


def test_visitors_see_posts_but_not_gifts(client: FlaskClient, poster: User, donor: User) -> None:
    add_post(donor, "Bus pass")
    add_gift(add_post(poster, "Textbook"), donor, status=DonationStatus.CONFIRMED)
    login_as(client, poster)
    page = client.get("/u/dev_tom?tab=chipped").get_data(as_text=True)
    assert "Bus pass" in page
    assert "Textbook" not in page
    assert "Chipped in" not in page
    assert 'href="/profile">Settings' not in page
    assert "Report dev_tom" in page


def test_posts_say_what_comes_next(client: FlaskClient, poster: User, donor: User) -> None:
    add_post(poster, "Groceries")
    due = add_post(poster, "Gas", status=PostStatus.FUNDED, closed_at=utcnow())
    add_gift(due, donor, status=DonationStatus.CONFIRMED, resolved_at=utcnow())
    late = utcnow() - timedelta(days=20)
    overdue = add_post(poster, "Bill", status=PostStatus.CLOSED, closed_at=late)
    add_gift(overdue, donor, status=DonationStatus.CONFIRMED, resolved_at=late)
    login_as(client, poster)
    page = client.get("/u/maria_g").get_data(as_text=True)
    assert '<span class="chip">Open until ' in page
    assert '<span class="chip">Update due by ' in page
    assert '<span class="chip chip-disputed">Update overdue</span>' in page
    assert f'href="/posts/{overdue.id}#update">Post update' in page
    assert page.count('class="meter"') == 2


def test_visitors_never_see_update_status(client: FlaskClient, poster: User, donor: User) -> None:
    late = utcnow() - timedelta(days=20)
    overdue = add_post(poster, "Bill", status=PostStatus.CLOSED, closed_at=late)
    add_gift(overdue, donor, status=DonationStatus.CONFIRMED, resolved_at=late)
    page = client.get("/u/maria_g").get_data(as_text=True)
    assert '<span class="chip chip-expired">Closed</span>' in page
    assert "Update overdue" not in page
    assert "Post update" not in page


def test_unverified_owner_can_open_their_page(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("newbie", verified=False))
    assert client.get("/u/newbie").status_code == 200


def test_unverified_profiles_stay_hidden(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("newbie", verified=False)
    assert client.get("/u/newbie").status_code == 404


def test_settings_links_back_to_your_profile(client: FlaskClient, poster: User) -> None:
    login_as(client, poster)
    page = client.get("/profile").get_data(as_text=True)
    assert 'class="settings-back" href="/u/maria_g"' in page
    assert "<h1>Settings</h1>" in page
    you = page.split('class="nav-user"')[1].split(">")[0]
    assert 'aria-current="page"' in you


def test_see_your_gifts_opens_chipped_in(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    add_gift(post, donor)
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert 'href="/u/dev_tom?tab=chipped">See your gifts</a>' in page
