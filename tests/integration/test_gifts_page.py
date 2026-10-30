import pytest
from flask.testing import FlaskClient

from app.extensions import db
from app.models import Donation, DonationStatus, PaymentMethod, Post, PostKind, PostStatus, User
from tests.conftest import MakeUser, login_as


@pytest.fixture
def poster(make_user: MakeUser) -> User:
    return make_user("maria_g", venmo_handle="@maria-g")


@pytest.fixture
def donor(make_user: MakeUser) -> User:
    return make_user("dev_tom", cashapp_handle="$devtom")


def add_post(owner: User, title: str = "Rent", goal_cents: int = 30_000) -> Post:
    post = Post(user=owner, kind=PostKind.NEED, title=title, body="Short.", goal_cents=goal_cents)
    db.session.add(post)
    db.session.commit()
    return post


def add_gift(
    post: Post, donor: User, cents: int = 2_000, status: DonationStatus = DonationStatus.PENDING
) -> Donation:
    gift = Donation(
        post=post, donor=donor, amount_cents=cents, method=PaymentMethod.VENMO, status=status
    )
    db.session.add(gift)
    db.session.commit()
    return gift


def resolve(client: FlaskClient, gift: Donation, action: str = "confirm"):  # type: ignore[no-untyped-def]
    return client.post(f"/gifts/{gift.id}/{action}")


def test_requires_login(client: FlaskClient) -> None:
    assert client.get("/gifts").location.startswith("/login")


def test_lists_gifts_to_confirm_and_my_gifts(
    client: FlaskClient, poster: User, donor: User, make_user: MakeUser
) -> None:
    rent = add_post(poster)
    add_gift(rent, donor, 2_000)
    add_gift(rent, donor, 700, DonationStatus.CONFIRMED)
    other = add_post(make_user("kayla.r"), "Textbook")
    add_gift(other, donor, 900)
    add_gift(other, poster, 1_500, DonationStatus.DISPUTED)
    login_as(client, poster)
    page = client.get("/gifts").get_data(as_text=True)
    to_confirm, sent = page.split("My gifts")
    assert '<span class="count">1</span>' in to_confirm
    assert '<p class="gift-amount">$20</p>' in to_confirm
    assert "via Venmo from" in to_confirm
    assert "$7" not in to_confirm
    assert "$9" not in to_confirm
    gift_id = rent.donations[0].id
    assert f'action="/gifts/{gift_id}/confirm"' in to_confirm
    assert f'href="/gifts?dispute={gift_id}#gift-{gift_id}">Didn\'t get it</a>' in to_confirm
    assert "Dispute this gift?" not in to_confirm
    assert '<span class="gift-list-amount">$15</span>' in sent
    assert 'chip-disputed">Not received' in sent


def test_dispute_asks_before_acting(client: FlaskClient, poster: User, donor: User) -> None:
    first = add_gift(add_post(poster), donor, 2_000)
    second = add_gift(first.post, donor, 500)
    login_as(client, poster)
    page = client.get(f"/gifts?dispute={first.id}").get_data(as_text=True)
    assert "Dispute this gift? dev_tom won't get credit for $20." in page
    assert f'action="/gifts/{first.id}/dispute"' in page
    assert f'action="/gifts/{first.id}/confirm"' not in page
    assert f'href="/gifts#gift-{first.id}">Cancel</a>' in page
    assert f'action="/gifts/{second.id}/confirm"' in page
    assert first.status is DonationStatus.PENDING


def test_empty_states(client: FlaskClient, poster: User) -> None:
    login_as(client, poster)
    page = client.get("/gifts").get_data(as_text=True)
    assert "To confirm" not in page
    assert "No gifts yet." in page


def test_confirm_counts_toward_progress(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    gift = add_gift(post, donor, 2_000)
    login_as(client, poster)
    resp = resolve(client, gift)
    assert resp.location == "/gifts"
    assert gift.status is DonationStatus.CONFIRMED
    assert gift.resolved_at is not None
    assert (post.raised_cents, post.status) == (2_000, PostStatus.OPEN)
    assert "Confirmed $20 from dev_tom." in client.get("/gifts").get_data(as_text=True)


def test_dispute_does_not_count(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    gift = add_gift(post, donor)
    login_as(client, poster)
    assert resolve(client, gift, "dispute").location == "/gifts"
    assert gift.status is DonationStatus.DISPUTED
    assert gift.resolved_at is not None
    assert post.raised_cents == 0
    assert "Marked $20 from dev_tom as not received." in client.get("/gifts").get_data(as_text=True)


def test_confirm_reaching_goal_funds_post(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster, goal_cents=5_000)
    add_gift(post, donor, 3_000, DonationStatus.CONFIRMED)
    gift = add_gift(post, donor, 2_000)
    login_as(client, poster)
    resolve(client, gift)
    assert post.status is PostStatus.FUNDED
    assert "&#34;Rent&#34; is fully funded!" in client.get("/gifts").get_data(as_text=True)
    assert "Rent" not in client.get("/").get_data(as_text=True)


def test_confirm_on_closed_post_keeps_status(
    client: FlaskClient, poster: User, donor: User
) -> None:
    post = add_post(poster, goal_cents=1_000)
    gift = add_gift(post, donor, 1_000)
    post.status = PostStatus.CLOSED
    db.session.commit()
    login_as(client, poster)
    resolve(client, gift)
    assert gift.status is DonationStatus.CONFIRMED
    assert post.status is PostStatus.CLOSED


@pytest.mark.parametrize("who", ["donor", "stranger"])
def test_only_recipient_can_resolve(
    client: FlaskClient, poster: User, donor: User, make_user: MakeUser, who: str
) -> None:
    gift = add_gift(add_post(poster), donor)
    login_as(client, donor if who == "donor" else make_user("lee_w"))
    assert resolve(client, gift).status_code == 404
    assert gift.status is DonationStatus.PENDING


@pytest.mark.parametrize(
    "path", ["/gifts/999/confirm", f"/gifts/{2**31}/dispute", "/gifts/1/approve"]
)
def test_unknown_gift_or_action(client: FlaskClient, poster: User, donor: User, path: str) -> None:
    add_gift(add_post(poster), donor)
    login_as(client, poster)
    assert client.post(path).status_code == 404


def test_already_handled(client: FlaskClient, poster: User, donor: User) -> None:
    gift = add_gift(add_post(poster), donor, status=DonationStatus.CONFIRMED)
    login_as(client, poster)
    assert resolve(client, gift, "dispute").location == "/gifts"
    assert gift.status is DonationStatus.CONFIRMED
    assert "That gift was already handled." in client.get("/gifts").get_data(as_text=True)


def test_nav_badge_counts_gifts_waiting(client: FlaskClient, poster: User, donor: User) -> None:
    post = add_post(poster)
    first = add_gift(post, donor)
    add_gift(post, donor, 500)
    login_as(client, poster)
    assert 'aria-label="2 to confirm">2</span>' in client.get("/").get_data(as_text=True)
    resolve(client, first)
    assert 'aria-label="1 to confirm">1</span>' in client.get("/").get_data(as_text=True)


def test_no_badge_for_the_donor(client: FlaskClient, poster: User, donor: User) -> None:
    add_gift(add_post(poster), donor)
    login_as(client, donor)
    page = client.get("/").get_data(as_text=True)
    assert 'href="/gifts">Gifts</a>' in page
    assert 'class="badge"' not in page


def test_no_gifts_link_when_logged_out(client: FlaskClient) -> None:
    assert 'href="/gifts"' not in client.get("/").get_data(as_text=True)
