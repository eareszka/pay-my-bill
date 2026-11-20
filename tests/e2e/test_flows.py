"""The main ways through Yearnly, driven in a real browser at phone and desktop sizes (#207).

Every page along the way gets a full-page screenshot and the design checks; a test fails if
the flow breaks or if any check finds something.
"""

import re

import pytest
from playwright.sync_api import Route, expect
from sqlalchemy import select

from app.extensions import db
from app.models import Post, PostStatus, User
from tests.conftest import jpeg
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
            expect(ui.page).to_have_url(re.compile(re.escape(suffix) + "/?$"))
            # Sign up and Log in stay on screen on every step (2026-11-16).
            expect(ui.page.locator(".how-way-in .home-signup")).to_be_in_viewport()
            expect(ui.page.locator(".how-way-in .home-login a")).to_be_in_viewport()
            ui.check(f"{path}-step{step}")
            if step < 3:
                ui.goto(f"/how/{path}/{step + 1}")
    assert_clean(ui)


def test_sign_up(ui: Ui, size: str) -> None:
    ui.goto("/signup")
    ui.check("form")
    page = ui.page
    name = f"newbie_{size}"
    page.fill("#username", name)
    page.fill("#email", f"{name}@example.com")
    page.fill("#password", "a-long-enough-password")
    page.fill("#confirm", "a-long-enough-password")
    page.check("#adult")
    ui.submit("form:has(#username) button[type=submit]")
    expect(page).to_have_url(re.compile("/verify/pending"))
    ui.check("verify-pending")
    assert_clean(ui)


def test_sign_up_from_each_story(ui: Ui) -> None:
    # Arriving from a How story, sign-up keeps that story's tail and the way back (#208).
    for story in ("help", "ask"):
        ui.goto(f"/signup?from={story}")
        expect(ui.page.locator("form button[type=submit]")).to_be_visible()
        ui.check(f"from-{story}")
    assert_clean(ui)


def test_sign_up_errors(ui: Ui) -> None:
    ui.goto("/signup")
    ui.submit("form:has(#username) button[type=submit]")
    expect(ui.page.locator(".error").first).to_be_visible()
    ui.check("errors")
    assert_clean(ui)


def test_log_in_to_the_feed(ui: Ui, live_server: LiveServer) -> None:
    user = live_server.make_user()
    ui.goto("/login")
    ui.check("form")
    ui.login(user)
    expect(ui.page).to_have_url(re.compile("/feed"))
    ui.check("feed")
    # Logged in, the front door sends you on to the feed.
    ui.goto("/")
    expect(ui.page).to_have_url(re.compile("/feed"))
    assert_clean(ui)


def test_log_in_with_a_wrong_password(ui: Ui, live_server: LiveServer) -> None:
    user = live_server.make_user("typo")
    ui.login(user, password="not-the-password")  # noqa: S106 - a deliberately wrong one
    expect(ui.page).to_have_url(re.compile("/login"))
    expect(ui.page.locator(".flash, .error").first).to_be_visible()
    ui.check("error")
    assert_clean(ui)


def test_reset_request_lands_on_log_in(ui: Ui, live_server: LiveServer) -> None:
    user = live_server.make_user("forgot")
    ui.goto("/reset")
    ui.page.fill("#email", f"{user}@example.com")
    ui.submit("form:has(#email) button[type=submit]")
    # The "check your email" message is a flash on the log-in page (#211 moved it).
    expect(ui.page).to_have_url(re.compile("/login"))
    expect(ui.page.locator(".flash").first).to_be_visible()
    ui.check("flash")
    assert_clean(ui)


