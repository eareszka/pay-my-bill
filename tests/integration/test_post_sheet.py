from datetime import timedelta

from flask.testing import FlaskClient

from app.accounts import anonymize
from app.extensions import db
from app.models import (
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    PostCategory,
    PostKind,
    PostStatus,
    User,
    utcnow,
)
from tests.conftest import MakeUser, login_as

BIO = "Night-shift nurse and a dad of two. I pay it forward when I can."


def make_post(user: User, title: str = "Power bill") -> Post:
    post = Post(
        user=user,
        kind=PostKind.NEED,
        category=PostCategory.BILLS,
        title=title,
        body="The power bill came in high this month.",
        goal_cents=8_000,
        photo_key="posts/" + "a" * 32 + ".webp",
        more_photo_keys=["posts/" + c * 32 + ".webp" for c in "bcde"],
    )
    db.session.add(post)
    db.session.commit()
    return post


def test_bio_is_saved_and_shown(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user()
    login_as(client, user)
    resp = client.post("/profile", data={"state": "", "bio": f"  {BIO}  "}, follow_redirects=True)
    assert b"Profile saved." in resp.data
    assert user.bio == BIO
    assert BIO in client.get("/profile").get_data(as_text=True)
    assert f'<p class="profile-bio">{BIO}</p>' in client.get("/u/alice").get_data(as_text=True)
    client.post("/profile", data={"state": "", "bio": ""})
    assert user.bio is None


def test_bio_refuses_fundraising_and_long_text(client: FlaskClient, make_user: MakeUser) -> None:
    user = make_user()
    login_as(client, user)
    page = client.post("/profile", data={"state": "", "bio": "Raising seed money for my startup"})
    assert "Keep it about you." in page.get_data(as_text=True)
    page = client.post("/profile", data={"state": "", "bio": "x" * 301})
    assert "Up to 300 characters." in page.get_data(as_text=True)
    assert user.bio is None


def test_deleting_an_account_clears_the_bio(make_user: MakeUser) -> None:
    user = make_user(bio=BIO)
    anonymize(user)
    assert user.bio is None


def test_sheet_shows_the_whole_person_in_order(client: FlaskClient, make_user: MakeUser) -> None:
    poster = make_user("maria_g", bio=BIO, city="Tampa", state="FL")
    # The recipient is older than 3 days, so the poster's gift counts (T2).
    donor = make_user("dev_tom", created_at=utcnow() - timedelta(days=10))
    post = make_post(poster)
    earlier = make_post(donor, title="Car battery")
    db.session.add(
        Donation(
            post=earlier,
            donor=poster,
            amount_cents=2_000,
            method=PaymentMethod.VENMO,
            status=DonationStatus.CONFIRMED,
        )
    )
    db.session.commit()
    login_as(client, donor)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    order = [
        'class="hero-photo"',
        post.body,
        '<span aria-hidden="true">💡</span> Bills and utilities',
        '<span aria-hidden="true">🙏</span> Need',
        '<span aria-hidden="true">🎯</span> Goal $80',
        '<span aria-hidden="true">📍</span> Tampa, FL',
        "Photo 2 from maria_g",
        'class="poster-card"',
        BIO,
        '<span aria-hidden="true">⭐</span> Level 1',
        '<span aria-hidden="true">🤝</span> 1 person helped',
        '<span aria-hidden="true">📅</span> Joined',
        "Photo 3 from maria_g",
        "Photo 5 from maria_g",
        f'href="/posts/{post.id}/chat" aria-label="Chat with maria_g"',
        f'href="/posts/{post.id}/chip-in" aria-label="Chip in"',
    ]
    assert 'id="chip-in"' not in page
    spots = [page.index(text) for text in order]
    assert spots == sorted(spots)


def test_no_chip_in_button_for_the_poster(client: FlaskClient, make_user: MakeUser) -> None:
    poster = make_user("maria_g")
    post = make_post(poster)
    login_as(client, poster)
    page = client.get(f"/posts/{post.id}").get_data(as_text=True)
    assert 'class="poster-card"' in page
    assert "chip-fab" not in page


def test_chip_in_and_chat_are_their_own_pages(client: FlaskClient, make_user: MakeUser) -> None:
    poster = make_user("maria_g")
    post = make_post(poster)
    login_as(client, make_user("dev_tom"))
    chip_in = client.get(f"/posts/{post.id}/chip-in").get_data(as_text=True)
    assert 'id="chip-in"' in chip_in
    assert "Chip in to maria_g" in chip_in
    assert f'href="/posts/{post.id}">' in chip_in
    chat = client.get(f"/posts/{post.id}/chat").get_data(as_text=True)
    assert "Chat is coming soon" in chat
    assert "<textarea" in chat and " disabled" in chat
    assert "<form" not in chat.split('class="chat"')[1]


def test_poster_has_no_chip_in_or_chat_page(client: FlaskClient, make_user: MakeUser) -> None:
    poster = make_user("maria_g")
    post = make_post(poster)
    login_as(client, poster)
    assert client.get(f"/posts/{post.id}/chip-in").status_code == 404
    assert client.get(f"/posts/{post.id}/chat").status_code == 404


def test_hidden_post_has_no_chip_in_or_chat_page(client: FlaskClient, make_user: MakeUser) -> None:
    post = make_post(make_user("maria_g"))
    post.status = PostStatus.REMOVED
    db.session.commit()
    login_as(client, make_user("dev_tom"))
    assert client.get(f"/posts/{post.id}/chip-in").status_code == 404
    assert client.get(f"/posts/{post.id}/chat").status_code == 404
