from datetime import timedelta

import pytest
from flask.testing import FlaskClient

from app.extensions import db
from app.leaderboard import Period, Scope, rank
from app.models import Donation, DonationStatus, PaymentMethod, Post, PostKind, User, utcnow
from tests.conftest import MakeUser, login_as

OLD = timedelta(days=30)


def person(make_user: MakeUser, name: str, **fields: object) -> User:
    fields.setdefault("created_at", utcnow() - OLD)
    return make_user(name, **fields)


def post_by(owner: User) -> Post:
    post = Post(user=owner, kind=PostKind.NEED, title="Rent", body="Short.", goal_cents=100_000)
    db.session.add(post)
    db.session.commit()
    return post


def give(donor: User, recipient: User, cents: int = 500, ago: timedelta = timedelta()) -> None:
    when = utcnow() - ago
    db.session.add(
        Donation(
            post=post_by(recipient),
            donor=donor,
            amount_cents=cents,
            method=PaymentMethod.VENMO,
            status=DonationStatus.CONFIRMED,
            created_at=when,
            resolved_at=when,
        )
    )
    db.session.commit()


def board(scope: Scope = Scope.GLOBAL, period: Period = Period.ALL, viewer: User | None = None):  # type: ignore[no-untyped-def]
    return [(r.rank, r.user.username, r.people) for r in rank(scope, period, viewer)]


def test_ranks_by_distinct_people_with_shared_ranks(make_user: MakeUser) -> None:
    tom, kay, lee = (person(make_user, n) for n in ("dev_tom", "kayla.r", "lee_w"))
    r1, r2, r3 = (person(make_user, f"r{i}") for i in range(3))
    for r in (r1, r2, r3):
        give(tom, r)
    give(kay, r1)
    give(kay, r1)
    give(kay, r2, cents=19_000)  # amount never matters
    give(lee, r3)
    give(lee, r1)
    assert board() == [(1, "dev_tom", 3), (2, "kayla.r", 2), (2, "lee_w", 2)]


@pytest.mark.parametrize("who", ["young_donor", "unverified_donor", "young_recipient"])
def test_ineligible_accounts_are_left_out(make_user: MakeUser, who: str) -> None:
    donor = person(
        make_user,
        "dev_tom",
        created_at=utcnow() if who == "young_donor" else utcnow() - OLD,
        verified=who != "unverified_donor",
    )
    recipient = person(
        make_user, "maria_g", created_at=utcnow() if who == "young_recipient" else utcnow() - OLD
    )
    give(donor, recipient)
    assert board() == []


def test_pair_over_200_in_a_week_is_left_out(make_user: MakeUser) -> None:
    tom, maria, kay = (person(make_user, n) for n in ("dev_tom", "maria_g", "kayla.r"))
    give(tom, maria, cents=15_000)
    give(tom, maria, cents=6_000)
    give(tom, kay, cents=20_000)
    assert board() == [(1, "dev_tom", 1)]


def test_this_week_only_counts_gifts_confirmed_this_week(make_user: MakeUser) -> None:
    tom, maria = person(make_user, "dev_tom"), person(make_user, "maria_g")
    give(tom, maria, ago=timedelta(weeks=2))
    assert board(period=Period.WEEK) == []
    assert board(period=Period.ALL) == [(1, "dev_tom", 1)]


def test_state_and_city_scopes_follow_the_viewer(make_user: MakeUser) -> None:
    viewer = person(make_user, "me", city="Tampa", state="FL")
    tampa = person(make_user, "tampa_g", city="tampa ", state="fl")
    miami = person(make_user, "miami_g", city="Miami", state="FL")
    madison = person(make_user, "madison_g", city="Madison", state="WI")
    for i, donor in enumerate((tampa, miami, madison)):
        give(donor, person(make_user, f"r{i}"))
    names = lambda scope: [n for _, n, _ in board(scope, viewer=viewer)]  # noqa: E731
    assert names(Scope.GLOBAL) == ["madison_g", "miami_g", "tampa_g"]
    assert names(Scope.STATE) == ["miami_g", "tampa_g"]
    assert names(Scope.CITY) == ["tampa_g"]


