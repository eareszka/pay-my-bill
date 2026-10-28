from flask import current_app
from itsdangerous import BadSignature, URLSafeTimedSerializer

VERIFY_EMAIL = "verify-email"
VERIFY_MAX_AGE = 48 * 3600


def _serializer(purpose: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=purpose)


def make_token(user_id: int, bound_to: str, purpose: str) -> str:
    return _serializer(purpose).dumps([user_id, bound_to])


def read_token(token: str, purpose: str, max_age: int) -> tuple[int, str] | None:
    try:
        value = _serializer(purpose).loads(token, max_age=max_age)
    except BadSignature:
        return None
    match value:
        case [int() as user_id, str() as bound_to]:
            return user_id, bound_to
    return None
