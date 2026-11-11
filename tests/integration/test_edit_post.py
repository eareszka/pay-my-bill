from datetime import timedelta
from typing import Any

import pytest
from flask.testing import FlaskClient

from app.extensions import db
from app.models import (
    DELETED_POST_BODY,
    DELETED_POST_TITLE,
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

EDIT = {"kind": "want", "title": "New tires", "body": "My front tires are bald.", "goal": "$250"}


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g")


def add_post(owner: User, title: str = "Rent", **fields: Any) -> Post:
    fields.setdefault("body", "Short on rent this month.")
    post = Post(user=owner, kind=PostKind.NEED, title=title, goal_cents=9_000, **fields)
    db.session.add(post)
    db.session.commit()
    return post


def add_gift(
    post: Post, donor: User, status: DonationStatus = DonationStatus.CONFIRMED, **fields: Any
) -> None:
    db.session.add(
        Donation(
            post=post,
            donor=donor,
            amount_cents=2_000,
            method=PaymentMethod.VENMO,
            status=status,
            **fields,
        )
    )
    db.session.commit()


def test_edit_page_is_prefilled(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}/edit").get_data(as_text=True)
    assert "Edit your post" in page
    assert 'value="Rent"' in page
    assert 'value="$90"' in page
    assert "Short on rent this month." in page
    assert "Community Rules" not in page


def test_owner_edits_every_field_before_a_gift(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    login_as(client, poster)
    resp = client.post(f"/posts/{post.id}/edit", data=EDIT, follow_redirects=True)
    assert b"Your post was updated." in resp.data
    db.session.refresh(post)
    assert (post.kind, post.title, post.body, post.goal_cents) == (
        PostKind.WANT,
        "New tires",
        "My front tires are bald.",
        25_000,
    )
    assert post.edited_at is not None
    assert b"Edited " in resp.data


def test_unchanged_save_is_not_marked_edited(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    login_as(client, poster)
    data = {"kind": "need", "title": "Rent", "body": "Short on rent this month.", "goal": "90"}
    resp = client.post(f"/posts/{post.id}/edit", data=data)
    assert resp.status_code == 302
    db.session.refresh(post)
    assert post.edited_at is None
    assert b"Edited " not in client.get(f"/posts/{post.id}").data


def test_only_the_story_changes_after_a_gift(
    client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    post = add_post(poster)
    add_gift(post, make_user("dev_tom"))
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}/edit").get_data(as_text=True)
    assert "Someone has chipped in" in page
    assert 'name="title"' not in page
    assert 'name="goal"' not in page
    client.post(f"/posts/{post.id}/edit", data=EDIT)
    db.session.refresh(post)
    assert (post.kind, post.title, post.goal_cents) == (PostKind.NEED, "Rent", 9_000)
    assert post.body == "My front tires are bald."


@pytest.mark.parametrize(
    ("status", "fields", "locked"),
    [
        (DonationStatus.PENDING, {}, True),
        (DonationStatus.PENDING, {"created_at": utcnow() - timedelta(days=15)}, False),
        (DonationStatus.DISPUTED, {}, False),
    ],
)
def test_waiting_gifts_lock_but_failed_ones_dont(
    client: FlaskClient,
    poster: User,
    make_user: MakeUser,
    status: DonationStatus,
    fields: dict[str, Any],
    locked: bool,
) -> None:
    post = add_post(poster)
    add_gift(post, make_user("dev_tom"), status, **fields)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}/edit").get_data(as_text=True)
    assert ('name="title"' not in page) is locked


def test_invalid_edit_shows_errors(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    login_as(client, poster)
    resp = client.post(f"/posts/{post.id}/edit", data={**EDIT, "goal": "$5,000"})
    assert resp.status_code == 200
    assert b"Goals are capped" in resp.data
    db.session.refresh(post)
    assert post.title == "Rent"


def test_flagged_edit_goes_back_to_review(
    client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    make_user("admin", is_admin=True)
    post = add_post(poster)
    login_as(client, poster)
    resp = client.post(
        f"/posts/{post.id}/edit",
        data={**EDIT, "body": "Help me invest in my startup."},
        follow_redirects=True,
    )
    assert b"will show after a quick review" in resp.data
    db.session.refresh(post)
    assert post.status == PostStatus.PENDING_REVIEW


def test_post_in_review_can_be_edited(client: FlaskClient, poster: User) -> None:
    post = add_post(poster, status=PostStatus.PENDING_REVIEW)
    login_as(client, poster)
    client.post(f"/posts/{post.id}/edit", data=EDIT)
    db.session.refresh(post)
    assert post.title == "New tires"
    assert post.status == PostStatus.PENDING_REVIEW


@pytest.mark.parametrize("state", ["closed", "expired", "deleted"])
def test_finished_posts_cant_be_edited(client: FlaskClient, poster: User, state: str) -> None:
    fields: dict[str, Any] = {
        "closed": {"status": PostStatus.CLOSED, "closed_at": utcnow()},
        "expired": {"created_at": utcnow() - timedelta(days=31)},
        "deleted": {"body": DELETED_POST_BODY},
    }[state]
    title = DELETED_POST_TITLE if state == "deleted" else "Rent"
    post = add_post(poster, title, **fields)
    login_as(client, poster)
    resp = client.get(f"/posts/{post.id}/edit", follow_redirects=True)
    assert b"Only open posts can be edited." in resp.data
    assert b"Edit post</a>" not in resp.data


def test_others_cant_edit(client: FlaskClient, poster: User, make_user: MakeUser) -> None:
    post = add_post(poster)
    login_as(client, make_user("dev_tom"))
    assert client.get(f"/posts/{post.id}/edit").status_code == 404
    assert client.post(f"/posts/{post.id}/edit", data=EDIT).status_code == 404


def test_post_page_links_to_edit_for_owner(client: FlaskClient, poster: User) -> None:
    post = add_post(poster)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f'href="/posts/{post.id}/edit">Edit post</a>' in page


def test_post_page_has_no_edit_for_others(
    client: FlaskClient, poster: User, make_user: MakeUser
) -> None:
    post = add_post(poster)
    login_as(client, make_user("dev_tom"))
    assert b"Edit post</a>" not in client.get(f"/posts/{post.id}").data


def test_profile_lists_public_posts(client: FlaskClient, poster: User, make_user: MakeUser) -> None:
    add_post(poster, "Groceries")
    add_post(poster, "Gas money", status=PostStatus.FUNDED, closed_at=utcnow())
    add_post(poster, "Old bill", status=PostStatus.CLOSED, closed_at=utcnow())
    add_post(poster, "Hidden", status=PostStatus.PENDING_REVIEW)
    add_post(poster, "Gone", status=PostStatus.REMOVED)
    add_post(poster, DELETED_POST_TITLE).body = DELETED_POST_BODY
    db.session.commit()
    login_as(client, make_user("dev_tom"))
    page = client.get("/u/maria_g").get_data(as_text=True)
    assert "Groceries" in page
    assert 'Need · <span class="chip">Open until ' in page
    assert 'Need · <span class="chip chip-confirmed">Funded</span>' in page
    assert 'Need · <span class="chip chip-expired">Closed</span>' in page
    assert "$0<span" in page
    for hidden in ("Hidden", "Gone", DELETED_POST_TITLE):
        assert hidden not in page
    assert "/edit" not in page
    assert "delete=1" not in page


def test_owner_sees_review_posts_and_actions(client: FlaskClient, poster: User) -> None:
    open_post = add_post(poster, "Groceries")
    review = add_post(poster, "Hidden", status=PostStatus.PENDING_REVIEW)
    done = add_post(poster, "Old bill", status=PostStatus.CLOSED, closed_at=utcnow())
    login_as(client, poster)
    page = client.get("/u/maria_g").get_data(as_text=True)
    assert 'Need · <span class="chip">In review</span>' in page
    assert f'href="/posts/{open_post.id}/edit"' in page
    assert f'href="/posts/{review.id}/edit"' in page
    assert f'href="/posts/{done.id}/edit"' not in page
    assert f'href="/posts/{done.id}?delete=1#delete"' in page


def test_profile_post_list_is_capped(client: FlaskClient, poster: User) -> None:
    for n in range(21):
        add_post(poster, f"Bill {n}", status=PostStatus.CLOSED, closed_at=utcnow())
    page = client.get("/u/maria_g").get_data(as_text=True)
    assert "Showing the latest 20 posts." in page
    assert "Bill 20" in page
    assert ">Bill 0<" not in page


def test_profile_empty_state_for_visitors(client: FlaskClient, poster: User) -> None:
    assert b"maria_g hasn't posted yet." in client.get("/u/maria_g").data


def test_profile_empty_state_for_owner(client: FlaskClient, poster: User) -> None:
    login_as(client, poster)
    assert b"You haven't posted yet." in client.get("/u/maria_g").data
