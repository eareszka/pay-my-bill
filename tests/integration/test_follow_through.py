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
from app.rewards import FollowThrough, follow_through
from tests.conftest import MakeUser


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g")


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def add_post(
    owner: User,
    donor: User | None,
    closed_days_ago: float = 30,
    updated: bool = False,
    status: PostStatus = PostStatus.CLOSED,
    gift_status: DonationStatus = DonationStatus.CONFIRMED,
) -> Post:
    when = utcnow() - timedelta(days=closed_days_ago)
    post = Post(
        user=owner,
        kind=PostKind.NEED,
        title="Rent",
        body="Short.",
        goal_cents=9_000,
        status=status,
        closed_at=when,
        update_posted_at=utcnow() if updated else None,
        update_body="Made rent. Thank you all." if updated else None,
    )
    if donor:
        post.donations.append(
            Donation(
                donor=donor,
                amount_cents=2_000,
                method=PaymentMethod.VENMO,
                status=gift_status,
                resolved_at=when,
            )
        )
    db.session.add(post)
    db.session.commit()
    return post


def test_counts_posted_and_overdue(poster: User, donor: User) -> None:
    add_post(poster, donor, updated=True)
    add_post(poster, donor, updated=True, status=PostStatus.FUNDED)
    add_post(poster, donor)
    assert follow_through(poster) == FollowThrough(2, 3)


def test_post_inside_its_seven_days_does_not_count(poster: User, donor: User) -> None:
    add_post(poster, donor, closed_days_ago=1)
    assert follow_through(poster) == FollowThrough(0, 0)


def test_update_posted_inside_the_seven_days_counts(poster: User, donor: User) -> None:
    add_post(poster, donor, closed_days_ago=1, updated=True)
    assert follow_through(poster) == FollowThrough(1, 1)


def test_posts_that_never_owed_do_not_count(poster: User, donor: User) -> None:
    add_post(poster, None)
    add_post(poster, donor, gift_status=DonationStatus.PENDING)
    add_post(poster, donor, gift_status=DonationStatus.DISPUTED)
    add_post(poster, donor, status=PostStatus.REMOVED)
    assert follow_through(poster) == FollowThrough(0, 0)


def test_other_peoples_posts_do_not_count(poster: User, donor: User) -> None:
    add_post(donor, poster)
    assert follow_through(poster) == FollowThrough(0, 0)


def test_auto_closed_post_counts_once_overdue(poster: User, donor: User) -> None:
    post = add_post(poster, donor, status=PostStatus.OPEN)
    post.closed_at = None
    post.created_at = utcnow() - timedelta(days=40)
    db.session.commit()
    assert follow_through(poster) == FollowThrough(0, 1)


def test_deleted_posts_still_count(poster: User, donor: User) -> None:
    delete_post(add_post(poster, donor))
    delete_post(add_post(poster, donor, updated=True))
    db.session.commit()
    assert follow_through(poster) == FollowThrough(1, 2)


def test_late_confirmation_stays_out_until_its_deadline(poster: User, donor: User) -> None:
    post = add_post(poster, donor)
    post.confirmed_gifts[0].resolved_at = utcnow() - timedelta(days=1)
    db.session.commit()
    assert follow_through(poster) == FollowThrough(0, 0)


def test_profile_shows_the_stat(client: FlaskClient, poster: User, donor: User) -> None:
    add_post(poster, donor, updated=True)
    add_post(poster, donor)
    page = client.get("/u/maria_g").get_data(as_text=True)
    assert "Updated 1 of 2 posts" in page
    assert "Results updates shared, out of those due." in page


def test_profile_says_post_for_one(client: FlaskClient, poster: User, donor: User) -> None:
    add_post(poster, donor, updated=True)
    assert "Updated 1 of 1 post<" in client.get("/u/maria_g").get_data(as_text=True)


def test_profile_hides_the_stat_when_nothing_came_due(
    client: FlaskClient, poster: User, donor: User
) -> None:
    add_post(poster, donor, closed_days_ago=1)
    assert "Updated " not in client.get("/u/maria_g").get_data(as_text=True)
