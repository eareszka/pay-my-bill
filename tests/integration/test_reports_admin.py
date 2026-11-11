import smtplib
from datetime import timedelta
from unittest.mock import patch

import pytest
from flask import Flask, g
from flask.testing import FlaskClient
from sqlalchemy import select

from app.extensions import db
from app.models import Post, PostKind, PostStatus, Report, ReportReason, User, as_utc, utcnow
from tests.conftest import PASSWORD, MakeUser, login_as


def make_post(user: User, status: PostStatus = PostStatus.OPEN, **fields: object) -> Post:
    post = Post(
        user=user,
        kind=PostKind.NEED,
        title="Help with rent",
        body="Short on rent this month.",
        goal_cents=10_000,
        status=status,
        **fields,
    )
    db.session.add(post)
    db.session.commit()
    return post


@pytest.fixture
def admin(make_user: MakeUser) -> User:
    return make_user("boss", is_admin=True)


def open_reports() -> list[Report]:
    return list(db.session.scalars(select(Report).where(Report.resolved_at.is_(None))))


def test_report_a_post_notifies_admins(
    client: FlaskClient, make_user: MakeUser, admin: User, caplog: pytest.LogCaptureFixture
) -> None:
    post = make_post(make_user("poster"))
    login_as(client, make_user("bob"))
    page = client.get(f"/posts/{post.id}")
    assert f'href="/report/post/{post.id}"'.encode() in page.data
    assert b"Scam or false story" in client.get(f"/report/post/{post.id}").data

    resp = client.post(f"/report/post/{post.id}", data={"reason": "scam", "details": "Fake"})
    assert resp.status_code == 302
    (report,) = open_reports()
    assert (report.post_id, report.reason, report.details) == (post.id, ReportReason.SCAM, "Fake")
    assert "New report on Pay My Bill" in caplog.text
    assert "boss@example.com" in caplog.text

    client.post(f"/report/post/{post.id}", data={"reason": "spam"})
    assert len(open_reports()) == 1


def test_report_needs_a_reason(client: FlaskClient, make_user: MakeUser) -> None:
    post = make_post(make_user("poster"))
    login_as(client, make_user("bob"))
    resp = client.post(f"/report/post/{post.id}", data={})
    assert resp.status_code == 200
    assert b"Choose a reason." in resp.data
    assert open_reports() == []


def test_cant_report_own_post_or_hidden_or_missing(
    client: FlaskClient, make_user: MakeUser
) -> None:
    poster = make_user("poster")
    post = make_post(poster)
    hidden = make_post(make_user("other"), PostStatus.PENDING_REVIEW)
    login_as(client, poster)
    assert b"Report this post" not in client.get(f"/posts/{post.id}").data
    assert client.get(f"/report/post/{post.id}").status_code == 404
    assert client.get(f"/report/post/{hidden.id}").status_code == 404
    assert client.get("/report/post/99999").status_code == 404
    assert client.get("/report/post/99999999999").status_code == 404


def test_report_needs_a_verified_account(client: FlaskClient, make_user: MakeUser) -> None:
    post = make_post(make_user("poster"))
    login_as(client, make_user("new", verified=False))
    resp = client.post(f"/report/post/{post.id}", data={"reason": "scam"})
    assert resp.location.endswith("/verify/pending")


def test_report_a_user(client: FlaskClient, make_user: MakeUser, admin: User) -> None:
    target = make_user("creep")
    me = make_user("bob")
    login_as(client, me)
    assert b'href="/report/user/creep"' in client.get("/u/creep").data
    assert client.get("/report/user/creep").status_code == 200
    client.post("/report/user/creep", data={"reason": "harassment"})
    (report,) = open_reports()
    assert report.user_id == target.id
    assert b"Report bob" not in client.get("/u/bob").data
    assert client.get("/report/user/bob").status_code == 404
    assert client.get("/report/user/nobody").status_code == 404


