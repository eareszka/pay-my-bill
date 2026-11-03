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
    Reaction,
    ReactionKind,
    User,
    utcnow,
)
from app.top_spot import top_post
from tests.conftest import MakeUser, login_as


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def open_post(
    owner: User, donor: User | None = None, raised: int = 0, kind: PostKind = PostKind.NEED
) -> Post:
    post = Post(
        user=owner, kind=kind, title=f"Ask from {owner.username}", body="Short.", goal_cents=10_000
    )
    if raised and donor:
        post.donations.append(gift(donor, raised))
    db.session.add(post)
    db.session.commit()
    return post


def gift(donor: User, cents: int = 500, days_ago: float = 1) -> Donation:
    return Donation(
        donor=donor,
        amount_cents=cents,
        method=PaymentMethod.VENMO,
        status=DonationStatus.CONFIRMED,
        resolved_at=utcnow() - timedelta(days=days_ago),
    )


def past_post(owner: User, donor: User, updated: bool = True, days_ago: float = 1) -> Post:
    post = Post(
        user=owner,
        kind=PostKind.NEED,
        title="Past ask",
        body="Past.",
        goal_cents=9_000,
        status=PostStatus.CLOSED,
        closed_at=utcnow() - timedelta(days=days_ago),
        update_body="Made rent. Thank you all." if updated else None,
        update_posted_at=utcnow() if updated else None,
    )
    post.donations.append(gift(donor, days_ago=days_ago))
    db.session.add(post)
    db.session.commit()
    return post


def react(post: Post, user: User, kind: ReactionKind) -> None:
    db.session.add(Reaction(post_id=post.id, user_id=user.id, kind=kind))
    db.session.commit()


def test_empty_board_has_no_top(app: object) -> None:
    assert top_post() is None


def test_first_time_poster_can_win(make_user: MakeUser) -> None:
    post = open_post(make_user("new_one"))
    assert top_post() is post


def test_good_record_beats_a_newcomer_closer_to_goal(make_user: MakeUser, donor: User) -> None:
    keeper = make_user("keeper")
    past_post(keeper, donor)
    earned = open_post(keeper)
    open_post(make_user("new_one"), donor, raised=9_000)
    assert top_post() is earned


def test_overdue_poster_is_out(make_user: MakeUser, donor: User) -> None:
    late = make_user("late_one")
    past_post(late, donor, updated=False, days_ago=30)
    open_post(late, donor, raised=9_000)
    newcomer = open_post(make_user("new_one"))
    assert top_post() is newcomer


def test_only_overdue_posters_leaves_no_top(make_user: MakeUser, donor: User) -> None:
    late = make_user("late_one")
    past_post(late, donor, updated=False, days_ago=30)
    open_post(late)
    assert top_post() is None


def test_update_still_inside_its_seven_days_is_not_a_penalty(
    make_user: MakeUser, donor: User
) -> None:
    owes = make_user("owes_one")
    past_post(owes, donor, updated=False, days_ago=1)
    post = open_post(owes)
    assert top_post() is post


def test_more_feedback_ranks_higher(make_user: MakeUser, donor: User) -> None:
    liked, plain = make_user("liked"), make_user("plain")
    react(past_post(liked, donor), donor, ReactionKind.KUDOS)
    past_post(plain, donor)
    open_post(plain, donor, raised=9_000)
    earned = open_post(liked)
    assert top_post() is earned


def test_closest_to_goal_breaks_ties(make_user: MakeUser, donor: User) -> None:
    open_post(make_user("first"), donor, raised=1_000)
    closest = open_post(make_user("second"), donor, raised=5_000)
    open_post(make_user("third"))
    assert top_post() is closest


def test_oldest_post_wins_a_full_tie(make_user: MakeUser) -> None:
    oldest = open_post(make_user("first"))
    open_post(make_user("second"))
    assert top_post() is oldest


def test_hmm_outweighing_good_feedback_drops_below_newcomers(
    make_user: MakeUser, donor: User
) -> None:
    doubted = make_user("doubted")
    react(past_post(doubted, donor), donor, ReactionKind.HMM)
    open_post(doubted)
    newcomer = open_post(make_user("new_one"))
    assert top_post() is newcomer


def test_scrubbed_update_no_longer_counts_its_feedback(make_user: MakeUser, donor: User) -> None:
    poster = make_user("poster")
    past = past_post(poster, donor)
    react(past, donor, ReactionKind.HMM)
    past.update_body = None
    db.session.commit()
    post = open_post(poster)
    open_post(make_user("new_one"))
    assert top_post() is post


def test_filter_picks_a_top_of_that_kind(make_user: MakeUser) -> None:
    open_post(make_user("first"))
    want = open_post(make_user("second"), kind=PostKind.WANT)
    assert top_post(PostKind.WANT) is want


def test_feed_shows_top_once(client: FlaskClient, make_user: MakeUser) -> None:
    top = open_post(make_user("first"))
    other = open_post(make_user("second"))
    page = client.get("/").get_data(as_text=True)
    assert 'class="ticket top-ticket ticket-need"' in page
    assert page.count(top.title) == 2  # title and the tab's screen-reader text
    assert f'href="/posts/{top.id}#chip-in">Chip in' in page
    assert other.title in page


def test_only_post_shows_no_empty_message(client: FlaskClient, make_user: MakeUser) -> None:
    open_post(make_user("first"))
    assert "No open posts here yet" not in client.get("/").get_data(as_text=True)


def test_top_is_only_on_the_first_page(client: FlaskClient, make_user: MakeUser) -> None:
    open_post(make_user("first"))
    page = client.get("/?page=2").get_data(as_text=True)
    assert "top-ticket" not in page


def test_own_top_post_has_no_chip_in_tab(client: FlaskClient, make_user: MakeUser) -> None:
    owner = make_user("first")
    open_post(owner)
    login_as(client, owner)
    assert "tear-tab" not in client.get("/").get_data(as_text=True)
