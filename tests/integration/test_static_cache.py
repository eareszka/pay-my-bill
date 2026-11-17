import re

from flask import Flask, flash
from flask.testing import FlaskClient

from app.static_cache import YEAR, file_hash, version_of
from tests.conftest import MakeUser, login_as


def css_href(page: str) -> str:
    match = re.search(r'href="(/static/css/app\.css\?v=[0-9a-f]{12})"', page)
    assert match, "app.css should carry a version"
    return match.group(1)


def test_static_urls_carry_the_file_hash(app: Flask, client: FlaskClient) -> None:
    href = css_href(client.get("/how/help").get_data(as_text=True))
    assert href.endswith(str(version_of(app, "css/app.css")))
    page = client.get("/how/help").get_data(as_text=True)
    assert 'href="/static/fonts/public-sans-400.woff2"' in page


def test_current_version_is_kept_for_a_year(client: FlaskClient) -> None:
    resp = client.get(css_href(client.get("/how/help").get_data(as_text=True)))
    assert resp.status_code == 200
    assert resp.cache_control.max_age == YEAR
    assert resp.cache_control.immutable
    assert not resp.cache_control.no_cache


def test_old_or_missing_version_revalidates(client: FlaskClient) -> None:
    for url in ("/static/css/app.css?v=000000000000", "/static/css/app.css"):
        resp = client.get(url)
        assert resp.cache_control.no_cache
        assert resp.cache_control.max_age != YEAR


def test_missing_files_have_no_version(app: Flask) -> None:
    assert file_hash(str(app.static_folder), "nope.css") is None
    with app.test_request_context():
        from flask import url_for

        assert url_for("static", filename="nope.css") == "/static/nope.css"


def test_debug_rehashes_every_time(app: Flask) -> None:
    app.debug = True
    assert version_of(app, "css/app.css") == version_of(app, "css/app.css")


def test_story_step_is_kept_briefly_and_fetches_neighbors(client: FlaskClient) -> None:
    resp = client.get("/how/help/2")
    assert resp.cache_control.private
    assert resp.cache_control.max_age == 60
    page = resp.get_data(as_text=True)
    assert '<link rel="prefetch" href="/how/help/3">' in page
    assert '<link rel="prefetch" href="/how/help">' in page
    assert "js/prefetch.js" in page


def test_first_and_last_steps_prefetch_home_and_skip_signup(client: FlaskClient) -> None:
    first = client.get("/how/ask").get_data(as_text=True)
    assert '<link rel="prefetch" href="/">' in first
    last = client.get("/how/ask/3").get_data(as_text=True)
    assert '<link rel="prefetch" href="/how/ask/2">' in last
    assert 'rel="prefetch" href="/signup' not in last


def test_home_prefetches_both_stories(client: FlaskClient) -> None:
    resp = client.get("/")
    assert resp.cache_control.max_age == 60
    page = resp.get_data(as_text=True)
    assert '<link rel="prefetch" href="/how/help">' in page
    assert '<link rel="prefetch" href="/how/ask">' in page


def test_logged_in_story_is_not_kept(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("maria_g"))
    resp = client.get("/how/help/2")
    assert resp.cache_control.max_age is None
    assert "prefetch" not in resp.get_data(as_text=True)


def test_page_with_a_flash_is_not_kept(app: Flask, client: FlaskClient) -> None:
    @app.get("/test-flash")
    def flash_then_home() -> str:
        flash("You're logged out.", "info")
        return "ok"

    client.get("/test-flash")
    resp = client.get("/how/help")
    assert "logged out" in resp.get_data(as_text=True)
    assert resp.cache_control.max_age is None


def test_other_pages_have_no_prefetch(client: FlaskClient) -> None:
    page = client.get("/feed").get_data(as_text=True)
    assert 'rel="prefetch"' not in page
    assert "prefetch.js" not in page
