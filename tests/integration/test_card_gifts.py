import hashlib
import hmac
import json
import smtplib
import time
from datetime import timedelta
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import stripe
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select

from app import stripe_pay
from app.extensions import db
from app.models import Donation, DonationStatus, PaymentMethod, Post, PostKind, PostStatus, User
from tests.conftest import MakeUser, login_as

SECRET = "whsec_test"  # noqa: S105 - test fixture


@pytest.fixture(autouse=True)
def stripe_on(app: Flask) -> None:
    app.config.update(STRIPE_SECRET_KEY="sk_test_fake", STRIPE_WEBHOOK_SECRET=SECRET)  # noqa: S106


@pytest.fixture
def fake_client(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    fake = MagicMock()
    fake.v1.checkout.sessions.create.return_value = SimpleNamespace(
        url="https://checkout.stripe.com/c/pay/cs_1"
    )
    monkeypatch.setattr(stripe_pay, "client", lambda: fake)
    return fake


@pytest.fixture
def recipient(make_user: MakeUser) -> User:
    return make_user("maria_g", stripe_account_id="acct_maria", stripe_ready=True)


@pytest.fixture
def post(recipient: User) -> Post:
    post = Post(
        user=recipient, kind=PostKind.NEED, title="Rent", body="Short on rent.", goal_cents=5_000
    )
    db.session.add(post)
    db.session.commit()
    return post


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def signed(client: FlaskClient, event: dict[str, Any], secret: str = SECRET) -> Any:
    payload = json.dumps(event)
    t = int(time.time())
    sig = hmac.new(secret.encode(), f"{t}.{payload}".encode(), hashlib.sha256).hexdigest()
    return client.post(
        "/stripe/webhook",
        data=payload,
        headers={"Stripe-Signature": f"t={t},v1={sig}"},
        content_type="application/json",
    )


def paid_event(
    post: Post, donor: User, gift: int = 2_000, session_id: str = "cs_1", **extra: Any
) -> dict[str, Any]:
    session = {
        "id": session_id,
        "object": "checkout.session",
        "payment_status": "paid",
        "payment_intent": "pi_1",
        "metadata": {
            "post_id": str(post.id),
            "donor_id": str(donor.id),
            "gift_cents": str(gift),
            "fee_cents": str(stripe_pay.charge_for(gift) - gift),
        },
        **extra,
    }
    return {
        "id": "evt_1",
        "object": "event",
        "account": "acct_maria",
        "type": "checkout.session.completed",
        "data": {"object": session},
    }


def gifts() -> list[Donation]:
    return list(db.session.scalars(select(Donation)))


@pytest.mark.parametrize(("gift", "charge"), [(500, 546), (2_000, 2_091), (100_000, 103_018)])
def test_donor_covers_the_fee(gift: int, charge: int) -> None:
    assert stripe_pay.charge_for(gift) == charge
    # What Stripe keeps (2.9% + 30¢ of the charge) never eats into the gift.
    assert charge - (charge * 29 // 1000 + 30) >= gift


def test_post_page_offers_instant_card_gift(client: FlaskClient, post: Post, donor: User) -> None:
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "Chip in instantly" in page
    assert "You cover the card fee" in page
    assert "Or pay in an app" not in page


def test_card_form_hidden_without_stripe_or_when_not_ready(
    app: Flask, client: FlaskClient, post: Post, donor: User, recipient: User
) -> None:
    login_as(client, donor)
    recipient.stripe_ready = False
    recipient.cashapp_handle = "$mariag"
    db.session.commit()
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "Chip in instantly" not in page
    assert "Cash App" in page
    recipient.stripe_ready = True
    db.session.commit()
    assert "Or pay in an app" in client.get(f"/posts/{post.id}").get_data(as_text=True)
    app.config["STRIPE_SECRET_KEY"] = ""
    assert "Chip in instantly" not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_logged_out_visitor_is_asked_to_log_in(client: FlaskClient, post: Post) -> None:
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "Chip in instantly" in page
    assert "Log in first" in page


def test_checkout_redirects_to_stripe_with_direct_charge(
    client: FlaskClient, post: Post, donor: User, fake_client: MagicMock
) -> None:
    login_as(client, donor)
    resp = client.post(f"/posts/{post.id}/card", data={"amount": "$20"})
    assert resp.status_code == 303
    assert resp.location == "https://checkout.stripe.com/c/pay/cs_1"
    params = fake_client.v1.checkout.sessions.create.call_args.kwargs["params"]
    assert params["line_items"][0]["price_data"]["unit_amount"] == 2_091
    assert params["allowed_payment_method_types"] == ["card"]
    assert "transfer_data" not in params["payment_intent_data"]
    options = fake_client.v1.checkout.sessions.create.call_args.kwargs["options"]
    assert options == {"stripe_account": "acct_maria"}
    assert params["metadata"] == {
        "post_id": str(post.id),
        "donor_id": str(donor.id),
        "gift_cents": "2000",
        "fee_cents": "91",
    }
    assert params["customer_email"] == "dev_tom@example.com"
    assert params["success_url"] == f"http://localhost/posts/{post.id}?paid=1"
    assert gifts() == []


@pytest.mark.parametrize(
    ("amount", "message"),
    [("4.99", "from $5 up to $50."), ("51", "from $5 up to $50."), ("abc", "like 20")],
)
def test_checkout_amount_limits(
    client: FlaskClient, post: Post, donor: User, fake_client: MagicMock, amount: str, message: str
) -> None:
    login_as(client, donor)
    resp = client.post(f"/posts/{post.id}/card", data={"amount": amount})
    assert resp.status_code == 400
    assert message in resp.get_data(as_text=True)
    fake_client.v1.checkout.sessions.create.assert_not_called()


def test_checkout_stripe_error_or_missing_url(
    client: FlaskClient,
    post: Post,
    donor: User,
    fake_client: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    login_as(client, donor)
    fake_client.v1.checkout.sessions.create.side_effect = stripe.APIConnectionError("down")
    resp = client.post(f"/posts/{post.id}/card", data={"amount": "20"})
    assert resp.status_code == 400
    assert "Stripe isn&#39;t answering" in resp.get_data(as_text=True)
    assert "Stripe checkout failed" in caplog.text
    fake_client.v1.checkout.sessions.create.side_effect = None
    fake_client.v1.checkout.sessions.create.return_value = SimpleNamespace(url=None)
    assert client.post(f"/posts/{post.id}/card", data={"amount": "20"}).status_code == 400


def test_checkout_refused_cases(
    app: Flask, client: FlaskClient, post: Post, donor: User, recipient: User
) -> None:
    login_as(client, donor)
    assert client.post("/posts/99999/card", data={"amount": "20"}).status_code == 404
    assert client.post("/posts/99999999999/card", data={"amount": "20"}).status_code == 404
    recipient.stripe_ready = False
    db.session.commit()
    resp = client.post(f"/posts/{post.id}/card", data={"amount": "20"})
    assert resp.status_code == 302
    recipient.stripe_ready = True
    post.status = PostStatus.CLOSED
    db.session.commit()
    assert client.post(f"/posts/{post.id}/card", data={"amount": "20"}).status_code == 302
    app.config["STRIPE_SECRET_KEY"] = ""
    assert client.post(f"/posts/{post.id}/card", data={"amount": "20"}).status_code == 404


def test_recipient_cant_pay_own_post(client: FlaskClient, post: Post, recipient: User) -> None:
    login_as(client, recipient)
    assert client.post(f"/posts/{post.id}/card", data={"amount": "20"}).status_code == 404


def test_paid_webhook_records_a_confirmed_gift_once(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    resp = signed(client, paid_event(post, donor))
    assert resp.status_code == 200
    [gift] = gifts()
    assert (gift.amount_cents, gift.fee_cents, gift.method, gift.status) == (
        2_000,
        91,
        PaymentMethod.CARD,
        DonationStatus.CONFIRMED,
    )
    assert (gift.stripe_session_id, gift.stripe_payment_intent) == ("cs_1", "pi_1")
    assert post.raised_cents == 2_000
    assert "dev_tom sent you $20" in caplog.text
    assert "Your $20 gift to maria_g went through" in caplog.text
    assert signed(client, paid_event(post, donor)).status_code == 200
    assert len(gifts()) == 1


def test_paid_webhook_that_funds_the_post(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    signed(client, paid_event(post, donor, gift=5_000))
    db.session.refresh(post)
    assert post.status == PostStatus.FUNDED
    assert "fully funded" in caplog.text


def test_unpaid_or_orphan_sessions_are_ignored(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    signed(client, paid_event(post, donor, payment_status="unpaid"))
    event = paid_event(post, donor, session_id="cs_2")
    event["data"]["object"]["metadata"]["post_id"] = "99999"
    signed(client, event)
    assert gifts() == []
    assert "unusable metadata" in caplog.text


def test_duplicate_delivery_race_is_harmless(client: FlaskClient, post: Post, donor: User) -> None:
    db.session.add(
        Donation(
            post=post,
            donor=donor,
            amount_cents=100,
            method=PaymentMethod.CARD,
            stripe_session_id="cs_1",
        )
    )
    db.session.commit()
    with patch("app.routes.card_gifts.select") as no_check:
        no_check.return_value.where.return_value = None
        with patch("app.routes.card_gifts.db.session.scalar", return_value=None):
            assert signed(client, paid_event(post, donor)).status_code == 200
    assert len(gifts()) == 1


def test_webhook_rejects_bad_signatures_and_needs_a_secret(
    app: Flask, client: FlaskClient, post: Post, donor: User
) -> None:
    wrong = signed(client, paid_event(post, donor), secret="whsec_wrong")  # noqa: S106
    assert wrong.status_code == 400
    assert client.post("/stripe/webhook", data="not json").status_code == 400
    app.config["STRIPE_WEBHOOK_SECRET"] = ""
    assert client.post("/stripe/webhook", data="{}").status_code == 404
    assert gifts() == []


@pytest.mark.parametrize(
    ("event_type", "why"),
    [("charge.refunded", "refunded"), ("charge.dispute.created", "disputed by the card holder")],
)
def test_refund_or_dispute_uncounts_the_gift(
    client: FlaskClient,
    post: Post,
    donor: User,
    make_user: MakeUser,
    caplog: pytest.LogCaptureFixture,
    event_type: str,
    why: str,
) -> None:
    make_user("boss", is_admin=True)
    signed(client, paid_event(post, donor))
    charge = {"id": "ch_1", "object": "charge", "payment_intent": "pi_1", "refunded": True}
    event = {"id": "evt_2", "object": "event", "type": event_type, "data": {"object": charge}}
    assert signed(client, event).status_code == 200
    [gift] = gifts()
    assert gift.status == DonationStatus.DISPUTED
    assert post.raised_cents == 0
    assert f"A card gift was {why}" in caplog.text
    assert signed(client, event).status_code == 200
    other = {"id": "ch_2", "object": "charge", "payment_intent": "pi_other", "refunded": True}
    signed(client, {**event, "data": {"object": other}})
    bare = {"id": "ch_3", "object": "charge", "refunded": True}
    signed(client, {**event, "data": {"object": bare}})


def test_account_updated_webhook_tracks_readiness(
    client: FlaskClient, recipient: User, make_user: MakeUser
) -> None:
    account = {
        "id": "acct_maria",
        "object": "account",
        "charges_enabled": True,
        "payouts_enabled": False,
    }
    event = {
        "id": "evt_3",
        "object": "event",
        "type": "account.updated",
        "data": {"object": account},
    }
    assert signed(client, event).status_code == 200
    db.session.refresh(recipient)
    assert recipient.stripe_ready is False
    account["id"] = "acct_unknown"
    assert signed(client, event).status_code == 200
    unhandled = {"id": "evt_4", "object": "event", "type": "payout.paid", "data": {"object": {}}}
    assert signed(client, unhandled).status_code == 200


def test_webhook_emails_failing_is_logged(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    with patch("app.routes.card_gifts.send_email", side_effect=smtplib.SMTPException("down")):
        assert signed(client, paid_event(post, donor)).status_code == 200
    assert "Could not send" in caplog.text
    assert len(gifts()) == 1


def test_terms_cover_card_gifts(client: FlaskClient) -> None:
    terms = client.get("/terms").get_data(as_text=True)
    assert "Stripe Connected Account Agreement" in terms
    assert "Stripe processes card gifts" in client.get("/privacy").get_data(as_text=True)


def charge_event(event_type: str, **charge: Any) -> dict[str, Any]:
    obj = {"id": "ch_1", "object": "charge", "payment_intent": "pi_1", **charge}
    return {"id": "evt_9", "object": "event", "type": event_type, "data": {"object": obj}}


def test_refund_reopens_a_post_it_had_funded(client: FlaskClient, post: Post, donor: User) -> None:
    signed(client, paid_event(post, donor, gift=5_000))
    db.session.refresh(post)
    assert post.status == PostStatus.FUNDED
    signed(client, charge_event("charge.refunded", refunded=True))
    db.session.refresh(post)
    assert post.status == PostStatus.OPEN
    assert post.closed_at is None
    assert post.is_open


def test_refund_after_30_days_leaves_the_post_closed(
    client: FlaskClient, post: Post, donor: User
) -> None:
    signed(client, paid_event(post, donor, gift=5_000))
    post.created_at = post.created_at - timedelta(days=31)
    db.session.commit()
    signed(client, charge_event("charge.refunded", refunded=True))
    db.session.refresh(post)
    assert post.status == PostStatus.CLOSED


def test_partial_refund_keeps_the_gift_and_tells_admins(
    client: FlaskClient,
    post: Post,
    donor: User,
    make_user: MakeUser,
    caplog: pytest.LogCaptureFixture,
) -> None:
    make_user("boss", is_admin=True)
    signed(client, paid_event(post, donor))
    signed(client, charge_event("charge.refunded", refunded=False, amount_refunded=100))
    [gift] = gifts()
    assert gift.status == DonationStatus.CONFIRMED
    assert "A card gift was partly refunded" in caplog.text
    assert "$1 of dev_tom" in caplog.text
    signed(client, charge_event("charge.refunded", refunded=False, payment_intent="pi_none"))


def test_won_dispute_counts_the_gift_again(
    client: FlaskClient,
    post: Post,
    donor: User,
    make_user: MakeUser,
    caplog: pytest.LogCaptureFixture,
) -> None:
    make_user("boss", is_admin=True)
    signed(client, paid_event(post, donor))
    signed(client, charge_event("charge.dispute.created"))
    lost = charge_event("charge.dispute.closed", status="lost")
    signed(client, lost)
    assert gifts()[0].status == DonationStatus.DISPUTED
    signed(client, charge_event("charge.dispute.closed", status="won"))
    [gift] = gifts()
    assert gift.status == DonationStatus.CONFIRMED
    assert post.raised_cents == 2_000
    assert "A card dispute was won" in caplog.text
    signed(client, charge_event("charge.dispute.closed", status="won"))
    assert "A card dispute was won" in caplog.text


def test_connect_endpoint_secret_is_accepted(
    app: Flask, client: FlaskClient, recipient: User
) -> None:
    app.config.update(STRIPE_WEBHOOK_SECRET="", STRIPE_CONNECT_WEBHOOK_SECRET="whsec_connect")  # noqa: S106
    account = {
        "id": "acct_maria",
        "object": "account",
        "charges_enabled": False,
        "payouts_enabled": True,
    }
    event = {
        "id": "evt_5",
        "object": "event",
        "type": "account.updated",
        "data": {"object": account},
    }
    assert signed(client, event, secret="whsec_connect").status_code == 200  # noqa: S106
    db.session.refresh(recipient)
    assert recipient.stripe_ready is False


def test_missing_gift_amount_is_acknowledged(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    event = paid_event(post, donor)
    del event["data"]["object"]["metadata"]["gift_cents"]
    assert signed(client, event).status_code == 200
    assert gifts() == []
    assert "unusable metadata" in caplog.text


def test_failed_post_update_saves_nothing_so_retry_works(
    client: FlaskClient, post: Post, donor: User
) -> None:
    client.application.config["PROPAGATE_EXCEPTIONS"] = False
    with patch("app.routes.card_gifts.count_confirmed", side_effect=RuntimeError("lock timeout")):
        assert signed(client, paid_event(post, donor)).status_code == 500
    db.session.rollback()
    assert gifts() == []
    assert signed(client, paid_event(post, donor)).status_code == 200
    assert len(gifts()) == 1


def test_card_option_shows_beside_a_waiting_app_gift(
    client: FlaskClient, post: Post, donor: User, recipient: User
) -> None:
    recipient.cashapp_handle = "$mariag"
    db.session.add(Donation(post=post, donor=donor, amount_cents=500, method=PaymentMethod.CASHAPP))
    db.session.commit()
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "waiting for maria_g to confirm" in page
    assert "You can still chip in instantly by card" in page
    assert "Chip in instantly" in page


def test_gift_event_from_another_account_is_not_counted(
    client: FlaskClient, post: Post, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    event = paid_event(post, donor)
    event["account"] = "acct_someone_else"
    assert signed(client, event).status_code == 200
    del event["account"]
    event["data"]["object"]["id"] = "cs_2"
    assert signed(client, event).status_code == 200
    assert gifts() == []
    assert "not the recipient of post" in caplog.text


def test_failed_checkout_rechecks_the_recipient(
    client: FlaskClient, post: Post, donor: User, recipient: User, fake_client: MagicMock
) -> None:
    login_as(client, donor)
    fake_client.v1.checkout.sessions.create.side_effect = stripe.APIConnectionError("down")
    fake_client.v1.accounts.retrieve.return_value = stripe.Account.construct_from(
        {"id": "acct_maria", "charges_enabled": False, "payouts_enabled": True}, "sk_test_fake"
    )
    client.post(f"/posts/{post.id}/card", data={"amount": "20"})
    db.session.refresh(recipient)
    assert recipient.stripe_ready is False
    fake_client.v1.accounts.retrieve.side_effect = stripe.APIConnectionError("down")
    recipient.stripe_ready = True
    db.session.commit()
    assert client.post(f"/posts/{post.id}/card", data={"amount": "20"}).status_code == 400
