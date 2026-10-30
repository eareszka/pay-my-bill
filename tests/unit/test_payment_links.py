import pytest

from app.models import PaymentMethod, User
from app.payment_links import normalize_cashapp, normalize_paypal, normalize_venmo, pay_options


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("$maria", "$maria"), (" maria88 ", "$maria88"), ("", None), (None, None)],
)
def test_cashapp(raw: str | None, expected: str | None) -> None:
    assert normalize_cashapp(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"), [("@kayla-r", "@kayla-r"), ("jordan88", "@jordan88"), ("  ", None)]
)
def test_venmo(raw: str, expected: str | None) -> None:
    assert normalize_venmo(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("ChrisP", "ChrisP"),
        ("paypal.me/ChrisP", "ChrisP"),
        ("https://www.PayPal.me/ChrisP/", "ChrisP"),
    ],
)
def test_paypal(raw: str, expected: str) -> None:
    assert normalize_paypal(raw) == expected


@pytest.mark.parametrize(
    ("normalize", "raw"),
    [
        (normalize_cashapp, "$has space"),
        (normalize_cashapp, "$" + "a" * 21),
        (normalize_cashapp, "$maria_g"),
        (normalize_cashapp, "$12345"),
        (normalize_venmo, "@abc"),
        (normalize_venmo, "@bad!name"),
        (normalize_paypal, "paypal.com/me/x"),
        (normalize_paypal, "under_score"),
    ],
)
def test_invalid(normalize: object, raw: str) -> None:
    with pytest.raises(ValueError, match="."):
        normalize(raw)  # type: ignore[operator]


def test_pay_options_only_for_set_handles() -> None:
    user = User(cashapp_handle="$mariag", venmo_handle="@maria-g")
    options = pay_options(user)
    assert [(o.method, o.label, o.handle, o.url, o.amount_sep) for o in options] == [
        (PaymentMethod.CASHAPP, "Cash App", "$mariag", "https://cash.app/$mariag", "/"),
        (PaymentMethod.VENMO, "Venmo", "@maria-g", "https://venmo.com/maria-g?txn=pay", "&amount="),
    ]


def test_pay_options_paypal_and_none() -> None:
    assert [o.url for o in pay_options(User(paypal_handle="MariaG"))] == [
        "https://paypal.me/MariaG"
    ]
    assert pay_options(User()) == []
