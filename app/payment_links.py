import re

CASHAPP_RE = re.compile(r"^\$?([A-Za-z0-9_-]{1,20})$")
VENMO_RE = re.compile(r"^@?([A-Za-z0-9_-]{5,30})$")
PAYPAL_RE = re.compile(r"^(?:(?:https?://)?(?:www\.)?paypal\.me/)?([A-Za-z0-9]{1,20})/?$", re.I)


def _normalize(value: str | None, pattern: re.Pattern[str], prefix: str) -> str | None:
    value = (value or "").strip()
    if not value:
        return None
    match = pattern.match(value)
    if match is None:
        raise ValueError(value)
    return prefix + match.group(1)


def normalize_cashapp(value: str | None) -> str | None:
    return _normalize(value, CASHAPP_RE, "$")


def normalize_venmo(value: str | None) -> str | None:
    return _normalize(value, VENMO_RE, "@")


def normalize_paypal(value: str | None) -> str | None:
    return _normalize(value, PAYPAL_RE, "")
