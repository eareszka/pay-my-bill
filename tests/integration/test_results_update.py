import logging
import smtplib
from datetime import timedelta

import pytest
from flask.testing import FlaskClient

from app.accounts import anonymize, delete_post
from app.extensions import db
from app.models import (
    POST_OPEN_DAYS,
    UPDATE_DUE_DAYS,
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

NOTE = "Made rent on time. Thank you all so much."


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g")


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


def add_post(owner: User, *donors: User, status: DonationStatus = DonationStatus.CONFIRMED) -> Post:
    post = Post(user=owner, kind=PostKind.NEED, title="Rent", body="Short.", goal_cents=9_000)
    for donor in donors:
        post.donations.append(
            Donation(
                donor=donor,
                amount_cents=2_000,
                method=PaymentMethod.VENMO,
                status=status,
                resolved_at=utcnow(),
            )
        )
    db.session.add(post)
    db.session.commit()
    return post


def closed_post(owner: User, *donors: User) -> Post:
    post = add_post(owner, *donors)
    post.close()
    db.session.commit()
    return post


def add_pending(post: Post, donor: User) -> Donation:
    gift = Donation(post=post, donor=donor, amount_cents=500, method=PaymentMethod.VENMO)
    db.session.add(gift)
    db.session.commit()
    return gift


def emails(caplog: pytest.LogCaptureFixture, address: str) -> int:
    return sum(address in r.getMessage() for r in caplog.records)


def test_open_post_owes_nothing(poster: User, donor: User) -> None:
    assert not add_post(poster, donor).owes_update


def test_closed_post_without_a_confirmed_gift_owes_nothing(poster: User, donor: User) -> None:
    post = add_post(poster, donor, status=DonationStatus.PENDING)
    post.close()
    assert not post.owes_update


@pytest.mark.parametrize("status", [PostStatus.REMOVED, PostStatus.PENDING_REVIEW])
def test_moderated_post_owes_nothing(poster: User, donor: User, status: PostStatus) -> None:
    post = closed_post(poster, donor)
    post.status = status
    assert not post.owes_update


@pytest.mark.parametrize("status", [PostStatus.CLOSED, PostStatus.FUNDED])
def test_closed_or_funded_post_owes_one(poster: User, donor: User, status: PostStatus) -> None:
    post = add_post(poster, donor)
    post.close(status)
    assert post.owes_update


def test_auto_closed_post_owes_one(poster: User, donor: User) -> None:
    post = add_post(poster, donor)
    post.created_at = utcnow() - timedelta(days=POST_OPEN_DAYS)
    assert post.owes_update


def test_due_date_runs_from_the_close(poster: User, donor: User) -> None:
    post = closed_post(poster, donor)
    post.closed_at = utcnow() + timedelta(days=1)
    assert post.update_due_at == post.closes_at + timedelta(days=UPDATE_DUE_DAYS)


def test_late_confirmation_pushes_the_due_date(poster: User, donor: User) -> None:
    post = closed_post(poster, donor)
    post.closed_at = utcnow() - timedelta(days=30)
    confirmed = utcnow() - timedelta(days=1)
    post.confirmed_gifts[0].resolved_at = confirmed
    assert post.update_due_at == confirmed + timedelta(days=UPDATE_DUE_DAYS)


def test_owner_sees_the_prompt_and_privacy_warning(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = closed_post(poster, donor)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    day = post.update_last_day
    assert f"Due by {day:%b} {day.day}, {day.year}. Tell the person who helped" in page
    assert "Receipts are never needed." in page
    assert "account numbers or medical details" in page
    assert f'action="/posts/{post.id}/update#update"' in page


def test_prompt_counts_people_not_gifts(
    client: FlaskClient, poster: User, donor: User, make_user: MakeUser
) -> None:
    post = closed_post(poster, donor, donor, make_user("kayla"))
    login_as(client, poster)
    assert "Tell the 2 people who helped" in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_others_see_when_it_is_due_but_no_form(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = closed_post(poster, donor)
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "maria_g has until" in page
    assert "Post update" not in page


def test_posting_shows_the_update_and_emails_each_donor_once(
    client: FlaskClient,
    poster: User,
    donor: User,
    make_user: MakeUser,
    caplog: pytest.LogCaptureFixture,
) -> None:
    post = closed_post(poster, donor, donor, make_user("kayla"))
    login_as(client, poster)
    with caplog.at_level(logging.INFO):
        response = client.post(
            f"/posts/{post.id}/update", data={"note": f"  {NOTE}  "}, follow_redirects=True
        )
    page = response.get_data(as_text=True)
    assert NOTE in page
    assert "Results update" in page
    assert "Post update" not in page
    assert post.update_body == NOTE
    assert post.update_posted_at is not None
    assert not post.owes_update
    assert emails(caplog, "dev_tom@example.com") == 1
    assert emails(caplog, "kayla@example.com") == 1
    assert emails(caplog, "maria_g@example.com") == 0


def test_everyone_can_read_the_update(client: FlaskClient, poster: User, donor: User) -> None:
    post = closed_post(poster, donor)
    post.update_body = NOTE
    post.update_posted_at = utcnow()
    db.session.commit()
    assert NOTE in client.get(f"/posts/{post.id}").get_data(as_text=True)


@pytest.mark.parametrize(
    ("note", "message"),
    [
        ("", "Tell people how it went."),
        ("Too short.", "Your update needs 20 to 2,000 characters."),
        ("x" * 2001, "Your update needs 20 to 2,000 characters."),
    ],
)
def test_bad_note_is_rejected(
    client: FlaskClient, poster: User, donor: User, note: str, message: str
) -> None:
    post = closed_post(poster, donor)
    login_as(client, poster)
    response = client.post(f"/posts/{post.id}/update", data={"note": note})
    assert response.status_code == 400
    page = response.get_data(as_text=True)
    assert message in page
    assert "Don't share account numbers" in page
    assert post.update_posted_at is None


def test_only_the_owner_can_post(client: FlaskClient, poster: User, donor: User) -> None:
    post = closed_post(poster, donor)
    login_as(client, donor)
    assert client.post(f"/posts/{post.id}/update", data={"note": NOTE}).status_code == 404
    assert post.update_body is None


def test_update_cannot_be_replaced(client: FlaskClient, poster: User, donor: User) -> None:
    post = closed_post(poster, donor)
    login_as(client, poster)
    client.post(f"/posts/{post.id}/update", data={"note": NOTE})
    response = client.post(
        f"/posts/{post.id}/update",
        data={"note": "A completely different story now."},
        follow_redirects=True,
    )
    assert "This post doesn&#39;t need an update." in response.get_data(as_text=True)
    assert post.update_body == NOTE


def test_open_post_cannot_be_updated(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster, donor)
    login_as(client, poster)
    client.post(f"/posts/{post.id}/update", data={"note": NOTE})
    assert post.update_body is None


def test_mail_failure_keeps_the_update(
    client: FlaskClient, poster: User, donor: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*_: object) -> None:
        raise smtplib.SMTPException

    monkeypatch.setattr("app.routes.posts.send_email", fail)
    post = closed_post(poster, donor)
    login_as(client, poster)
    assert client.post(f"/posts/{post.id}/update", data={"note": NOTE}).status_code == 302
    assert post.update_body == NOTE


def test_deleted_donor_is_not_emailed(
    client: FlaskClient, poster: User, donor: User, caplog: pytest.LogCaptureFixture
) -> None:
    post = closed_post(poster, donor)
    anonymize(donor)
    db.session.commit()
    login_as(client, poster)
    with caplog.at_level(logging.INFO):
        client.post(f"/posts/{post.id}/update", data={"note": NOTE})
    assert post.update_body == NOTE
    assert emails(caplog, "@deleted.invalid") == 0


def test_deleted_post_still_owes_and_can_be_updated(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = closed_post(poster, donor)
    delete_post(post)
    db.session.commit()
    assert post.owes_update
    login_as(client, poster)
    assert "Post update" in client.get(f"/posts/{post.id}").get_data(as_text=True)
    client.post(f"/posts/{post.id}/update", data={"note": NOTE})
    assert post.update_body == NOTE
    assert not post.owes_update


def test_delete_prompt_warns_the_update_is_still_owed(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = closed_post(poster, donor)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}?delete=1").get_data(as_text=True)
    assert "You'll still owe a results update." in page


def test_deleting_scrubs_the_note_but_counts_as_updated(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = closed_post(poster, donor)
    login_as(client, poster)
    client.post(f"/posts/{post.id}/update", data={"note": NOTE})
    client.post(f"/posts/{post.id}/delete")
    assert post.update_body is None
    assert post.update_posted_at is not None
    assert not post.owes_update
    assert NOTE not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_note_on_a_deleted_post_can_still_be_removed(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = closed_post(poster, donor)
    delete_post(post)
    db.session.commit()
    login_as(client, poster)
    client.post(f"/posts/{post.id}/update", data={"note": NOTE})
    assert "Delete update" in client.get(f"/posts/{post.id}").get_data(as_text=True)
    page = client.get(f"/posts/{post.id}?delete=1").get_data(as_text=True)
    assert "Delete your results update?" in page
    client.post(f"/posts/{post.id}/delete")
    assert post.update_body is None
    assert "Delete update" not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_close_prompt_mentions_the_update_only_when_it_will_be_owed(
    client: FlaskClient, poster: User, donor: User
) -> None:
    owes = add_post(poster, donor)
    free = add_post(poster)
    login_as(client, poster)
    assert "7 days to post a results update" in client.get(f"/posts/{owes.id}?close=1").get_data(
        as_text=True
    )
    assert "7 days to post" not in client.get(f"/posts/{free.id}?close=1").get_data(as_text=True)


def test_deleted_posters_owed_update_is_not_mentioned(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = closed_post(poster, donor)
    anonymize(poster)
    db.session.commit()
    assert "has until" not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_delete_prompt_on_an_open_post_warns_the_update_will_be_owed(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster, donor)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}?delete=1").get_data(as_text=True)
    assert "still owe a results update" in page


def test_delete_prompt_says_the_update_goes_too(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = closed_post(poster, donor)
    post.update_body = NOTE
    post.update_posted_at = utcnow()
    db.session.commit()
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}?delete=1").get_data(as_text=True)
    assert "Its story and results update are removed" in page
    assert "still owe" not in page


def test_donor_confirmed_after_the_update_is_emailed_once(
    client: FlaskClient,
    poster: User,
    donor: User,
    make_user: MakeUser,
    caplog: pytest.LogCaptureFixture,
) -> None:
    early = make_user("kayla")
    post = closed_post(poster, early)
    gifts = [add_pending(post, donor), add_pending(post, donor), add_pending(post, early)]
    login_as(client, poster)
    client.post(f"/posts/{post.id}/update", data={"note": NOTE})
    caplog.clear()
    with caplog.at_level(logging.INFO):
        for gift in gifts:
            client.post(f"/gifts/{gift.id}/confirm")
    assert emails(caplog, "dev_tom@example.com") == 1
    assert emails(caplog, "kayla@example.com") == 0


def test_disputing_after_the_update_emails_no_one(
    client: FlaskClient,
    poster: User,
    donor: User,
    make_user: MakeUser,
    caplog: pytest.LogCaptureFixture,
) -> None:
    post = closed_post(poster, make_user("kayla"))
    gift = add_pending(post, donor)
    login_as(client, poster)
    client.post(f"/posts/{post.id}/update", data={"note": NOTE})
    caplog.clear()
    with caplog.at_level(logging.INFO):
        client.post(f"/gifts/{gift.id}/dispute")
    assert emails(caplog, "dev_tom@example.com") == 0


def test_confirming_on_a_closed_post_says_an_update_is_owed(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster)
    gift = add_pending(post, donor)
    post.close()
    db.session.commit()
    login_as(client, poster)
    response = client.post(f"/gifts/{gift.id}/confirm", follow_redirects=True)
    assert "You have 7 days to post a results update." in response.get_data(as_text=True)


def test_fundraising_note_is_rejected(client: FlaskClient, poster: User, donor: User) -> None:
    post = closed_post(poster, donor)
    login_as(client, poster)
    response = client.post(
        f"/posts/{post.id}/update", data={"note": "Now invest in my startup, shares available."}
    )
    assert response.status_code == 400
    assert "reads like fundraising" in response.get_data(as_text=True)
    assert post.update_body is None


def test_note_with_a_nul_byte_is_cleaned(client: FlaskClient, poster: User, donor: User) -> None:
    post = closed_post(poster, donor)
    login_as(client, poster)
    client.post(f"/posts/{post.id}/update", data={"note": NOTE + "\x00"})
    assert post.update_body == NOTE


def test_line_breaks_count_as_one_character(client: FlaskClient, poster: User, donor: User) -> None:
    post = closed_post(poster, donor)
    login_as(client, poster)
    note = "\r\n".join(["x" * 99] * 20)
    assert len(note) > 2000
    client.post(f"/posts/{post.id}/update", data={"note": note})
    assert post.update_body == note.replace("\r\n", "\n")