def test_admin_queue_is_hidden_from_others(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("bob"))
    assert client.get("/admin").status_code == 404
    assert client.post("/admin/reports/1/dismiss").status_code == 404
    assert b'href="/admin"' not in client.get("/feed").data


def test_admin_approves_a_flagged_post_and_its_clock_restarts(
    client: FlaskClient, make_user: MakeUser, admin: User
) -> None:
    post = make_post(
        make_user("poster"), PostStatus.PENDING_REVIEW, created_at=utcnow() - timedelta(days=25)
    )
    login_as(client, admin)
    queue = client.get("/admin")
    assert b'href="/admin"' in queue.data
    assert b"Waiting for review (1)" in queue.data
    client.post(f"/admin/posts/{post.id}/approve")
    db.session.refresh(post)
    assert post.status == PostStatus.OPEN
    assert as_utc(post.created_at) > utcnow() - timedelta(minutes=1)
    assert post.is_open
    client.post(f"/admin/posts/{post.id}/approve")
    assert post.status == PostStatus.OPEN


def test_admin_removes_a_reported_post(
    client: FlaskClient, make_user: MakeUser, admin: User
) -> None:
    post = make_post(make_user("poster"))
    bob = make_user("bob")
    db.session.add(Report(reporter=bob, post=post, reason=ReportReason.SCAM))
    db.session.commit()
    login_as(client, admin)
    queue = client.get("/admin")
    assert b"Open reports (1)" in queue.data
    assert b"Remove post" in queue.data
    client.post(f"/admin/posts/{post.id}/remove")
    db.session.refresh(post)
    assert post.status == PostStatus.REMOVED
    assert open_reports() == []
    assert b"Remove post" not in client.get("/admin").data
    assert client.post("/admin/posts/99999/remove").status_code == 404


def test_admin_bans_a_user(client: FlaskClient, make_user: MakeUser, admin: User) -> None:
    creep = make_user("creep")
    open_post = make_post(creep)
    flagged = make_post(creep, PostStatus.PENDING_REVIEW)
    closed = make_post(creep, PostStatus.CLOSED)
    db.session.add_all(
        [
            Report(reporter=admin, user=creep, reason=ReportReason.HARASSMENT),
            Report(reporter=admin, post=open_post, reason=ReportReason.SCAM),
        ]
    )
    db.session.commit()
    login_as(client, admin)
    assert b"Ban creep" in client.get("/admin").data
    client.post(f"/admin/users/{creep.id}/ban")
    db.session.refresh(creep)
    assert creep.is_banned
    assert [p.status for p in (open_post, flagged, closed)] == [
        PostStatus.REMOVED,
        PostStatus.REMOVED,
        PostStatus.REMOVED,
    ]
    assert open_reports() == []
    assert client.post(f"/admin/users/{admin.id}/ban").status_code == 404
    assert client.post("/admin/users/99999/ban").status_code == 404


def test_banned_user_is_logged_out_and_cant_log_in(
    client: FlaskClient, make_user: MakeUser
) -> None:
    creep = make_user("creep")
    login_as(client, creep)
    creep.banned_at = utcnow()
    db.session.commit()
    assert client.get("/profile").status_code == 302
    right = client.post("/login", data={"identifier": "creep", "password": PASSWORD})
    wrong = client.post("/login", data={"identifier": "creep", "password": "not-it"})
    # Same reply either way, so it never confirms a guessed password.
    assert right.status_code == wrong.status_code == 200
    for resp in (right, wrong):
        assert b"Wrong username, email, or password." in resp.data
        assert b"suspended" not in resp.data
    assert client.get("/profile").status_code == 302


