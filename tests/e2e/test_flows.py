"""The main ways through Yearnly, driven in a real browser at phone and desktop sizes (#207).

Every page along the way gets a full-page screenshot and the design checks; a test fails if
the flow breaks or if any check finds something.
"""

import pytest
from playwright.sync_api import expect
from sqlalchemy import select

from app.extensions import db
from app.models import Post, PostStatus, User
from tests.e2e.checks import assert_clean, long_motion
from tests.e2e.conftest import LiveServer, Ui, UiFactory

pytestmark = pytest.mark.e2e


def open_post_by_someone_else(live_server: LiveServer) -> int:
    """A seeded open post whose poster takes app payments."""
    with live_server.app.app_context():
        post = db.session.scalars(
            select(Post)
            .join(User, Post.user_id == User.id)
            .where(Post.status == PostStatus.OPEN, User.venmo_handle.is_not(None))
            .order_by(Post.id)
        ).first()
        assert post is not None, "the seed should have an open post with a Venmo handle"
        return post.id


def test_front_door(ui: Ui) -> None:
    ui.goto("/")
    page = ui.page
    expect(page.locator(".home-door-help")).to_be_visible()
    expect(page.locator(".home-door-ask")).to_be_visible()
    # The front door offers only Sign up and Log in (#196), with no top bar (#205).
    expect(page.locator(".home-signup")).to_have_text("Sign up")
    expect(page.locator(".home-login a")).to_have_text("Log in")
    ui.check("doors")
    assert_clean(ui)


def test_how_it_works_stories(ui: Ui) -> None:
    for path in ("help", "ask"):
        ui.goto("/")
        ui.page.click(f".home-door-{path}")
        ui.settle()
        for step in (1, 2, 3):
            suffix = f"/how/{path}" + (f"/{step}" if step > 1 else "")
            assert ui.page.url.rstrip("/").endswith(suffix), ui.page.url
            ui.check(f"{path}-step{step}")
            if step < 3:
                ui.goto(f"/how/{path}/{step + 1}")
    assert_clean(ui)


def test_sign_up(ui: Ui, device: str) -> None:
    ui.goto("/signup")
    ui.check("form")
    page = ui.page
    name = f"newbie_{device}"
    page.fill("#username", name)
    page.fill("#email", f"{name}@example.com")
    page.fill("#password", "a-long-enough-password")
    page.fill("#confirm", "a-long-enough-password")
    page.check("#adult")
    page.click("form button[type=submit]")
    ui.settle()
    assert "/verify/pending" in page.url, page.url
    ui.check("verify-pending")
    assert_clean(ui)


def test_sign_up_errors(ui: Ui) -> None:
    ui.goto("/signup")
    ui.page.click("form button[type=submit]")
    ui.settle()
    expect(ui.page.locator(".error").first).to_be_visible()
    ui.check("errors")
    assert_clean(ui)


def test_log_in_to_the_feed(ui: Ui, live_server: LiveServer) -> None:
    user = live_server.make_user()
    ui.goto("/login")
    ui.check("form")
    ui.login(user)
    assert "/feed" in ui.page.url, ui.page.url
    ui.check("feed")
    # Logged in, the front door sends you on to the feed.
    ui.goto("/")
    assert "/feed" in ui.page.url
    assert_clean(ui)


def test_create_a_post(ui: Ui, live_server: LiveServer) -> None:
    user = live_server.make_user("poster")
    ui.login(user)
    ui.goto("/posts/new")
    ui.check("form")
    page = ui.page
    page.check("input[name=kind][value=need]")
    page.fill("#title", "Help with the power bill")
    page.fill("#body", "The power bill came in higher than usual this month.")
    page.fill("#goal", "80")
    page.click("form.page-form button[type=submit]")
    ui.settle()
    expect(page.locator("h1")).to_contain_text("Help with the power bill")
    ui.check("detail")
    assert_clean(ui)


def test_chip_in_with_an_app(ui: Ui, live_server: LiveServer) -> None:
    donor = live_server.make_user("donor")
    post_id = open_post_by_someone_else(live_server)
    ui.login(donor)
    ui.goto(f"/posts/{post_id}")
    page = ui.page
    # Stripe is off in e2e, so the pay-app path is the one shown.
    expect(page.locator("form.chip-in")).to_be_visible()
    ui.check("chip-in")
    page.fill("#chip-amount", "15")
    # The first option is the "Choose app" placeholder; pick the first real app.
    first_app = page.locator("#method option:not([value=''])").first.get_attribute("value")
    page.select_option("#method", first_app)
    page.click("form.chip-in .sent-row button[type=submit]")
    ui.settle()
    expect(page.locator("[data-gift-recorded]")).to_be_visible()
    ui.check("gift-recorded")
    assert_clean(ui)


def test_chip_in_logged_out(ui: Ui, live_server: LiveServer) -> None:
    ui.goto(f"/posts/{open_post_by_someone_else(live_server)}")
    expect(ui.page.locator("#chip-in")).to_be_visible()
    ui.check("chip-in")
    assert_clean(ui)


def test_your_pages(ui: Ui, live_server: LiveServer) -> None:
    user = live_server.make_user("you")
    ui.login(user)
    for step, path in [
        ("profile", f"/u/{user}"),
        ("gifts", "/gifts"),
        ("settings", "/profile"),
        ("leaders", "/leaders"),
    ]:
        ui.goto(path)
        ui.check(step)
    assert_clean(ui)


def test_public_pages(ui: Ui) -> None:
    for step, path in [
        ("rules", "/rules"),
        ("terms", "/terms"),
        ("privacy", "/privacy"),
        ("reset", "/reset"),
        ("not-found", "/no-such-page"),
    ]:
        ui.goto(path)
        ui.check(step)
    assert_clean(ui)


def test_arrival_respects_reduced_motion(make_ui: UiFactory) -> None:
    ui = make_ui(reduced_motion="reduce")
    ui.page.goto(ui.base + "/")
    # Measure while the arrival would still be running, then again once it's settled.
    ui.page.wait_for_timeout(100)
    early = long_motion(ui.page)
    ui.settle()
    ui.check("arrival-reduced", focus=False, extra=early)
    assert_clean(ui)
