import re
from typing import NamedTuple

from app.models import PaymentMethod, User

CASHAPP_RE = re.compile(r"^\$?((?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{1,20})$")
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


class PayOption(NamedTuple):
    method: PaymentMethod
    label: str
    handle: str
    url: str
    amount_sep: str


# Base pay URL per app and how an amount is appended to it (done in the browser).
PAY_URLS = {
    PaymentMethod.CASHAPP: ("Cash App", "https://cash.app/{}", "/"),
    PaymentMethod.VENMO: ("Venmo", "https://venmo.com/?txn=pay&recipients={}", "&amount="),
    PaymentMethod.PAYPAL: ("PayPal", "https://paypal.me/{}", "/"),
}


def pay_options(user: User) -> list[PayOption]:
    handles = {
        PaymentMethod.CASHAPP: user.cashapp_handle,
        PaymentMethod.VENMO: user.venmo_handle,
        PaymentMethod.PAYPAL: user.paypal_handle,
    }
    options = []
    for method, handle in handles.items():
        if handle:
            label, url, sep = PAY_URLS[method]
            options.append(PayOption(method, label, handle, url.format(handle.lstrip("@")), sep))
    return options
