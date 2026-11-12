import re

import pytest
from flask.testing import FlaskClient

from app.extensions import db
from app.models import Donation, DonationStatus, PaymentMethod, Post, PostKind
from tests.conftest import MakeUser, login_as


def visible_text(html: str) -> str:
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", html)


@pytest.mark.parametrize(
    "path",
    ["/leaders", "/rules", "/profile", "/profile?delete=1", "/posts/{id}", "/posts/{id}?delete=1"],
)
def test_pages_never_say_donor(client: FlaskClient, make_user: MakeUser, path: str) -> None:
    poster = make_user("maria_g", city="Tampa", state="FL", venmo_handle="@maria-g")
    helper = make_user("dev_tom")
    post = Post(
        user=poster, kind=PostKind.NEED, title="Rent", body="Short on rent.", goal_cents=9_000
    )
    db.session.add(post)
    db.session.add(
        Donation(
            post=post,
            donor=helper,
            amount_cents=2_000,
            method=PaymentMethod.VENMO,
            status=DonationStatus.CONFIRMED,
        )
    )
    db.session.commit()
    login_as(client, poster)
    response = client.get(path.format(id=post.id))
    assert response.status_code == 200
    assert "donor" not in visible_text(response.get_data(as_text=True)).lower()