def test_create_a_post(ui: Ui, live_server: LiveServer) -> None:
    user = live_server.make_user("poster")
    ui.login(user)
    ui.goto("/posts/new")
    ui.check("form")
    page = ui.page
    # One question per screen: picking an option moves on by itself, typed answers use Next.
    page.check("input[name=kind][value=need]")
    page.check("input[name=category][value=bills]")
    page.fill("#title", "Help with the power bill")
    page.click("[data-q-next]")
    page.fill("#body", "The power bill came in higher than usual this month.")
    page.click("[data-q-next]")
    page.fill("#goal", "80")
    page.click("[data-q-next]")
    page.locator("input[name=photos]").first.set_input_files(
        files=[{"name": "bill.jpg", "mimeType": "image/jpeg", "buffer": jpeg().getvalue()}]
    )
    expect(page.locator(".q-photo-box.has-file")).to_have_count(1)
    ui.check("photos")
    ui.submit("form:has(#title) button[type=submit]")
    expect(page.locator("h1")).to_contain_text("Help with the power bill")
    ui.check("detail")
    assert_clean(ui)


def test_chip_in_with_an_app(ui: Ui, live_server: LiveServer) -> None:
    donor = live_server.make_user("donor")
    post_id = open_post_by_someone_else(live_server)
    ui.login(donor)
    ui.goto(f"/posts/{post_id}")
    page = ui.page
    ui.check("post")
    # Chip in is its own page behind the round gift button (#295).
    page.click(".chip-fab")
    page.wait_for_url(re.compile(r"/posts/\d+/chip-in$"))
    # Stripe is off in e2e, so the pay-app path is the one shown.
    expect(page.locator("form.chip-in")).to_be_visible()
    ui.check("chip-in")
    page.fill("#chip-amount", "15")
    # The first option is the "Choose app" placeholder; pick the first real app.
    first_app = page.locator("#method option:not([value=''])").first.get_attribute("value")
    page.select_option("#method", first_app)
    ui.submit("form.chip-in .sent-row button[type=submit]")
    expect(page.locator("[data-gift-recorded]")).to_be_visible()
    ui.check("gift-recorded")
    assert_clean(ui)


def test_chip_in_logged_out(ui: Ui, live_server: LiveServer) -> None:
    ui.goto(f"/posts/{open_post_by_someone_else(live_server)}/chip-in")
    expect(ui.page.locator("#chip-in")).to_be_visible()
    ui.check("chip-in")
    assert_clean(ui)


def test_chat_mock(ui: Ui, live_server: LiveServer) -> None:
    ui.login(live_server.make_user("chatter"))
    ui.goto(f"/posts/{open_post_by_someone_else(live_server)}")
    ui.page.click(".sheet-chat")
    ui.page.wait_for_url(re.compile(r"/posts/\d+/chat$"))
    expect(ui.page.locator(".chat-compose textarea")).to_be_disabled()
    ui.check("chat")
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
    late = long_motion(ui.page)
    ui.check("arrival-reduced", focus=False, extra=early + late)
    assert_clean(ui)


def drag(ui: Ui, dx: float, dy: float) -> None:
    box = ui.page.locator(".deck > .deck-ticket").bounding_box()
    assert box is not None
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    mouse = ui.page.mouse
    mouse.move(x, y)
    mouse.down()
    mouse.move(x + dx, y + dy, steps=12)
    mouse.up()


def test_swipe_up_opens_the_post(ui: Ui, live_server: LiveServer) -> None:
    ui.login(live_server.make_user("swiper"))
    ui.goto("/feed")
    drag(ui, 0, -200)
    ui.page.wait_for_url(re.compile(r"/posts/\d+$"))
    expect(ui.page.locator(".post-hero")).to_be_attached()


def test_swipe_down_shows_less_of_that_kind(ui: Ui, live_server: LiveServer) -> None:
    ui.login(live_server.make_user("lesser"))
    # The first ticket is the follow-through pick, which always stays first, so it has no
    # Show less (#119 review); the second one does.
    ui.goto("/feed?n=2")
    category = ui.page.locator("form.show-less").get_attribute("data-category")
    drag(ui, 0, 200)
    ui.page.wait_for_url(re.compile(rf"undo={category}"))
    expect(ui.page.locator(".show-less-note")).to_be_visible()
    ui.check("show-less")


