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
    assert "Newest want" not in first.split("<template")[0]
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


def test_who_and_where_are_for_wide_screens_only(client: FlaskClient, make_user: MakeUser) -> None:
    add_post(make_user(city="Tampa", state="FL"), "Only post")
    page = client.get("/").get_data(as_text=True)
    assert page.index('class="wide-only"') < page.index("Tampa, FL")
    assert 'class="grow"' not in page


def test_chip_in_panel_sits_beside_the_ticket(client: FlaskClient, make_user: MakeUser) -> None:
    post = add_post(make_user(venmo_handle="@maria-g"), "Only post")
    login_as(client, make_user("dev_tom"))
    page = client.get("/").get_data(as_text=True)
    assert 'class="deck-side"' in page
    assert f'action="/posts/{post.id}/gifts"' in page
    assert "side-amount" in page


def test_own_post_has_no_form_beside_the_ticket(client: FlaskClient, make_user: MakeUser) -> None:
    owner = make_user(venmo_handle="@maria-g")
    add_post(owner, "Only post")
    login_as(client, owner)
    page = client.get("/").get_data(as_text=True)
    assert "This is your post." in page
    assert 'class="chip-in"' not in page


def test_empty_board_has_no_panel(client: FlaskClient) -> None:
    assert "deck-side" not in client.get("/").get_data(as_text=True)


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


def test_logging_in_from_the_panel_returns_to_that_post(
    client: FlaskClient, make_user: MakeUser
) -> None:
    post = add_post(make_user(venmo_handle="@maria-g"), "Only post")
    page = client.get("/").get_data(as_text=True)
    assert f'href="/login?next=/posts/{post.id}">Log in first' in page


def test_lone_ticket_does_not_use_the_stack(client: FlaskClient, make_user: MakeUser) -> None:
    add_post(make_user(), "Only post")
    assert "deck-stacked" not in client.get("/").get_data(as_text=True)


def test_swipe_script_loads_only_with_a_ticket(client: FlaskClient, make_user: MakeUser) -> None:
    assert "js/swipe.js" not in client.get("/").get_data(as_text=True)
    add_post(make_user(), "Only post")
    assert "js/swipe.js" in client.get("/").get_data(as_text=True)


def test_back_link_is_there_to_swipe_to(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user()
    add_post(user, "First post")
    add_post(user, "Second post")
    assert "deck-back" not in client.get("/").get_data(as_text=True)
    assert "deck-back" in client.get("/?n=2").get_data(as_text=True)


def under_card(page: str, side: str) -> str:
    start = page.find(f'<template id="deck-under-{side}">')
    return "" if start < 0 else page[start : page.index("</template>", start)]


def three_posts(user: User) -> None:
    for title in ("Oldest post", "Middle post", "Newest post"):
        add_post(user, title)


def test_neighbors_wait_under_a_middle_ticket(client: FlaskClient, make_user: MakeUser) -> None:
    three_posts(make_user(venmo_handle="@maria-g"))
    page = client.get("/?n=2").get_data(as_text=True)
    shown = page[: page.index("<template")]
    titles = ("Oldest post", "Middle post", "Newest post")
    current = next(title for title in titles if title in shown)
    next_title = next(title for title in titles if title in under_card(page, "next"))
    back_title = next(title for title in titles if title in under_card(page, "back"))
    assert {current, next_title, back_title} == set(titles)


def test_first_ticket_has_nothing_to_go_back_to(client: FlaskClient, make_user: MakeUser) -> None:
    three_posts(make_user())
    page = client.get("/").get_data(as_text=True)
    assert under_card(page, "next")
    assert not under_card(page, "back")


def test_last_ticket_wraps_to_the_first_underneath(
    client: FlaskClient, make_user: MakeUser
) -> None:
    three_posts(make_user())
    first = client.get("/").get_data(as_text=True)
    first_title = first[: first.index("<template")]
    last = client.get("/?n=3").get_data(as_text=True)
    wrapped = under_card(last, "next")
    title = next(t for t in ("Oldest post", "Middle post", "Newest post") if t in first_title)
    assert title in wrapped


def test_lone_ticket_has_nothing_underneath(client: FlaskClient, make_user: MakeUser) -> None:
    add_post(make_user(), "Only post")
    assert "<template" not in client.get("/").get_data(as_text=True)


def test_neighbor_checks_its_own_owner(client: FlaskClient, make_user: MakeUser) -> None:
    mine = make_user("mine", venmo_handle="@mine-pays")
    theirs = make_user("theirs", venmo_handle="@they-pay")
    add_post(mine, "My post")
    add_post(theirs, "Their post")
    login_as(client, mine)
    for position in (1, 2):
        page = client.get(f"/?n={position}").get_data(as_text=True)
        under = under_card(page, "next") or under_card(page, "back")
        assert ("tear-tab" in under) == ("Their post" in under)
