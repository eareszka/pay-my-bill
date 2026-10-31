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
from app.rewards import badges, confirmed_gifts, progress, streak
from tests.conftest import MakeUser


def recipient(make_user: MakeUser, name: str, **fields: object) -> User:
    return make_user(name, created_at=utcnow() - timedelta(days=5), **fields)


def add_post(owner: User) -> Post:
    post = Post(user=owner, kind=PostKind.NEED, title="Rent", body="Short.", goal_cents=90_000)
    db.session.add(post)
    db.session.commit()
    return post


def give(post: Post, donor: User, status: DonationStatus = DonationStatus.CONFIRMED) -> None:
    db.session.add(
        Donation(
            post=post, donor=donor, amount_cents=500, method=PaymentMethod.VENMO, status=status
        )
    )
    db.session.commit()


def test_xp_counts_confirmed_gifts_and_new_people(make_user: MakeUser) -> None:
    donor = make_user("dev_tom")
    rent = add_post(recipient(make_user, "maria_g"))
    book = add_post(recipient(make_user, "kayla.r"))
    give(rent, donor)
    give(rent, donor)
    give(book, donor)
    for status in (DonationStatus.PENDING, DonationStatus.DISPUTED):
        give(add_post(recipient(make_user, f"x_{status.value}")), donor, status)
    p = progress(confirmed_gifts(donor))
    assert (p.xp, p.people_helped) == (3 * 10 + 2 * 25, 2)


@pytest.mark.parametrize("case", ["removed_post", "new_account", "unverified"])
def test_gifts_that_earn_nothing(make_user: MakeUser, case: str) -> None:
    donor = make_user("dev_tom")
    if case == "new_account":
        owner = make_user("maria_g")
    else:
        owner = recipient(make_user, "maria_g", verified=case != "unverified")
    post = add_post(owner)
    if case == "removed_post":
        post.status = PostStatus.REMOVED
    give(post, donor)
    assert progress(confirmed_gifts(donor)).xp == 0


def test_profile_shows_level_and_people_helped(client: FlaskClient, make_user: MakeUser) -> None:
    donor = make_user("dev_tom")
    for i in range(4):
        give(add_post(recipient(make_user, f"friend{i}")), donor)
    page = client.get("/u/dev_tom").get_data(as_text=True)
    assert '<p class="rewards-level">Level 2</p>' in page
    assert "140 / 300 XP · 4 people helped" in page
    assert 'aria-valuenow="20"' in page


def test_new_profile_starts_at_level_1(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("sam_helps")
    page = client.get("/u/sam_helps").get_data(as_text=True)
    assert '<p class="rewards-level">Level 1</p>' in page
    assert "0 / 100 XP · 0 people helped" in page


def test_profile_shows_streak_only_when_active(client: FlaskClient, make_user: MakeUser) -> None:
    donor = make_user("dev_tom")
    assert "week streak" not in client.get("/u/dev_tom").get_data(as_text=True)
    give(add_post(recipient(make_user, "maria_g")), donor)
    assert "1-week streak" in client.get("/u/dev_tom").get_data(as_text=True)


def names(donor: User) -> list[str]:
    gifts = confirmed_gifts(donor)
    return [b.name for b in badges(donor, gifts, streak(gifts))]


def test_badges_by_people_helped(make_user: MakeUser) -> None:
    donor = make_user("dev_tom")
    assert names(donor) == []
    give(add_post(recipient(make_user, "friend0")), donor)
    assert names(donor) == ["First gift"]
    for i in range(1, 25):
        give(add_post(recipient(make_user, f"friend{i}")), donor)
    assert names(donor)[:3] == ["First gift", "Helped 5", "Helped 25"]


def test_local_hero_needs_three_people_in_your_city(make_user: MakeUser) -> None:
    donor = make_user("dev_tom", city="Tampa", state="FL")
    for i, (city, state) in enumerate([("tampa", "FL"), ("Tampa", "FL"), ("Tampa", "WI")]):
        give(add_post(recipient(make_user, f"friend{i}", city=city, state=state)), donor)
    assert "Local hero" not in names(donor)
    give(add_post(recipient(make_user, "friend9", city="Tampa", state="FL")), donor)
    assert "Local hero" in names(donor)


def test_on_a_roll_after_four_weeks(make_user: MakeUser) -> None:
    donor = make_user("dev_tom")
    post = add_post(recipient(make_user, "maria_g"))
    for week in range(4):
        give(post, donor)
        post.donations[-1].created_at = utcnow() - timedelta(weeks=week)
    db.session.commit()
    assert "On a roll" in names(donor)


def test_profile_lists_earned_badges(client: FlaskClient, make_user: MakeUser) -> None:
    donor = make_user("dev_tom")
    assert "badge-list" not in client.get("/u/dev_tom").get_data(as_text=True)
    give(add_post(recipient(make_user, "maria_g")), donor)
    page = client.get("/u/dev_tom").get_data(as_text=True)
    assert '<li title="Had a gift confirmed">First gift</li>' in page
