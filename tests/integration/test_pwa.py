import json

from flask.testing import FlaskClient

from tests.conftest import MakeUser, login_as


def test_manifest_describes_the_installed_app(client: FlaskClient) -> None:
    resp = client.get("/manifest.webmanifest")
    assert resp.status_code == 200
    assert resp.mimetype == "application/manifest+json"
    assert "no-cache" in resp.headers["Cache-Control"]
    manifest = json.loads(resp.data)
    assert (manifest["display"], manifest["start_url"], manifest["scope"]) == (
        "standalone",
        "/",
        "/",
    )
    assert manifest["background_color"] == manifest["theme_color"] == "#0a0a0a"
    for icon in manifest["icons"]:
        assert client.get(icon["src"]).status_code == 200
    assert any(icon.get("purpose") == "maskable" for icon in manifest["icons"])


def test_service_worker_is_served_from_the_root(client: FlaskClient) -> None:
    resp = client.get("/sw.js")
    assert resp.status_code == 200
    assert resp.mimetype == "text/javascript"
    assert "no-cache" in resp.headers["Cache-Control"]
    script = resp.get_data(as_text=True)
    assert '"/offline"' in script
    for path in ("/static/css/app.css", "/static/fonts/league-gothic-400.woff2"):
        assert f'"{path}"' in script
        assert client.get(path).status_code == 200


def test_offline_page_never_shows_who_is_logged_in(
    client: FlaskClient, make_user: MakeUser
) -> None:
    login_as(client, make_user("maria_g"))
    page = client.get("/offline").get_data(as_text=True)
    assert "You're offline" in page
    assert '<a class="btn" href="">Try again</a>' in page
    assert "maria_g" not in page


def test_pages_link_the_manifest_and_home_screen_icon(client: FlaskClient) -> None:
    page = client.get("/rules").get_data(as_text=True)
    assert '<link rel="manifest" href="/manifest.webmanifest">' in page
    assert 'rel="apple-touch-icon" href="/static/icons/apple-touch-icon.png"' in page
    assert 'name="apple-mobile-web-app-title" content="Pay My Bill"' in page
    assert "/static/js/pwa.js" in page
