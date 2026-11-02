import pytest
from flask.testing import FlaskClient
from sqlalchemy import select

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
from tests.conftest import MakeUser, login_as

NOTE = "Made rent on time. Thank you all so much."
ON, OFF = {"on": "1"}, {"on": "0"}


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g")


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom")


@pytest.fixture
def stranger(make_user: MakeUser) -> User:
    return make_user("kayla")


@pytest.fixture
def post(poster: User, donor: User) -> Post:
    post = Post(
        user=poster,
        kind=PostKind.NEED,
        title="Rent",
        body="Short.",
        goal_cents=9_000,
        status=PostStatus.CLOSED,
        closed_at=utcnow(),
        update_body=NOTE,
        update_posted_at=utcnow(),
    )
    post.donations.append(
        Donation(
            donor=donor,
            amount_cents=2_000,
            method=PaymentMethod.VENMO,
            status=DonationStatus.CONFIRMED,
            resolved_at=utcnow(),
        )
    )
    db.session.add(post)
    db.session.commit()
    return post


def kinds(post: Post, user: User) -> set[ReactionKind]:
    rows = db.session.scalars(
        select(Reaction).where(Reaction.post_id == post.id, Reaction.user_id == user.id)
    )
    return {row.kind for row in rows}


def add(post: Post, user: User, kind: ReactionKind) -> None:
    db.session.add(Reaction(post_id=post.id, user_id=user.id, kind=kind))
    db.session.commit()


def test_anyone_verified_can_give_kudos_and_take_it_back(
    client: FlaskClient, post: Post, stranger: User
) -> None:
    login_as(client, stranger)
    response = client.post(f"/posts/{post.id}/react/kudos", data=ON)
    assert response.location.endswith(f"/posts/{post.id}#update")
    assert kinds(post, stranger) == {ReactionKind.KUDOS}
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert 'aria-pressed="true"' in page
    assert "Kudos 1" in page
    assert 'name="on" value="0"' in page
    client.post(f"/posts/{post.id}/react/kudos", data=OFF)
    assert kinds(post, stranger) == set()


def test_unverified_user_cannot_react(client: FlaskClient, post: Post, make_user: MakeUser) -> None:
    user = make_user("new_one", verified=False)
    login_as(client, user)
    assert client.post(f"/posts/{post.id}/react/kudos").status_code != 200
    assert kinds(post, user) == set()
    assert f"/posts/{post.id}/react" not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_logged_out_visitor_is_invited_to_log_in(client: FlaskClient, post: Post) -> None:
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "to give kudos" in page
    assert f"/posts/{post.id}/react" not in page
    assert client.post(f"/posts/{post.id}/react/kudos").status_code == 302


@pytest.mark.parametrize("kind", ["up", "hmm"])
def test_only_people_who_gave_can_judge(
    client: FlaskClient, post: Post, stranger: User, kind: str
) -> None:
    login_as(client, stranger)
    assert client.post(f"/posts/{post.id}/react/{kind}").status_code == 403
    assert kinds(post, stranger) == set()
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert f"/react/{kind}" not in page


@pytest.mark.parametrize("status", [DonationStatus.PENDING, DonationStatus.DISPUTED])
def test_unconfirmed_gift_does_not_count(
    client: FlaskClient, post: Post, stranger: User, status: DonationStatus
) -> None:
    db.session.add(
        Donation(
            post=post,
            donor=stranger,
            amount_cents=500,
            method=PaymentMethod.VENMO,
            status=status,
        )
    )
    db.session.commit()
    login_as(client, stranger)
    assert client.post(f"/posts/{post.id}/react/up").status_code == 403


def test_up_and_hmm_replace_each_other_and_leave_kudos_alone(
    client: FlaskClient, post: Post, donor: User
) -> None:
    login_as(client, donor)
    client.post(f"/posts/{post.id}/react/kudos", data=ON)
    client.post(f"/posts/{post.id}/react/up", data=ON)
    assert kinds(post, donor) == {ReactionKind.KUDOS, ReactionKind.UP}
    client.post(f"/posts/{post.id}/react/hmm", data=ON)
    assert kinds(post, donor) == {ReactionKind.KUDOS, ReactionKind.HMM}
    client.post(f"/posts/{post.id}/react/hmm", data=OFF)
    assert kinds(post, donor) == {ReactionKind.KUDOS}


def test_poster_cannot_react_to_their_own_update(
    client: FlaskClient, post: Post, poster: User
) -> None:
    login_as(client, poster)
    assert client.post(f"/posts/{post.id}/react/kudos").status_code == 403
    assert f"/posts/{post.id}/react" not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_hmm_count_is_hidden_from_people_who_gave(
    client: FlaskClient, post: Post, donor: User, stranger: User
) -> None:
    add(post, donor, ReactionKind.HMM)
    add(post, stranger, ReactionKind.HMM)
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert 'aria-label="Something seems off"' in page
    assert "Something seems off, 2" not in page


