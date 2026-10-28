import pytest

from app.money import format_cents, parse_dollars


@pytest.mark.parametrize(
    ("raw", "cents"),
    [
        ("120", 12_000),
        ("$1,000", 100_000),
        (" 45.5 ", 4_550),
        ("$ 0.99", 99),
        ("1000.00", 100_000),
        ("0", 0),
    ],
)
def test_parse_dollars(raw: str, cents: int) -> None:
    assert parse_dollars(raw) == cents


@pytest.mark.parametrize("raw", ["", "abc", "-5", "1.234", "1,00", "1e3", "$$5"])
def test_parse_dollars_rejects(raw: str) -> None:
    with pytest.raises(ValueError, match="."):
        parse_dollars(raw)


@pytest.mark.parametrize(
    ("cents", "text"), [(12_000, "$120"), (100_000, "$1,000"), (4_550, "$45.50"), (5, "$0.05")]
)
def test_format_cents(cents: int, text: str) -> None:
    assert format_cents(cents) == text
