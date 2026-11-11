from datetime import timedelta

import pytest
from flask.testing import FlaskClient

from app.accounts import anonymize, delete_post
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

OLD = utcnow() - timedelta(days=30)


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom", created_at=OLD)


def open_post(
    owner: User, donor: User | None = None, raised: int = 0, kind: PostKind = PostKind.NEED
) -> Post:
    owner.venmo_handle = "@has-a-handle"
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


def test_deleting_a_post_does_not_erase_its_hmm(make_user: MakeUser, donor: User) -> None:
    doubted = make_user("doubted")
    past = past_post(doubted, donor)
    react(past, donor, ReactionKind.HMM)
    delete_post(past)
    db.session.commit()
    open_post(doubted)
    newcomer = open_post(make_user("new_one"))
    assert top_post() is newcomer


def test_removing_a_post_does_not_erase_its_hmm(make_user: MakeUser, donor: User) -> None:
    doubted = make_user("doubted")
    past = past_post(doubted, donor)
    react(past, donor, ReactionKind.HMM)
    past.status = PostStatus.REMOVED
    db.session.commit()
    open_post(doubted)
    newcomer = open_post(make_user("new_one"))
    assert top_post() is newcomer


def test_removed_post_earns_no_credit(make_user: MakeUser, donor: User) -> None:
    poster = make_user("poster")
    past = past_post(poster, donor)
    react(past, make_user("fan", created_at=OLD), ReactionKind.KUDOS)
    past.status = PostStatus.REMOVED
    db.session.commit()
    open_post(poster)
    closer = open_post(make_user("new_one"), donor, raised=500)
    assert top_post() is closer


def test_deleted_update_earns_no_credit(make_user: MakeUser, donor: User) -> None:
    poster = make_user("poster")
    delete_post(past_post(poster, donor))
    db.session.commit()
    open_post(poster)
    closer = open_post(make_user("new_one"), donor, raised=500)
    assert top_post() is closer


def test_fake_progress_does_not_win_the_tie(make_user: MakeUser, donor: User) -> None:
    open_post(make_user("faker"), make_user("sock_puppet"), raised=9_900)
    real = open_post(make_user("real_one"), donor, raised=500)
    assert top_post() is real


def test_real_update_keeps_credit_after_the_donor_leaves(make_user: MakeUser, donor: User) -> None:
    keeper = make_user("keeper")
    past_post(keeper, donor)
    anonymize(donor)
    db.session.commit()
    earned = open_post(keeper)
    open_post(make_user("new_one"))
    assert top_post() is earned


def test_sock_account_does_not_start_counting_once_it_ages(
    make_user: MakeUser, donor: User
) -> None:
    faker = make_user("faker")
    sock = make_user("sock_puppet")
    past_post(faker, sock)
    sock.created_at = utcnow() - timedelta(days=30)  # now old, but new when it gave
    gift_made = db.session.query(Donation).filter_by(donor_id=sock.id).one()
    gift_made.created_at = sock.created_at + timedelta(hours=1)
    db.session.commit()
    open_post(faker)
    closer = open_post(make_user("new_one"), donor, raised=500)
    assert top_post() is closer


def test_kudos_on_a_sock_funded_update_cannot_cancel_real_hmm(
    make_user: MakeUser, donor: User
) -> None:
    doubted = make_user("doubted")
    react(past_post(doubted, donor), donor, ReactionKind.HMM)
    sock_funded = past_post(doubted, make_user("sock_puppet"))
    react(sock_funded, make_user("friend", created_at=OLD), ReactionKind.KUDOS)
    open_post(doubted)
    newcomer = open_post(make_user("new_one"))
    assert top_post() is newcomer


def test_poster_with_no_way_to_be_paid_is_out(make_user: MakeUser) -> None:
    keeper = make_user("no_handle")
    open_post(keeper)
    keeper.venmo_handle = None
    db.session.commit()
    assert top_post() is None