def test_page_tabs_rows_and_empty_state(client: FlaskClient, make_user: MakeUser) -> None:
    page = client.get("/leaders").get_data(as_text=True)
    assert "No one's on this board yet this week." in page
    assert 'aria-label="Where"' not in page
    tom, maria = person(make_user, "dev_tom"), person(make_user, "maria_g")
    give(tom, maria)
    page = client.get("/leaders?period=all&scope=bogus").get_data(as_text=True)
    assert '<span class="leader-rank">1</span>' in page
    assert '<span class="leader-people">1 person</span>' in page
    assert 'href="/leaders?scope=global&amp;period=week"' in page


def test_viewer_row_and_region_tabs(client: FlaskClient, make_user: MakeUser) -> None:
    me = person(make_user, "me", city="Tampa", state="FL")
    give(me, person(make_user, "maria_g"))
    login_as(client, me)
    page = client.get("/leaders?period=all").get_data(as_text=True)
    assert '<li class="is-you" aria-current="true">' in page
    assert ">FL</a>" in page
    assert ">Tampa</a>" in page
    assert "You: #" not in page


def test_viewer_outside_top_20_sees_their_rank(
    client: FlaskClient, make_user: MakeUser, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.routes.leaders.TOP", 1)
    me = person(make_user, "zed")
    top = person(make_user, "alpha")
    r1, r2 = person(make_user, "r1"), person(make_user, "r2")
    give(top, r1)
    give(top, r2)
    give(me, r1)
    login_as(client, me)
    page = client.get("/leaders?period=all").get_data(as_text=True)
    assert "You: #2 · 1 person" in page


def test_logged_out_top_bar_links_leaders(client: FlaskClient) -> None:
    assert 'href="/leaders">Leaders</a>' in client.get("/").get_data(as_text=True)
    page = client.get("/leaders?scope=state").get_data(as_text=True)
    assert 'aria-label="Where"' not in page


def test_top_bar_links_leaders_and_profile_holds_logout(
    client: FlaskClient, make_user: MakeUser
) -> None:
    me = person(make_user, "me")
    login_as(client, me)
    home = client.get("/").get_data(as_text=True)
    assert 'href="/leaders">Leaders</a>' in home
    assert "Log out" not in home
    assert "Log out" in client.get("/profile").get_data(as_text=True)


def test_deleted_recipient_still_counts(make_user: MakeUser) -> None:
    from app.accounts import anonymize

    tom, maria = person(make_user, "dev_tom"), person(make_user, "maria_g")
    give(tom, maria)
    anonymize(maria)
    db.session.commit()
    assert board() == [(1, "dev_tom", 1)]


def test_cap_counts_gifts_on_removed_posts(make_user: MakeUser) -> None:
    from app.models import PostStatus

    tom, maria = person(make_user, "dev_tom"), person(make_user, "maria_g")
    give(tom, maria, cents=15_000)
    removed = maria.posts[0]
    give(tom, maria, cents=10_000)
    removed.status = PostStatus.REMOVED
    db.session.commit()
    assert board() == []


def test_viewer_tied_past_the_cut_still_sees_their_rank(
    client: FlaskClient, make_user: MakeUser, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("app.routes.leaders.TOP", 1)
    me, other, r1 = person(make_user, "zed"), person(make_user, "alpha"), person(make_user, "r1")
    give(other, r1)
    give(me, r1)
    login_as(client, me)
    page = client.get("/leaders?period=all").get_data(as_text=True)
    assert "You: #1 · 1 person" in page
    assert '<span class="sr-only">, you</span>' not in page


def test_viewer_row_is_announced(client: FlaskClient, make_user: MakeUser) -> None:
    me = person(make_user, "me")
    give(me, person(make_user, "maria_g"))
    login_as(client, me)
    assert '<span class="sr-only">, you</span>' in client.get("/leaders?period=all").get_data(
        as_text=True
    )


def test_state_board_skips_donors_without_a_region(make_user: MakeUser) -> None:
    viewer = person(make_user, "me", city="Tampa", state="FL")
    give(person(make_user, "nowhere"), person(make_user, "r1"))
    assert board(Scope.STATE, viewer=viewer) == []
