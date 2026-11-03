from flask.testing import FlaskClient

from app import create_app
from app.extensions import db
from tests.conftest import MakeUser, login_as


def test_missing_page_is_styled(client: FlaskClient) -> None:
    response = client.get("/no-such-page")
    page = response.get_data(as_text=True)
    assert response.status_code == 404
    assert "We can&#39;t find that page" in page
    assert 'class="topbar"' in page


def test_wrong_method_is_styled(client: FlaskClient) -> None:
    response = client.delete("/")
    assert response.status_code == 405
    assert "That action isn&#39;t available" in response.get_data(as_text=True)


def test_routing_redirects_are_not_treated_as_errors() -> None:
    app = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "SERVER_NAME": "localhost"}
    )

    @app.get("/slash/")
    def slash() -> str:
        return "ok"

    response = app.test_client().get("/slash")
    assert response.status_code == 308
    assert response.location.endswith("/slash/")


def test_server_error_page_stands_alone() -> None:
    app = create_app(
        {"TESTING": False, "SQLALCHEMY_DATABASE_URI": "sqlite://", "SERVER_NAME": "localhost"}
    )

    @app.get("/boom")
    def boom() -> str:
        raise RuntimeError

    with app.app_context():
        db.create_all()
    response = app.test_client().get("/boom")
    page = response.get_data(as_text=True)
    assert response.status_code == 500
    assert "Something went wrong on our end" in page


def test_stale_form_goes_back_with_a_message() -> None:
    app = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "SERVER_NAME": "localhost"}
    )
    with app.app_context():
        db.create_all()
    client = app.test_client()
    response = client.post(
        "/login",
        data={"identifier": "a", "password": "b"},
        headers={"Referer": "http://localhost/rules"},
    )
    assert response.status_code == 302
    assert response.location.endswith("/rules")
    assert "gone stale" in client.get("/rules").get_data(as_text=True)


def test_stale_form_never_redirects_off_site() -> None:
    app = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "SERVER_NAME": "localhost"}
    )
    with app.app_context():
        db.create_all()
    response = app.test_client().post(
        "/login", data={}, headers={"Referer": "https://evil.example/phish"}
    )
    assert "evil.example" not in response.location


def test_skip_link_and_named_nav(client: FlaskClient) -> None:
    page = client.get("/").get_data(as_text=True)
    assert 'href="#main">Skip to content' in page
    assert '<nav aria-label="Main">' in page
    assert 'id="main"' in page


def test_field_errors_are_focused_and_labels_stay_clean(client: FlaskClient) -> None:
    page = client.post("/login", data={"identifier": "", "password": ""}).get_data(as_text=True)
    assert '<label for="identifier">Username or email</label>' in page
    assert "autofocus" in page


def test_post_form_guards_against_double_submit(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user(venmo_handle="@maria-g"))
    page = client.get("/posts/new").get_data(as_text=True)
    assert "data-once" in page
    assert "js/once.js" in page


def test_unverified_profile_hides_the_public_link(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user(verified=False))
    assert "View your public profile" not in client.get("/profile").get_data(as_text=True)
