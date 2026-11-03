import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError

from app import create_app
from app.extensions import db
from app.models import Post, utcnow
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


def csrf_app() -> Flask:
    app = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "SERVER_NAME": "localhost"}
    )
    with app.app_context():
        db.create_all()
    return app


def test_stale_form_goes_back_with_a_message() -> None:
    client = csrf_app().test_client()
    with client.session_transaction() as session:
        session["seen"] = True
    response = client.post(
        "/login",
        data={"identifier": "a", "password": "b"},
        headers={"Referer": "http://localhost/rules"},
    )
    assert response.status_code == 302
    assert response.location.endswith("/rules")
    assert "gone stale" in client.get("/rules").get_data(as_text=True)


def test_no_session_explains_and_links_back() -> None:
    response = (
        csrf_app()
        .test_client()
        .post("/login", data={}, headers={"Referer": "http://localhost/rules"})
    )
    page = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "Your session ended" in page
    assert 'href="/rules">Go back' in page


@pytest.mark.parametrize(
    "referrer",
    [
        "https://evil.example/phish",  # another site
        "http://[bad",  # unparseable
        "http://localhost/posts/1/gifts",  # POST-only, so a redirect would be a 405
        "http://localhost/no-such-page",
    ],
)
def test_stale_form_only_goes_back_to_a_real_page(referrer: str) -> None:
    client = csrf_app().test_client()
    with client.session_transaction() as session:
        session["seen"] = True
    response = client.post("/login", data={}, headers={"Referer": referrer})
    assert response.location.endswith("/")
    assert "evil.example" not in response.location


def test_stale_form_handles_a_page_that_redirects() -> None:
    app = csrf_app()

    @app.get("/slash/")
    def slash() -> str:
        return "ok"

    client = app.test_client()
    with client.session_transaction() as session:
        session["seen"] = True
    response = client.post("/login", data={}, headers={"Referer": "http://localhost/slash"})
    assert response.location.endswith("/slash")


def test_wrong_method_keeps_the_allow_header(client: FlaskClient) -> None:
    assert "GET" in client.delete("/").headers["Allow"]


def test_server_error_page_survives_a_broken_database(
    make_user: MakeUser, app: Flask, monkeypatch: pytest.MonkeyPatch
) -> None:
    user = make_user()
    app.config.update(TESTING=False, PROPAGATE_EXCEPTIONS=False)

    @app.errorhandler(ValueError)
    def boom(_: ValueError) -> str:
        raise RuntimeError

    def broken(*_: object, **__: object) -> None:
        raise OperationalError("SELECT", {}, Exception("database is down"))

    client = app.test_client()
    login_as(client, user)
    monkeypatch.setattr(db.session, "scalar", broken)
    monkeypatch.setattr(db.session, "get", broken)
    response = client.get("/gifts")
    assert response.status_code == 500
    assert "Something went wrong on our end" in response.get_data(as_text=True)


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


def test_need_or_want_error_is_focused_and_linked(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user(venmo_handle="@maria-g", rules_accepted_at=utcnow()))
    page = client.post(
        "/posts/new", data={"title": "Phone bill", "body": "Need it for work.", "goal": "20"}
    ).get_data(as_text=True)
    assert 'id="kind-error"' in page
    assert 'aria-describedby="kind-error"' in page
    assert "autofocus" in page


def test_same_post_twice_makes_one_post(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user(venmo_handle="@maria-g", rules_accepted_at=utcnow()))
    form = {"kind": "need", "title": "Phone bill", "body": "Need it for work.", "goal": "20"}
    first = client.post("/posts/new", data=form)
    second = client.post("/posts/new", data=form)
    assert second.location == first.location
    assert db.session.scalar(select(func.count()).select_from(Post)) == 1
    other = client.post("/posts/new", data={**form, "title": "Water bill"})
    assert other.location != first.location
