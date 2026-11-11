import re

from flask.testing import FlaskClient

from tests.conftest import MakeUser, login_as


def visible_text(page: str) -> str:
    return re.sub(r"<[^>]+>", " ", page)


def test_new_visitors_get_the_story(client: FlaskClient) -> None:
    page = client.get("/").get_data(as_text=True)
    assert '<a class="home-door home-door-help" href="#help">' in page
    assert '<a class="home-door home-door-ask" href="#ask">' in page
    assert "Pay My Bill never holds your money." in page
    assert page.count('<figcaption class="home-example">Example</figcaption>') == 7
    assert 'aria-current="page"' not in page.split('aria-label="Main"')[1].split("</nav>")[0]


def test_story_ends_at_a_working_signup_form(client: FlaskClient) -> None:
    page = client.get("/").get_data(as_text=True)
    join = page.split('id="join"')[1]
    assert '<form method="post" action="/signup"' in join
    assert 'name="adult"' in join
    assert 'href="/feed">Browse the feed first</a>' in join


def test_story_never_says_donor_or_donation(client: FlaskClient) -> None:
    text = visible_text(client.get("/").get_data(as_text=True)).lower()
    assert "donor" not in text
    assert "donation" not in text
    assert "charity" not in text


def test_logged_in_users_go_to_the_feed(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("maria_g"))
    assert client.get("/").location == "/feed"


def test_old_feed_links_keep_working(client: FlaskClient) -> None:
    assert client.get("/?kind=need&n=2&x=1").location == "/feed?kind=need&n=2"
    assert client.get("/?n=3").location == "/feed?n=3"


def test_tracking_tags_still_show_the_story(client: FlaskClient) -> None:
    assert client.get("/?utm_source=x&fbclid=y").status_code == 200


def test_logged_out_top_bar_has_a_filled_sign_up(client: FlaskClient) -> None:
    assert '<a class="btn topbar-signup" href="#join">Sign up</a>' in client.get("/").get_data(
        as_text=True
    )
    page = client.get("/feed").get_data(as_text=True)
    assert '<a class="btn topbar-signup" href="/signup">Sign up</a>' in page


def test_feed_is_open_to_everyone(client: FlaskClient) -> None:
    assert client.get("/feed").status_code == 200


def test_brand_goes_home(client: FlaskClient) -> None:
    assert '<a class="brand" href="/">Pay My Bill</a>' in client.get("/feed").get_data(as_text=True)
