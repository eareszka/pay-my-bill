import logging
from datetime import timedelta

import pytest
from flask.testing import FlaskClient

from app.accounts import anonymize
from app.extensions import db
from app.models import Donation, DonationStatus, PaymentMethod, User, utcnow
from app.routes.gifts import answer_link, send_reminders
from tests.conftest import MakeUser, login_as
from tests.integration.test_gifts_page import add_gift, add_post


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g")


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def named_gift(poster: User, donor: User, **fields: object) -> Donation:
    gift = add_gift(add_post(poster), donor)
    gift.payer_name = "Tom Reyes"
    for key, value in fields.items():
        setattr(gift, key, value)
    db.session.commit()
    return gift


def test_donor_can_add_the_name_on_their_app(
    client: FlaskClient, poster: User, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    post = add_post(poster)
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "Name on your app (optional)" in page
    assert "Only maria_g sees it, to find your payment." in page
    with caplog.at_level(logging.INFO):
        client.post(
            f"/posts/{post.id}/gifts",
            data={"amount": "20", "method": "venmo", "payer_name": "  Tom Reyes "},
        )
    [gift] = post.donations
    assert gift.payer_name == "Tom Reyes"
    assert 'sent you $20 via Venmo as "Tom Reyes" for "Rent"' in caplog.text


def test_name_is_optional_and_capped(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    login_as(client, donor)
    resp = client.post(
        f"/posts/{post.id}/gifts", data={"amount": "20", "method": "venmo", "payer_name": "x" * 61}
    )
    assert resp.status_code == 400
    assert "Names are up to 60 characters." in resp.get_data(as_text=True)
    client.post(f"/posts/{post.id}/gifts", data={"amount": "20", "method": "venmo"})
    assert post.donations[0].payer_name is None


def test_visitors_never_see_the_name(client: FlaskClient, poster: User, donor: User) -> None:
    gift = named_gift(poster, donor)
    assert "Tom Reyes" not in client.get(f"/posts/{gift.post_id}").get_data(as_text=True)
    assert "Tom Reyes" not in client.get("/u/dev_tom").get_data(as_text=True)


def test_poster_sees_the_name(client: FlaskClient, poster: User, donor: User) -> None:
    named_gift(poster, donor)
    login_as(client, poster)
    assert "</a> as “Tom Reyes”</p>" in client.get("/u/maria_g").get_data(as_text=True)


def test_answer_page_shows_name_and_date(client: FlaskClient, poster: User, donor: User) -> None:
    gift = named_gift(poster, donor)
    page = client.get(answer_link(gift).removeprefix("http://localhost")).get_data(as_text=True)
    assert "dev_tom as “Tom Reyes”" in page
    assert f'Sent <time datetime="{gift.created_at.isoformat()}">' in page
    assert "Didn&#39;t get it</button>" in page or "Didn't get it</button>" in page


def sent_on(gift: Donation) -> str:
    return f"{gift.created_at:%b} {gift.created_at.day}, {gift.created_at.year}</time>"


def test_to_confirm_shows_when_it_was_sent(client: FlaskClient, poster: User, donor: User) -> None:
    gift = named_gift(poster, donor)
    login_as(client, poster)
    assert sent_on(gift) in client.get("/u/maria_g").get_data(as_text=True)


def test_chipped_in_shows_when_it_was_sent(client: FlaskClient, poster: User, donor: User) -> None:
    gift = named_gift(poster, donor)
    login_as(client, donor)
    assert sent_on(gift) in client.get("/u/dev_tom?tab=chipped").get_data(as_text=True)


def test_not_received_wording(client: FlaskClient, poster: User, donor: User) -> None:
    gift = add_gift(add_post(poster), donor)
    login_as(client, poster)
    page = client.get(f"/u/maria_g?dispute={gift.id}").get_data(as_text=True)
    assert "Not received</button>" in page
    assert "ispute" not in page.replace("dispute=", "").replace("/dispute", "")


def chipped(client: FlaskClient, donor: User) -> str:
    login_as(client, donor)
    return client.get("/u/dev_tom?tab=chipped").get_data(as_text=True)


def test_not_received_explains_what_to_do(client: FlaskClient, poster: User, donor: User) -> None:
    add_gift(add_post(poster), donor, status=DonationStatus.DISPUTED)
    page = chipped(client, donor)
    assert "maria_g said it didn&#39;t arrive" in page or "maria_g said it didn't arrive" in page
    assert "Check Venmo. If the money left your account, record it again" in page


def test_reversed_card_gift_explains_itself(client: FlaskClient, poster: User, donor: User) -> None:
    gift = add_gift(add_post(poster), donor, status=DonationStatus.DISPUTED)
    gift.method = PaymentMethod.CARD
    db.session.commit()
    page = chipped(client, donor)
    assert "The card payment was reversed" in page
    assert "said it didn" not in page


def test_expired_gift_explains_itself(client: FlaskClient, poster: User, donor: User) -> None:
    gift = add_gift(add_post(poster), donor)
    gift.created_at = utcnow() - timedelta(days=15)
    db.session.commit()
    page = chipped(client, donor)
    assert "maria_g didn&#39;t confirm it within 14 days" in page or (
        "maria_g didn't confirm it within 14 days" in page
    )
    assert "Any money you sent still went to them." in page


def test_confirmed_gift_needs_no_explanation(
    client: FlaskClient, poster: User, donor: User
) -> None:
    add_gift(add_post(poster), donor, status=DonationStatus.CONFIRMED)
    assert 'class="hint gift-explain"' not in chipped(client, donor)


def test_reminder_names_the_payer(
    poster: User, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    named_gift(poster, donor, created_at=utcnow() - timedelta(days=4))
    with caplog.at_level(logging.INFO):
        assert send_reminders() == 1
    assert 'via Venmo as "Tom Reyes" from dev_tom' in caplog.text
    assert "confirm each one or mark it not received" in caplog.text


def test_deleting_the_donor_clears_the_name(poster: User, donor: User) -> None:
    gift = named_gift(poster, donor)
    anonymize(donor)
    db.session.commit()
    db.session.refresh(gift)
    assert gift.payer_name is None
