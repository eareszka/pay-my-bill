import pytest

from app.payment_links import normalize_cashapp, normalize_paypal, normalize_venmo


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
