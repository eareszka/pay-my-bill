from flask.testing import FlaskClient

from app.extensions import db
from app.models import Donation, DonationStatus, PaymentMethod, Post, PostKind, User
from app.rewards import confirmed_gifts, progress
from tests.conftest import MakeUser


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
    maria, kayla = make_user("maria_g"), make_user("kayla.r")
    rent, book = add_post(maria), add_post(kayla)
    give(rent, donor)
    give(rent, donor)
    give(book, donor)
    for status in (DonationStatus.PENDING, DonationStatus.DISPUTED):
        give(add_post(make_user(f"x_{status.value}")), donor, status)
    p = progress(confirmed_gifts(donor))
    assert (p.xp, p.people_helped) == (3 * 10 + 2 * 25, 2)


def test_profile_shows_level_and_people_helped(client: FlaskClient, make_user: MakeUser) -> None:
    donor = make_user("dev_tom")
    for i in range(4):
        give(add_post(make_user(f"friend{i}")), donor)
    page = client.get("/u/dev_tom").get_data(as_text=True)
    assert '<p class="rewards-level">Level 2</p>' in page
    assert "140 / 300 XP · 4 people helped" in page
    assert 'aria-valuenow="20"' in page


def test_new_profile_starts_at_level_1(client: FlaskClient, make_user: MakeUser) -> None:
    make_user("sam_helps")
    page = client.get("/u/sam_helps").get_data(as_text=True)
    assert '<p class="rewards-level">Level 1</p>' in page
    assert "0 / 100 XP · 0 people helped" in page
