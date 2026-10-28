import re
from decimal import Decimal, InvalidOperation

_DOLLARS_RE = re.compile(r"^\$?\s*(\d{1,3}(?:,\d{3})*|\d+)(?:\.(\d{1,2}))?$")


def parse_dollars(value: str) -> int:
    """Parse user input like "$1,000" or "45.5" into integer cents (ADR 0006)."""
    match = _DOLLARS_RE.match(value.strip())
    if match is None:
        raise ValueError(f"not a dollar amount: {value!r}")
    whole, frac = match.group(1).replace(",", ""), match.group(2) or "0"
    try:
        return int(Decimal(f"{whole}.{frac}") * 100)
    except InvalidOperation:  # pragma: no cover - the regex only lets digits through
        raise ValueError(f"not a dollar amount: {value!r}") from None


def format_cents(cents: int) -> str:
    dollars, rem = divmod(cents, 100)
    return f"${dollars:,}" if rem == 0 else f"${dollars:,}.{rem:02d}"
