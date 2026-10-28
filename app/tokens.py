from flask import current_app
from itsdangerous import BadSignature, URLSafeTimedSerializer

VERIFY_EMAIL = "verify-email"
VERIFY_MAX_AGE = 48 * 3600


def _serializer(purpose: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=purpose)


def make_token(user_id: int, purpose: str) -> str:
    return _serializer(purpose).dumps(user_id)


def read_token(token: str, purpose: str, max_age: int) -> int | None:
    try:
        value = _serializer(purpose).loads(token, max_age=max_age)
    except BadSignature:
        return None
    return value if isinstance(value, int) else None
