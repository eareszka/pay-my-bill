"""Error reports to Sentry when SENTRY_DSN is set (#259, PB-15).

Nothing personal leaves: no request bodies, cookies, headers, query strings, or user,
and the one-tap links' tokens are cut out of the URL.
"""

import re
from typing import Any

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

TOKEN_IN_PATH = re.compile(r"/(verify|reset|gifts/answer)/[^/?#]+")


def scrub(event: Any, hint: Any) -> Any:
    request = event.get("request")
    if request:
        for key in ("data", "cookies", "headers", "query_string", "env"):
            request.pop(key, None)
        if "url" in request:
            request["url"] = TOKEN_IN_PATH.sub(r"/\1/[token]", request["url"])
    event.pop("user", None)
    return event


def init(dsn: str, environment: str) -> bool:
    if not dsn:
        return False
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[FlaskIntegration(transaction_style="endpoint")],
        send_default_pii=False,
        max_request_body_size="never",
        traces_sample_rate=0,
        before_send=scrub,
    )
    return True
