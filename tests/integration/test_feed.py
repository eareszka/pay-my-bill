from datetime import timedelta

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


def add_post(
    user: User,
    title: str,
    kind: PostKind = PostKind.NEED,
    status: PostStatus = PostStatus.OPEN,
    hours_ago: int = 0,
) -> Post:
    post = Post(
        user=user,
        kind=kind,
        title=title,
        body="A short story about it.",
        goal_cents=12_050,
        status=status,
        created_at=utcnow() - timedelta(hours=hours_ago),
    )
    db.session.add(post)
    db.session.commit()
    return post


def test_one_ticket_shows_at_a_time_newest_after_the_top(
    client: FlaskClient, make_user: MakeUser
) -> None:
    user = make_user(venmo_handle="@maria-g")
    add_post(user, "The top ticket", hours_ago=9)
    add_post(user, "Older need", hours_ago=5)
    add_post(user, "Newest want", kind=PostKind.WANT, hours_ago=1)
    first = client.get("/").get_data(as_text=True)
    assert "The top ticket" in first
    assert "Newest want" not in first
    assert "1 of 3" in first
    second = client.get("/?n=2").get_data(as_text=True)
    assert "Newest want" in second
    assert "ticket-want" in second
    assert '<span class="sr-only">Want: </span>' in second
    third = client.get("/?n=3").get_data(as_text=True)
    assert "Older need" in third
    assert "ticket-need" in third
    assert "$0</strong> of $120.50" in third


@pytest.mark.parametrize(
    "status", [PostStatus.PENDING_REVIEW, PostStatus.REMOVED, PostStatus.FUNDED, PostStatus.CLOSED]
)
def test_feed_hides_non_open_posts(
    client: FlaskClient, make_user: MakeUser, status: PostStatus
) -> None:
    add_post(make_user(), "Hidden post", status=status)
    page = client.get("/").get_data(as_text=True)
    assert "Hidden post" not in page
    assert "No open posts here yet." in page


@pytest.mark.parametrize(
    ("kind", "shown", "hidden"),
    [("want", "A want", "A need"), ("need", "A need", "A want")],
)
def test_feed_filters_by_kind(
    client: FlaskClient, make_user: MakeUser, kind: str, shown: str, hidden: str
) -> None:
    user = make_user()
    add_post(user, "A want", kind=PostKind.WANT)
    add_post(user, "A need", kind=PostKind.NEED)
    page = client.get(f"/?kind={kind}").get_data(as_text=True)
    assert shown in page
    assert hidden not in page
    assert f'href="/?kind={kind}" aria-current="page"' in page


def test_unknown_kind_shows_all(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user()
    add_post(user, "A want", kind=PostKind.WANT)
    add_post(user, "A need")
    assert "1 of 2" in client.get("/?kind=loan").get_data(as_text=True)


def test_next_and_back_walk_the_stack_and_wrap(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user()
    for i in range(3):
        add_post(user, f"Post number {i}", kind=PostKind.WANT)
    first = client.get("/?kind=want").get_data(as_text=True)
    assert 'href="/?kind=want&amp;n=2">Next ticket' in first
    assert ">Back</a>" not in first
    last = client.get("/?kind=want&n=3").get_data(as_text=True)
    assert 'href="/?kind=want&amp;n=2">Back' in last
    assert 'href="/?kind=want">Next ticket' in last


@pytest.mark.parametrize("bad", ["0", "-3", "abc", "99999999999999999999", "4"])
def test_position_off_the_stack_shows_the_first_ticket(
    client: FlaskClient, make_user: MakeUser, bad: str
) -> None:
    user = make_user()
    for i in range(3):
        add_post(user, f"Post number {i}")
    assert "1 of 3" in client.get(f"/?n={bad}").get_data(as_text=True)


def test_only_ticket_has_no_next_or_stack(client: FlaskClient, make_user: MakeUser) -> None:
    add_post(make_user(), "Only post")
    page = client.get("/").get_data(as_text=True)
    assert "Next ticket" not in page
    assert "deck-stacked" not in page
    assert "1 of 1" in page


def test_ticket_stays_uncluttered(client: FlaskClient, make_user: MakeUser) -> None:
    add_post(make_user(city="Tampa", state="FL"), "Only post")
    page = client.get("/").get_data(as_text=True)
    assert "Tampa, FL" not in page
    assert 'class="grow"' not in page


def test_ticket_body_is_shortened(client: FlaskClient, make_user: MakeUser) -> None:
    post = add_post(make_user(), "Only post")
    post.body = "word " * 100
    db.session.commit()
    assert "word " * 40 not in client.get("/").get_data(as_text=True)


def test_ticket_opens_the_post(client: FlaskClient, make_user: MakeUser) -> None:
    post = add_post(make_user(), "Only post")
    assert f'href="/posts/{post.id}"' in client.get("/").get_data(as_text=True)


def test_no_chip_in_tab_without_a_way_to_pay(client: FlaskClient, make_user: MakeUser) -> None:
    add_post(make_user(), "Only post")
    assert "tear-tab" not in client.get("/").get_data(as_text=True)


def test_empty_state_for_logged_out_visitor(client: FlaskClient) -> None:
    page = client.get("/").get_data(as_text=True)
    assert "No open posts here yet." in page
    assert "to post one" in page


def test_layout_has_mobile_viewport(client: FlaskClient) -> None:
    assert b'name="viewport" content="width=device-width, initial-scale=1"' in client.get("/").data


@pytest.mark.parametrize(
    ("raised", "marks"),
    [(0, 0), (1, 1), (100, 1), (5_000, 5), (9_100, 9), (9_999, 9), (10_000, 10)],
)
def test_progress_marks_only_look_full_when_funded(
    client: FlaskClient, make_user: MakeUser, raised: int, marks: int
) -> None:
    poster, donor = make_user(), make_user("dev_tom")
    post = Post(user=poster, kind=PostKind.NEED, title="Rent", body="Short.", goal_cents=10_000)
    if raised:
        post.donations.append(
            Donation(
                donor=donor,
                amount_cents=raised,
                method=PaymentMethod.VENMO,
                status=DonationStatus.CONFIRMED,
            )
        )
    db.session.add(post)
    db.session.commit()
    assert client.get(f"/posts/{post.id}").get_data(as_text=True).count('class="on"') == marks


def test_heading_is_visible_to_visitors(client: FlaskClient) -> None:
    assert "<h1>Help someone out</h1>" in client.get("/").get_data(as_text=True)


def test_heading_steps_back_for_members(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user())
    assert '<h1 class="sr-only">Help someone out</h1>' in client.get("/").get_data(as_text=True)
