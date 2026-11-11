from datetime import timedelta

from flask.testing import FlaskClient

from app.extensions import db
from app.farm_flags import suspected_farms
from app.models import User, utcnow
from tests.conftest import MakeUser, login_as
from tests.integration.test_leaders import give, person


def puppets(make_user: MakeUser, count: int, hours_apart: int = 1) -> list[User]:
    start = utcnow() - timedelta(days=10)
    return [
        make_user(f"p{n}", created_at=start + timedelta(hours=n * hours_apart))
        for n in range(count)
    ]


def flagged() -> list[tuple[str, int, list[str]]]:
    return [
        (f.donor.username, f.helped, [u.username for u in f.cluster]) for f in suspected_farms()
    ]


def test_burst_of_single_donor_recipients_is_flagged(make_user: MakeUser) -> None:
    farmer = person(make_user, "farmer")
    for puppet in puppets(make_user, 5):
        give(farmer, puppet, cents=1)
    give(farmer, person(make_user, "real"))
    assert flagged() == [("farmer", 6, ["p0", "p1", "p2", "p3", "p4"])]


def test_spread_out_or_shared_recipients_are_not_flagged(make_user: MakeUser) -> None:
    spread = person(make_user, "spread")
    for puppet in puppets(make_user, 4, hours_apart=25):
        give(spread, puppet)
    sharer = person(make_user, "sharer")
    other = person(make_user, "other")
    for n, recipient in enumerate(
        [make_user(f"s{n}", created_at=utcnow() - timedelta(days=10)) for n in range(3)]
    ):
        give(sharer, recipient)
        if n == 0:
            give(other, recipient)
    assert flagged() == []


def test_two_in_a_burst_is_not_enough(make_user: MakeUser) -> None:
    donor = person(make_user, "donor")
    for puppet in puppets(make_user, 2):
        give(donor, puppet)
    assert flagged() == []


def test_banned_donors_drop_off(make_user: MakeUser) -> None:
    farmer = person(make_user, "farmer")
    for puppet in puppets(make_user, 3):
        give(farmer, puppet)
    farmer.banned_at = utcnow()
    db.session.commit()
    assert flagged() == []


def test_queue_lists_flags_with_a_ban_button(client: FlaskClient, make_user: MakeUser) -> None:
    login_as(client, make_user("boss", is_admin=True))
    assert b"Nothing looks off." in client.get("/admin").data
    farmer = person(make_user, "farmer")
    for puppet in puppets(make_user, 3):
        give(farmer, puppet)
    page = client.get("/admin").get_data(as_text=True)
    assert "Possible fake helping (1)" in page
    assert "Helped 3 people. 3 joined together" in page
    assert f"/admin/users/{farmer.id}/ban" in page