def test_gift_from_a_new_account_earns_no_record(make_user: MakeUser) -> None:
    faker = make_user("faker")
    past_post(faker, make_user("sock_puppet"))
    open_post(faker)
    genuine = make_user("genuine")
    past_post(genuine, make_user("real_donor", created_at=OLD))
    earned = open_post(genuine)
    assert top_post() is earned


def test_reactions_from_new_accounts_do_not_count(make_user: MakeUser, donor: User) -> None:
    liked, plain = make_user("liked"), make_user("plain")
    react(past_post(liked, donor), make_user("sock_puppet"), ReactionKind.KUDOS)
    past_post(plain, donor)
    open_post(liked)
    closest = open_post(plain, donor, raised=500)
    assert top_post() is closest


def test_feedback_is_capped_per_update(make_user: MakeUser, donor: User) -> None:
    popular, steady = make_user("popular"), make_user("steady")
    past = past_post(popular, donor)
    for n in range(10):
        react(past, make_user(f"fan_{n}", created_at=OLD), ReactionKind.KUDOS)
    for _ in range(5):
        past_post(steady, donor)
    open_post(popular)
    earned = open_post(steady)
    assert top_post() is earned


def test_filter_picks_a_top_of_that_kind(make_user: MakeUser) -> None:
    open_post(make_user("first"))
    want = open_post(make_user("second"), kind=PostKind.WANT)
    assert top_post(PostKind.WANT) is want


def test_earned_ticket_comes_first_and_is_not_repeated(
    client: FlaskClient, make_user: MakeUser, donor: User
) -> None:
    keeper = make_user("keeper")
    past_post(keeper, donor)
    top = open_post(keeper)
    other = open_post(make_user("second"))
    first = client.get("/feed").get_data(as_text=True)
    assert top.title in first
    assert f'href="/posts/{top.id}#chip-in">Chip in' in first
    assert "1 of 2" in first
    second = client.get("/feed?n=2").get_data(as_text=True)
    assert other.title in second
    assert top.title not in second.split("<template")[0]


def test_stack_without_a_top_is_newest_first(client: FlaskClient, make_user: MakeUser) -> None:
    # A poster with no way to be paid can't earn the spot, but stays in the stack.
    owner = make_user("first")
    older = open_post(owner)
    newer = open_post(owner)
    older.created_at = utcnow() - timedelta(hours=2)
    owner.venmo_handle = None
    db.session.commit()
    assert newer.title in client.get("/feed").get_data(as_text=True)
    assert top_post() is None


def test_own_top_post_has_no_chip_in_tab(client: FlaskClient, make_user: MakeUser) -> None:
    owner = make_user("first")
    open_post(owner)
    login_as(client, owner)
    assert "tear-tab" not in client.get("/feed").get_data(as_text=True)


def test_pile_of_kudos_cannot_cancel_real_doubts(make_user: MakeUser, donor: User) -> None:
    doubted = make_user("doubted")
    past = past_post(doubted, donor)
    for number in range(4):
        react(past, make_user(f"doubter_{number}", created_at=OLD), ReactionKind.HMM)
    for number in range(6):
        react(past, make_user(f"friend_{number}", created_at=OLD), ReactionKind.KUDOS)
    open_post(doubted)
    newcomer = open_post(make_user("new_one"))
    assert top_post() is newcomer


def test_a_banned_donor_earns_nobody_the_top(make_user: MakeUser, donor: User) -> None:
    keeper = make_user("keeper")
    past = past_post(keeper, donor)
    react(past, donor, ReactionKind.KUDOS)
    earned = open_post(keeper)
    newcomer = open_post(make_user("new_one"), make_user("giver", created_at=OLD), raised=500)
    assert top_post() is earned
    donor.banned_at = utcnow()
    db.session.commit()
    # Without that record the keeper is just another poster, and progress decides.
    assert top_post() is newcomer
