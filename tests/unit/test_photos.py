import io
import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from flask import Flask
from PIL import Image

from app import create_app, photos
from app.photos import LocalStore, PhotoError, R2Store, process


def image_bytes(size: tuple[int, int] = (40, 30), fmt: str = "JPEG", **save: object) -> bytes:
    out = io.BytesIO()
    Image.new("RGB" if fmt != "PNG" else "RGBA", size, "red").save(out, fmt, **save)
    return out.getvalue()


def opened(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def test_photo_becomes_webp_without_metadata() -> None:
    exif = Image.Exif()
    exif[0x0110] = "SecretCam 3000"  # camera model
    exif[0x8825] = {2: (40.0, 26.0, 46.0)}  # GPS latitude
    out = process(io.BytesIO(image_bytes(exif=exif)))
    assert opened(out).format == "WEBP"
    assert not opened(out).getexif()
    assert b"SecretCam" not in out
    assert b"Exif" not in out


def test_big_photo_is_shrunk_to_the_longest_edge() -> None:
    out = process(io.BytesIO(image_bytes((3200, 1000))))
    assert opened(out).size == (1600, 500)


def test_small_photo_keeps_its_size() -> None:
    assert opened(process(io.BytesIO(image_bytes((300, 200))))).size == (300, 200)


def test_sideways_phone_photo_is_turned_upright() -> None:
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90 degrees
    assert opened(process(io.BytesIO(image_bytes((40, 30), exif=exif)))).size == (30, 40)


@pytest.mark.parametrize("fmt", ["PNG", "WEBP"])
def test_png_and_webp_are_accepted(fmt: str) -> None:
    assert opened(process(io.BytesIO(image_bytes(fmt=fmt)))).format == "WEBP"


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (b"", "empty"),
        (b"just some text, not a photo", "isn't a photo"),
        (image_bytes(fmt="GIF"), "JPG, PNG, or WebP"),
        (image_bytes()[:200], "isn't a photo"),
    ],
)
def test_unusable_files_are_refused(data: bytes, message: str) -> None:
    with pytest.raises(PhotoError, match=message):
        process(io.BytesIO(data))


def test_file_over_8_mb_is_refused() -> None:
    with pytest.raises(PhotoError, match="8 MB"):
        process(io.BytesIO(b"\0" * (photos.MAX_PHOTO_BYTES + 1)))


def test_huge_dimensions_are_refused_before_decoding(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(photos, "MAX_SOURCE_PIXELS", 100)
    with pytest.raises(PhotoError, match="too large"):
        process(io.BytesIO(image_bytes((20, 20))))


def test_keys_are_random_webp_paths() -> None:
    first, second = photos.new_key(), photos.new_key()
    assert first != second
    assert first.startswith("posts/")
    assert first.endswith(".webp")


def test_local_store_writes_and_deletes(app: Flask, tmp_path: Path) -> None:
    store = LocalStore(tmp_path)
    store.put("posts/a.webp", b"data")
    assert (tmp_path / "posts" / "a.webp").read_bytes() == b"data"
    assert store.url("posts/a.webp").endswith("/media/posts/a.webp")
    store.delete("posts/a.webp")
    store.delete("posts/a.webp")  # already gone is fine
    assert not (tmp_path / "posts" / "a.webp").exists()


def test_r2_store_uses_the_bucket_and_public_url() -> None:
    client = MagicMock()
    store = R2Store(client, "pmb-photos", "https://photos.example.com/")
    store.put("posts/a.webp", b"data")
    client.put_object.assert_called_once()
    sent = client.put_object.call_args.kwargs
    assert (sent["Bucket"], sent["Key"], sent["Body"]) == ("pmb-photos", "posts/a.webp", b"data")
    assert sent["ContentType"] == "image/webp"
    store.delete("posts/a.webp")
    client.delete_object.assert_called_once_with(Bucket="pmb-photos", Key="posts/a.webp")
    assert store.url("posts/a.webp") == "https://photos.example.com/posts/a.webp"


def test_app_uses_r2_when_a_bucket_is_set() -> None:
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "R2_BUCKET": "pmb-photos",
            "R2_PUBLIC_URL": "https://photos.example.com",
            "R2_CLIENT": MagicMock(),
        }
    )
    assert isinstance(app.extensions["photo_store"], R2Store)


def test_app_uses_a_local_folder_without_a_bucket(app: Flask) -> None:
    assert isinstance(app.extensions["photo_store"], LocalStore)


def test_discard_ignores_no_photo_and_logs_failures(
    app: Flask, caplog: pytest.LogCaptureFixture
) -> None:
    photos.discard(None)
    broken = MagicMock()
    broken.delete.side_effect = OSError("bucket down")
    app.extensions["photo_store"] = broken
    with caplog.at_level(logging.ERROR):
        photos.discard("posts/a.webp")
    assert "Couldn't delete photo posts/a.webp" in caplog.text