def test_small_lift_and_sideways_swipe_still_work(ui: Ui, live_server: LiveServer) -> None:
    ui.login(live_server.make_user("swiper"))
    ui.goto("/feed")
    drag(ui, 0, -30)
    assert ui.path() == "/feed"
    drag(ui, -260, 0)
    ui.page.wait_for_url(re.compile(r"/feed\?n=2"))


@pytest.mark.parametrize("size", ["mobile"])
def test_bars_stay_put_and_only_long_pages_scroll(ui: Ui, live_server: LiveServer) -> None:
    overflow = "() => document.body.scrollHeight - document.body.clientHeight"
    # Still pages fit and are locked: a drag never pans or bounces them, a pinch still zooms.
    locked = "() => ['overflowY', 'touchAction'].map(k => getComputedStyle(document.body)[k])"
    for path in ["/", *(f"/how/{story}/{step}" for story in ("help", "ask") for step in (1, 2, 3))]:
        ui.goto(path)
        assert ui.page.evaluate(overflow) <= 1, path
        assert ui.page.evaluate(locked) == ["hidden", "pinch-zoom"], path
    ui.login(live_server.make_user("still"))
    ui.goto("/feed")
    assert ui.page.evaluate(overflow) <= 1
    assert ui.page.evaluate(locked) == ["hidden", "pinch-zoom"]
    # A flash on the feed squeezes the stage instead of pushing it under the tabs.
    ui.goto("/profile")
    ui.submit("form[action='/logout'] button[type=submit]")
    expect(ui.page.locator(".flash")).to_be_visible()
    stage_bottom = "document.querySelector('.stage').getBoundingClientRect().bottom"
    nav_top = "document.querySelector('.topbar > nav').getBoundingClientRect().top"
    assert ui.page.evaluate(f"{stage_bottom} <= {nav_top} + 1")
    ui.goto("/terms")
    assert ui.page.evaluate(overflow) > 0
    ui.page.mouse.wheel(0, 5000)
    ui.page.wait_for_function("() => document.body.scrollTop > 0")
    bar_top = "document.querySelector('.topbar').getBoundingClientRect().top"
    assert ui.page.evaluate(f"[scrollY, {bar_top}]") == [0, 0]


def test_current_pill_slides_from_the_last_tab(ui: Ui, live_server: LiveServer) -> None:
    ui.page.add_init_script(
        "window.slides = []; const animate = Element.prototype.animate;"
        "Element.prototype.animate = function (frames, options) {"
        " if (options?.pseudoElement === '::before')"
        "  window.slides.push([this.textContent.trim(), frames[0].left]);"
        " return animate.call(this, frames, options); };"
    )
    ui.login(live_server.make_user("slider"))
    ui.goto("/feed")
    ui.page.get_by_role("link", name="Needs", exact=True).click()
    ui.page.wait_for_url(re.compile(r"/feed\?kind=need"))
    ui.page.wait_for_function("() => window.slides.length > 0")
    label, start = ui.page.evaluate("window.slides[0]")
    assert label == "Needs"
    assert float(start.removesuffix("px")) < 0  # it starts back over All, to the left
    ui.page.get_by_role("link", name="Leaders").click()
    ui.page.wait_for_url(re.compile(r"/leaders"))
    ui.page.wait_for_function("() => window.slides.length > 0")
    assert ui.page.evaluate("window.slides[0][0]") == "Leaders"


@pytest.mark.parametrize("size", ["mobile"])
def test_log_in_bubble_fills_the_phone(ui: Ui) -> None:
    ui.goto("/login")
    gap = "() => innerHeight - document.querySelector('.join-step').getBoundingClientRect().bottom"
    assert ui.page.evaluate(gap) <= 40  # only the tail and a gutter below the bubble (#237)


