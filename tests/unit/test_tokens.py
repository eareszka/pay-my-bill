from flask import Flask

from app.tokens import make_token, read_token


def test_round_trip(app: Flask) -> None:
    assert read_token(make_token(7, "p"), "p", 60) == 7


def test_wrong_purpose_and_garbage(app: Flask) -> None:
    assert read_token(make_token(7, "p"), "q", 60) is None
    assert read_token("garbage", "p", 60) is None


def test_non_int_payload_rejected(app: Flask) -> None:
    from app.tokens import _serializer

    assert read_token(_serializer("p").dumps("7"), "p", 60) is None