def test_admin_dismisses_a_report(client: FlaskClient, make_user: MakeUser, admin: User) -> None:
    creep = make_user("creep")
    report = Report(reporter=admin, user=creep, reason=ReportReason.OTHER, details="Odd")
    db.session.add(report)
    db.session.commit()
    login_as(client, admin)
    queue = client.get("/admin")
    assert b"Odd" in queue.data
    assert b"Ban creep" in queue.data
    client.post(f"/admin/reports/{report.id}/dismiss")
    db.session.refresh(report)
    assert report.resolution == "dismissed"
    assert b"No open reports." in client.get("/admin").data


def test_admin_actions_need_csrf(make_user: MakeUser, app: Flask) -> None:
    admin = make_user("boss", is_admin=True)
    report = Report(reporter=admin, user=make_user("creep"), reason=ReportReason.SPAM)
    db.session.add(report)
    db.session.commit()
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()
    login_as(client, admin)
    client.post(f"/admin/reports/{report.id}/dismiss")
    db.session.refresh(report)
    assert report.resolved_at is None


def test_flagged_post_notifies_admins(
    client: FlaskClient, make_user: MakeUser, admin: User, caplog: pytest.LogCaptureFixture
) -> None:
    login_as(client, make_user("poster", cashapp_handle="poster1", rules_accepted_at=utcnow()))
    client.post(
        "/posts/new",
        data={
            "kind": "want",
            "title": "Seed money for my startup",
            "body": "Help me launch my business.",
            "goal": "500",
        },
    )
    assert "A post is waiting for review" in caplog.text


def test_admin_email_failure_is_logged(
    client: FlaskClient, make_user: MakeUser, admin: User, caplog: pytest.LogCaptureFixture
) -> None:
    make_user("creep")
    login_as(client, make_user("bob"))
    with patch("app.mail.send_email", side_effect=smtplib.SMTPException("down")):
        resp = client.post("/report/user/creep", data={"reason": "spam"})
    assert resp.status_code == 302
    assert "Could not send" in caplog.text


def test_grant_command(app: Flask, make_user: MakeUser) -> None:
    user = make_user("emery")
    runner = app.test_cli_runner()
    result = runner.invoke(args=["admin", "grant", "Emery@Example.com"])
    assert result.exit_code == 0
    assert "emery is now an admin." in result.output
    db.session.refresh(user)
    assert user.is_admin
    missing = runner.invoke(args=["admin", "grant", "nobody@example.com"])
    assert missing.exit_code != 0
    assert "No account uses" in missing.output


def test_a_ban_hides_the_user_everywhere(
    client: FlaskClient, make_user: MakeUser, admin: User
) -> None:
    from app.leaderboard import Period, Scope, rank
    from app.rewards import confirmed_gifts
    from tests.integration.test_leaders import give, person

    creep = person(make_user, "creep")
    donor = person(make_user, "donor")
    give(donor, creep)  # creep was helped
    give(creep, person(make_user, "someone"))  # creep helped someone
    assert {r.user.username for r in rank(Scope.GLOBAL, Period.ALL, None)} == {"donor", "creep"}
    assert client.get("/u/creep").status_code == 200
    # Requests in the fixture's app context share g, so forget the visitor.
    g.pop("_login_user", None)

    login_as(client, admin)
    client.post(f"/admin/users/{creep.id}/ban")
    # Off the boards as a donor, and gifts to them no longer count.
    assert [r.user.username for r in rank(Scope.GLOBAL, Period.ALL, None)] == []
    assert confirmed_gifts(donor) == []
    assert all(p.status == PostStatus.REMOVED for p in creep.posts)
    # Only admins can still open the profile.
    assert client.get("/u/creep").status_code == 200
    client.post("/logout")
    g.pop("_login_user", None)
    assert client.get("/u/creep").status_code == 404


def test_a_banned_user_cannot_be_reported(client: FlaskClient, make_user: MakeUser) -> None:
    creep = make_user("creep", banned_at=utcnow())
    login_as(client, make_user("alice"))
    assert client.get(f"/report/user/{creep.username}").status_code == 404