@pytest.mark.parametrize("size", ["mobile"])
def test_to_confirm_badge_floats_on_the_you_tab(ui: Ui) -> None:
    ui.login("dev_tom")  # the seed leaves dev_tom a gift to confirm
    you = ui.page.locator(".nav-user")
    expect(you.locator(".badge")).to_be_visible()
    assert you.locator(".badge").evaluate("el => getComputedStyle(el).position") == "absolute"
    label = you.locator(".nav-label").bounding_box()
    nav = ui.page.locator(".topbar > nav").bounding_box()
    assert label and nav and label["y"] + label["height"] <= nav["y"] + nav["height"]


PULL_DOWN = """() => {
  const at = (y) => [new Touch({identifier: 1, target: document.body, clientX: 200, clientY: y})];
  const fire = (type, y) => document.dispatchEvent(new TouchEvent(type, {
    touches: type === "touchend" ? [] : at(y), changedTouches: at(y), bubbles: true}));
  fire("touchstart", 200);
  fire("touchmove", 300);
  fire("touchmove", 420);
  fire("touchend", 420);
}"""


@pytest.mark.parametrize("size", ["mobile"])
def test_post_is_a_sheet_on_the_feed(ui: Ui, live_server: LiveServer) -> None:
    ui.login(live_server.make_user("sheet"))
    ui.goto("/feed")
    drag(ui, 0, -200)
    ui.page.wait_for_url(re.compile(r"/posts/\d+$"))
    post = ui.path()
    feed_tab = ui.page.locator('.topbar > nav a[href="/feed"]')
    expect(feed_tab).to_have_attribute("aria-current", "page")  # the post is still home
    ui.page.get_by_role("link", name="Leaders").click()
    ui.page.wait_for_url(re.compile(r"/leaders"))
    feed_tab.click()
    ui.page.wait_for_url(re.compile(re.escape(post) + "$"))  # Feed brings you back to that post
    ui.page.evaluate(PULL_DOWN)
    ui.page.wait_for_url(re.compile(r"/feed"))


def test_see_more_opens_the_sheet_and_close_puts_it_back(ui: Ui, live_server: LiveServer) -> None:
    ui.login(live_server.make_user("closer"))
    ui.goto("/feed?n=2")
    ui.page.locator(".deck > .deck-ticket .ticket-more").click()
    ui.page.wait_for_url(re.compile(r"/posts/\d+$"))
    ui.check("sheet")
    ui.page.locator(".sheet-close").click()
    ui.page.wait_for_url(re.compile(r"/feed\?n=2$"))  # the same ticket, not the top of the feed


def test_a_lone_ticket_still_swipes_down(make_ui: UiFactory, live_server: LiveServer) -> None:
    # The service worker would answer the feed before the route could strip its neighbors.
    ui = make_ui(service_workers="block")

    def without_neighbors(route: Route) -> None:
        html = route.fetch().text()
        html = re.sub(r'<a class="rail-btn deck-(back|next)".*?</a>', "", html)
        route.fulfill(body=html, content_type="text/html")

    ui.page.route(re.compile(r"/feed(\?.*)?$"), without_neighbors)
    ui.login(live_server.make_user("lone"))
    ui.goto("/feed?n=2")  # not the follow-through pick, which has no Show less (#255)
    expect(ui.page.locator(".deck-next, .deck-back")).to_have_count(0)
    drag(ui, 0, 200)
    ui.page.wait_for_url(re.compile(r"undo="))


def test_block_asks_first_then_blocks(ui: Ui, live_server: LiveServer) -> None:
    ui.login(live_server.make_user("blocker"))
    ui.goto("/u/maria_g")
    ui.page.get_by_role("button", name="Block maria_g").click()
    question = ui.page.locator(".block-confirm")
    expect(question).to_be_visible()  # nothing is blocked until they say so
    ui.check("block-ask")
    ui.page.locator(".block-cancel").click()
    expect(question).to_be_hidden()
    ui.page.get_by_role("button", name="Block maria_g").click()
    ui.submit(".block-confirm .btn-danger")
    expect(ui.page.get_by_role("button", name="Unblock maria_g")).to_be_visible()
    ui.goto("/profile#blocked")
    expect(ui.page.locator(".blocked-list li")).to_have_count(1)
    ui.check("blocked-list")
