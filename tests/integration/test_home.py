import re

import pytest
from flask.testing import FlaskClient

from tests.conftest import MakeUser, login_as

STORIES = [("help", 4, "/how/ask"), ("ask", 3, "/how/help")]


def visible_text(page: str) -> str:
    return re.sub(r"<[^>]+>", " ", page)


def step_url(path: str, step: int) -> str:
    return f"/how/{path}" + (f"/{step}" if step > 1 else "")


def page_at(client: FlaskClient, url: str) -> str:
    return client.get(url).get_data(as_text=True)


def test_new_visitors_get_just_the_two_doors(client: FlaskClient) -> None:
    page = page_at(client, "/")
    assert '<a class="home-door home-door-help" href="/how/help">' in page
    assert '<a class="home-door home-door-ask" href="/how/ask">' in page
    assert "Pay My Bill never holds your money." in page
    assert "how-step" not in page
    assert 'aria-current="page"' not in page.split('aria-label="Main"')[1].split("</nav>")[0]


@pytest.mark.parametrize(("path", "total", "other"), STORIES)
def test_each_story_goes_one_step_at_a_time(
    client: FlaskClient, path: str, total: int, other: str
) -> None:
    assert client.get(f"/how/{path}/1").location.endswith(f"/how/{path}")
    assert '<a class="how-back" href="/">' in page_at(client, f"/how/{path}")
    for step in range(1, total + 1):
        page = page_at(client, step_url(path, step))
        assert page.count('<figcaption class="how-example">Example</figcaption>') == 1
        assert page.count('<li class="on">') == step
        assert f'<a class="how-other how-other-{other[5:]}" href="{other}">' in page
        if step < total:
            assert f'href="/how/{path}/{step + 1}">Next' in page
        else:
            assert f'href="/how/{path}/{total - 1}"><svg' in page


@pytest.mark.parametrize(("path", "total", "other"), STORIES)
def test_each_story_ends_on_sign_up_or_the_other_story(
    client: FlaskClient, path: str, total: int, other: str
) -> None:
    page = page_at(client, f"/how/{path}/{total}")
    assert f'<a class="btn how-end" href="/signup?from={path}">Sign up</a>' in page
    assert f'href="{other}">' in page
    assert "Or see how" in page
    assert "Next<svg" not in page


def test_a_logged_in_reader_ends_at_the_feed(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("maria_g"))
    page = page_at(client, "/how/ask/3")
    assert '<a class="btn how-end" href="/feed">Go to the feed</a>' in page


@pytest.mark.parametrize("url", ["/how/help/0", "/how/help/5", "/how/ask/4", "/how/give"])
def test_steps_outside_a_story_are_not_found(client: FlaskClient, url: str) -> None:
    assert client.get(url).status_code == 404


def test_stories_never_say_donor_or_donation(client: FlaskClient) -> None:
    for path, total, _ in STORIES:
        for step in range(1, total + 1):
            text = visible_text(page_at(client, step_url(path, step))).lower()
            assert "donor" not in text
            assert "donation" not in text
            assert "charity" not in text


def test_logged_in_users_go_to_the_feed(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("maria_g"))
    assert client.get("/").location == "/feed"


def test_old_feed_links_keep_working(client: FlaskClient) -> None:
    assert client.get("/?kind=need&n=2&x=1").location == "/feed?kind=need&n=2"
    assert client.get("/?n=3").location == "/feed?n=3"


def test_tracking_tags_still_show_the_doors(client: FlaskClient) -> None:
    assert client.get("/?utm_source=x&fbclid=y").status_code == 200


def test_logged_out_top_bar_has_a_filled_sign_up(client: FlaskClient) -> None:
    for url in ("/", "/feed", "/how/help"):
        assert '<a class="btn topbar-signup" href="/signup">Sign up</a>' in page_at(client, url)


def test_feed_is_open_to_everyone(client: FlaskClient) -> None:
    assert client.get("/feed").status_code == 200


def test_brand_goes_home(client: FlaskClient) -> None:
    assert '<a class="brand" href="/">Pay My Bill</a>' in page_at(client, "/feed")


@pytest.mark.parametrize(("path", "total", "other"), STORIES)
def test_sign_up_from_a_story_keeps_the_way_back(
    client: FlaskClient, path: str, total: int, other: str
) -> None:
    page = page_at(client, f"/signup?from={path}")
    assert f'<a class="how-other how-other-{path} join-back" href="/how/{path}/{total}">' in page
    assert other not in page.split("join-back")[1].split("</a>")[0]


def test_sign_up_ignores_an_unknown_story(client: FlaskClient) -> None:
    assert "join-back" not in page_at(client, "/signup?from=elsewhere")