def test_hmm_count_is_hidden_from_visitors(client: FlaskClient, post: Post, donor: User) -> None:
    add(post, donor, ReactionKind.HMM)
    assert "Something seems off" not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_admin_sees_the_hmm_count(
    client: FlaskClient, post: Post, donor: User, make_user: MakeUser
) -> None:
    add(post, donor, ReactionKind.HMM)
    login_as(client, make_user("admin_one", is_admin=True))
    assert "Something seems off:</span> 1" in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_admin_who_gave_sees_the_count_on_the_button(
    client: FlaskClient, post: Post, donor: User, stranger: User
) -> None:
    donor.is_admin = True
    add(post, stranger, ReactionKind.HMM)
    login_as(client, donor)
    assert 'aria-label="Something seems off, 1"' in client.get(f"/posts/{post.id}").get_data(
        as_text=True
    )


def test_public_counts_show_to_visitors(
    client: FlaskClient, post: Post, donor: User, stranger: User
) -> None:
    add(post, stranger, ReactionKind.KUDOS)
    add(post, donor, ReactionKind.UP)
    add(post, donor, ReactionKind.KUDOS)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "Kudos 2" in page
    assert "Thumbs up:</span> 1" in page


def test_no_counts_shown_when_there_are_none(client: FlaskClient, post: Post) -> None:
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "Kudos " not in page
    assert "Thumbs up" not in page


@pytest.mark.parametrize("post_id", [999, 2**31])
def test_missing_post(client: FlaskClient, stranger: User, post_id: int) -> None:
    login_as(client, stranger)
    assert client.post(f"/posts/{post_id}/react/kudos").status_code == 404


def test_bad_kind(client: FlaskClient, post: Post, stranger: User) -> None:
    login_as(client, stranger)
    assert client.post(f"/posts/{post.id}/react/love").status_code == 404


def test_no_reacting_without_an_update(client: FlaskClient, post: Post, stranger: User) -> None:
    post.update_body = None
    db.session.commit()
    login_as(client, stranger)
    assert client.post(f"/posts/{post.id}/react/kudos").status_code == 404


def test_no_reacting_on_a_removed_post(client: FlaskClient, post: Post, stranger: User) -> None:
    post.status = PostStatus.REMOVED
    db.session.commit()
    login_as(client, stranger)
    assert client.post(f"/posts/{post.id}/react/kudos").status_code == 404


def test_deleting_the_note_hides_reactions(client: FlaskClient, post: Post, stranger: User) -> None:
    add(post, stranger, ReactionKind.KUDOS)
    delete_post(post)
    db.session.commit()
    assert "Kudos" not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_double_tap_does_not_undo_the_reaction(
    client: FlaskClient, post: Post, stranger: User
) -> None:
    login_as(client, stranger)
    client.post(f"/posts/{post.id}/react/kudos", data=ON)
    client.post(f"/posts/{post.id}/react/kudos", data=ON)
    assert kinds(post, stranger) == {ReactionKind.KUDOS}
    client.post(f"/posts/{post.id}/react/kudos", data=OFF)
    client.post(f"/posts/{post.id}/react/kudos", data=OFF)
    assert kinds(post, stranger) == set()


def test_admin_gets_no_buttons_on_a_removed_post(
    client: FlaskClient, post: Post, make_user: MakeUser
) -> None:
    post.status = PostStatus.REMOVED
    db.session.commit()
    login_as(client, make_user("admin_one", is_admin=True))
    assert f"/posts/{post.id}/react" not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_deleting_an_account_removes_its_reactions(post: Post, stranger: User) -> None:
    add(post, stranger, ReactionKind.KUDOS)
    anonymize(stranger)
    db.session.commit()
    assert kinds(post, stranger) == set()


def test_unverified_user_is_told_to_verify(
    client: FlaskClient, post: Post, make_user: MakeUser
) -> None:
    login_as(client, make_user("new_one", verified=False))
    assert "Verify your email to give kudos." in client.get(f"/posts/{post.id}").get_data(
        as_text=True
    )


def test_poster_with_no_reactions_gets_no_empty_row(
    client: FlaskClient, post: Post, poster: User
) -> None:
    login_as(client, poster)
    assert 'class="reactions"' not in client.get(f"/posts/{post.id}").get_data(as_text=True)


def test_member_is_told_who_can_use_the_emoji(
    client: FlaskClient, post: Post, stranger: User
) -> None:
    login_as(client, stranger)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "People whose gift was confirmed can also use" in page


def test_donor_is_told_what_the_emoji_mean(client: FlaskClient, post: Post, donor: User) -> None:
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert "if something seems off" in page
    assert "People whose gift was confirmed" not in page


def test_poster_gets_no_emoji_hint(client: FlaskClient, post: Post, poster: User) -> None:
    login_as(client, poster)
    assert "reactions-hint" not in client.get(f"/posts/{post.id}").get_data(as_text=True)
