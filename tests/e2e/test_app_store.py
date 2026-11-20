"""App Store screenshots (#260): the real app on seed data at Apple's two required iPhone sizes.

Run with `pytest -m appstore --no-cov`. It writes PNGs to docs/app-store/screenshots/.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page

from app.seed import SEED_PASSWORD
from tests.e2e.conftest import LiveServer

OUT = Path(__file__).resolve().parents[2] / "docs" / "app-store" / "screenshots"
# Points at @3x: 430x932 is 1290x2796 (6.7"/6.9"), 414x896 is 1242x2688 (6.5").
SIZES = {"6.7in": (430, 932), "6.5in": (414, 896)}
DONOR = "dev_tom"  # a seed account with gifts, a level, and a gift to confirm


def settle(page: Page) -> None:
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)


@pytest.mark.appstore
@pytest.mark.parametrize("size", list(SIZES))
def test_app_store_screenshots(browser: Browser, live_server: LiveServer, size: str) -> None:
    width, height = SIZES[size]
    context = browser.new_context(
        viewport={"width": width, "height": height},
        device_scale_factor=3,
        is_mobile=True,
        has_touch=True,
    )
    page = context.new_page()
    out = OUT / size
    out.mkdir(parents=True, exist_ok=True)

    def shot(name: str, path: str) -> None:
        page.goto(live_server.url + path)
        settle(page)
        page.screenshot(path=out / f"{name}.png")

    shot("1-front-door", "/")
    shot("2-how-it-works", "/how/help/1")
    page.goto(live_server.url + "/login")
    page.fill("#identifier", DONOR)
    page.fill("#password", SEED_PASSWORD)
    page.locator("form:has(#identifier) button[type=submit]").click()
    settle(page)
    shot("3-feed", "/feed?n=2")
    page.locator(".deck > .deck-ticket .ticket-more").click()
    settle(page)
    page.screenshot(path=out / "4-post.png")
    # Chip in is its own page behind the round gift button (#295).
    page.locator(".chip-fab").click()
    settle(page)
    page.screenshot(path=out / "5-chip-in.png")
    shot("6-you", f"/u/{DONOR}?tab=chipped")
    shot("7-leaders", "/leaders")
    context.close()
