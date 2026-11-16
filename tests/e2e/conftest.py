"""Browser tests against the real app (#207).

A live Yearnly server runs in a background thread on a temp SQLite database filled by the
dev seed, and Playwright drives Chromium at a phone size and a desktop size. Every page a
test visits is screenshotted and run through the design checks in `checks.py`; what they
find goes to `tests/e2e/artifacts/findings.jsonl` for the Impeccable review.

Run with `pytest -m e2e --no-cov`. The default `pytest` run skips these.
"""

import itertools
import json
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from flask import Flask
from playwright.sync_api import Browser, ConsoleMessage, Page, Request
from werkzeug.security import generate_password_hash
from werkzeug.serving import make_server

from app import create_app
from app.extensions import db
from app.models import User, utcnow
from app.seed import SEED_PASSWORD, seed
from tests.e2e import checks

ARTIFACTS = Path(__file__).parent / "artifacts"
FINDINGS = ARTIFACTS / "findings.jsonl"

DEVICES: dict[str, dict[str, Any]] = {
    # iPhone 15-ish: the iOS shell is the final target.
    "mobile": {
        "viewport": {"width": 390, "height": 844},
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
    "desktop": {"viewport": {"width": 1280, "height": 800}},
}


@dataclass
class LiveServer:
    app: Flask
    url: str
    _names: Iterator[int] = field(default_factory=itertools.count)

    def make_user(self, prefix: str = "e2e", *, handles: bool = True) -> str:
        """Add a verified, rules-accepted user with a Venmo handle and return their username."""
        username = f"{prefix}{next(self._names)}"
        with self.app.app_context():
            user = User(
                username=username,
                email=f"{username}@example.com",
                password_hash=generate_password_hash(SEED_PASSWORD),
                email_verified_at=utcnow(),
                adult_attested_at=utcnow(),
                rules_accepted_at=utcnow(),
                city="Sarasota",
                state="FL",
                venmo_handle=f"@{username}" if handles else None,
            )
            db.session.add(user)
            db.session.commit()
        return username


@pytest.fixture(scope="session")
def live_server(tmp_path_factory: pytest.TempPathFactory) -> Iterator[LiveServer]:
    # Each run starts a fresh findings file; screenshots are overwritten in place.
    ARTIFACTS.mkdir(exist_ok=True)
    FINDINGS.unlink(missing_ok=True)
    root = tmp_path_factory.mktemp("e2e")
    app = create_app(
        {
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{(root / 'e2e.db').as_posix()}",
            "PHOTO_DIR": str(root / "photos"),
            "R2_BUCKET": "",
            "MAIL_ASYNC": False,
            # Plain http from the start: cookie and HSTS settings are read when the app is
            # built, and a developer's .env may carry the https production address.
            "APP_URL": "http://127.0.0.1",
            "SESSION_COOKIE_SECURE": False,
        }
    )
    server = make_server("127.0.0.1", 0, app, threaded=True)
    url = f"http://127.0.0.1:{server.server_port}"
    app.config["APP_URL"] = url
    with app.app_context():
        db.create_all()
        seed()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield LiveServer(app, url)
    server.shutdown()


@dataclass
class Ui:
    """One browser page at one device size, plus everything the checks found on it."""

    page: Page
    device: str
    base: str
    test_name: str
    console_errors: list[str] = field(default_factory=list)
    failed_requests: list[str] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)

    def goto(self, path: str) -> None:
        self.page.goto(self.base + path)
        self.settle()

    def settle(self) -> None:
        self.page.wait_for_load_state("networkidle")
        # Let the arrival and view-transition animations finish before measuring.
        self.page.wait_for_timeout(1200)

    def submit(self, selector: str) -> None:
        """Click a submit button and wait for the page it leads to, however slow."""
        with self.page.expect_navigation():
            self.page.click(selector)
        self.settle()

    def login(self, username: str, password: str = SEED_PASSWORD) -> None:
        self.goto("/login")
        self.page.fill("#identifier", username)
        self.page.fill("#password", password)
        self.submit("form:has(#identifier) button[type=submit]")

    def path(self) -> str:
        return self.page.url.removeprefix(self.base) or "/"

    def check(
        self, step: str, *, focus: bool = True, extra: list[dict[str, Any]] | None = None
    ) -> list[dict[str, Any]]:
        """Screenshot this page and run every design check on it."""
        slug = f"{self.test_name}-{step}-{self.device}".replace("/", "_")
        shot = ARTIFACTS / f"{slug}.png"
        self.page.screenshot(path=str(shot), full_page=True)
        problems = [
            *(extra or []),
            *checks.run_all(self.page, mobile=self.device == "mobile", focus=focus),
        ]
        # A page that is itself a 404 logs its own status; that one is expected.
        expected_404 = step == "not-found"
        return self.record(step, problems, shot, skip=lambda e: expected_404 and "404" in e)

    def flush(self, step: str = "after the last check") -> list[dict[str, Any]]:
        """Record errors that came after the last check, so a test can't end on one unseen."""
        return self.record(step, [], None)

    def record(
        self,
        step: str,
        problems: list[dict[str, Any]],
        shot: Path | None,
        skip: Callable[[str], bool] = lambda _: False,
    ) -> list[dict[str, Any]]:
        problems = [
            *problems,
            *({"check": "console-error", "detail": e} for e in self.console_errors if not skip(e)),
            *({"check": "failed-request", "detail": r} for r in self.failed_requests),
        ]
        self.console_errors.clear()
        self.failed_requests.clear()
        screenshot = str(shot.relative_to(ARTIFACTS.parent.parent.parent)) if shot else ""
        found = [
            {
                **p,
                "page": self.path(),
                "step": step,
                "device": self.device,
                "test": self.test_name,
                "screenshot": screenshot,
            }
            for p in problems
        ]
        with FINDINGS.open("a", encoding="utf-8") as out:
            for f in found:
                out.write(json.dumps(f) + "\n")
        self.findings += found
        return found


# Not named `device`: pytest-playwright has a session-scoped fixture by that name.
@pytest.fixture(params=list(DEVICES))
def size(request: pytest.FixtureRequest) -> str:
    return str(request.param)


UiFactory = Callable[..., Ui]


@pytest.fixture
def make_ui(
    browser: Browser, live_server: LiveServer, size: str, request: pytest.FixtureRequest
) -> Iterator[UiFactory]:
    contexts = []

    def make(**context_args: Any) -> Ui:
        context = browser.new_context(**DEVICES[size], **context_args)
        contexts.append(context)
        page = context.new_page()
        name = request.node.originalname.removeprefix("test_")
        ui = Ui(page, size, live_server.url, name)

        def log_error(text: str) -> None:
            # Chromium raises this when the harness navigates mid view-transition; slow clicks
            # through the same pages never do, so it's the test, not the app.
            if "Transition was aborted" not in text:
                # Name the page it happened on, which may not be the next one checked.
                ui.console_errors.append(f"{text} (on {ui.path()})")

        def on_console(msg: ConsoleMessage) -> None:
            if msg.type == "error":
                log_error(msg.text)

        def on_failed(req: Request) -> None:
            # Pay-app links leave the site on purpose; only our own requests count.
            if req.url.startswith(live_server.url):
                ui.failed_requests.append(f"{req.method} {req.url}: {req.failure}")

        page.on("console", on_console)
        page.on("pageerror", lambda err: log_error(str(err)))
        page.on("requestfailed", on_failed)
        return ui

    yield make
    for context in contexts:
        context.close()


@pytest.fixture
def ui(make_ui: UiFactory) -> Ui:
    return make_ui()
