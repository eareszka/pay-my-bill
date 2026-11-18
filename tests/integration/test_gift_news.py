import logging
from datetime import timedelta

import pytest
from flask.testing import FlaskClient

from app.extensions import db
from app.models import Donation, DonationStatus, PaymentMethod, PostStatus, User, utcnow
from tests.conftest import MakeUser, login_as
from tests.integration.test_gifts_page import add_gift, add_post, resolve


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    # Old enough that gifts to them count toward people helped (T2).
    return make_user("maria_g", created_at=utcnow() - timedelta(days=4))


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def you_page(client: FlaskClient, user: User, tab: str = "posts") -> str:
    login_as(client, user)
    return client.get(f"/u/{user.username}?tab={tab}").get_data(as_text=True)


def test_confirm_emails_the_donor(
    client: FlaskClient, poster: User, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    gift = add_gift(add_post(poster), donor)
    login_as(client, poster)
    with caplog.at_level(logging.INFO):
        resolve(client, gift)
    assert "maria_g confirmed your $20" in caplog.text
    assert 'maria_g confirmed your $20 for "Rent". You\'ve helped 1 person.' in caplog.text
    assert "http://localhost/gifts?tab=chipped" in caplog.text


def test_no_email_when_disputed_or_donor_deleted(
    client: FlaskClient, poster: User, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    post = add_post(poster)
    disputed, kept = add_gift(post, donor), add_gift(post, donor)
    donor.email = "deleted-1@deleted.invalid"
    db.session.commit()
    login_as(client, poster)
    with caplog.at_level(logging.INFO):
        resolve(client, disputed, "dispute")
        resolve(client, kept)
    assert "confirmed your" not in caplog.text


def confirm(gift: Donation) -> None:
    gift.status, gift.resolved_at = DonationStatus.CONFIRMED, utcnow()
    db.session.commit()


def seen(user: User) -> None:
    user.gifts_seen_at = utcnow() - timedelta(minutes=1)
    db.session.commit()


def test_banner_shows_news_once(client: FlaskClient, poster: User, donor: User) -> None:
    seen(donor)
    confirm(add_gift(add_post(poster), donor))
    page = you_page(client, donor)
    assert '<section class="gift-news"' in page
    assert "maria_g confirmed your $20." in page
    assert "You've helped 1 person." in page
    assert 'class="gift-news"' not in client.get("/u/dev_tom").get_data(as_text=True)


def test_banner_skips_card_gifts_removed_posts_and_old_accounts(
    client: FlaskClient, poster: User, donor: User
) -> None:
    seen(donor)
    card = add_gift(add_post(poster), donor)
    card.method = PaymentMethod.CARD
    confirm(card)
    removed = add_post(poster, "Gone")
    confirm(add_gift(removed, donor))
    removed.status = PostStatus.REMOVED
    db.session.commit()
    assert 'class="gift-news"' not in you_page(client, donor)


def test_accounts_from_before_the_banner_get_no_backlog(
    client: FlaskClient, poster: User, donor: User
) -> None:
    donor.gifts_seen_at = None
    db.session.commit()
    confirm(add_gift(add_post(poster), donor))
    assert 'class="gift-news"' not in you_page(client, donor)
    assert donor.gifts_seen_at is not None


def test_visitors_never_see_or_clear_the_news(
    client: FlaskClient, poster: User, donor: User
) -> None:
    seen(donor)
    last_seen = donor.gifts_seen_at
    confirm(add_gift(add_post(poster), donor))
    assert 'class="gift-news"' not in client.get("/u/dev_tom").get_data(as_text=True)
    assert donor.gifts_seen_at == last_seen


def test_chipped_in_shows_the_rewards_strip(client: FlaskClient, poster: User, donor: User) -> None:
    confirm(add_gift(add_post(poster), donor))
    page = you_page(client, donor, "chipped")
    assert '<p class="rewards-strip">Level 1 · 1 person helped · 1-week streak</p>' in page
    assert 'class="rewards-strip"' not in client.get("/u/dev_tom").get_data(as_text=True)


def test_chipped_in_strip_for_a_new_donor(client: FlaskClient, donor: User) -> None:
    page = you_page(client, donor, "chipped")
    assert '<p class="rewards-strip">Level 1 · 0 people helped</p>' in page
