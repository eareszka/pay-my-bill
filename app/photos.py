"""One optional photo per post: check it, strip it, shrink it, and store it (ADR 0015)."""

from __future__ import annotations

import io
import secrets
from pathlib import Path
from typing import IO, Any, Protocol

from flask import Flask, current_app, url_for
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PHOTO_BYTES = 8 * 1024 * 1024
MAX_SOURCE_PIXELS = 40_000_000  # about 7,300 x 5,500; anything bigger is refused, not decoded
MAX_EDGE = 1600
WEBP_QUALITY = 80
ACCEPTED_FORMATS = {"JPEG", "PNG", "WEBP"}
PHOTO_ACCEPT = "image/jpeg,image/png,image/webp"


class PhotoError(ValueError):
    """The upload can't be used as a photo; the message is safe to show the poster."""


def process(stream: IO[bytes]) -> bytes:
    """Return a clean WebP: right way up, at most MAX_EDGE wide or tall, with no metadata."""
    raw = stream.read(MAX_PHOTO_BYTES + 1)
    if not raw:
        raise PhotoError("That file is empty.")
    if len(raw) > MAX_PHOTO_BYTES:
        raise PhotoError("Photos can be up to 8 MB.")
    try:
        with Image.open(io.BytesIO(raw)) as probe:
            if probe.format not in ACCEPTED_FORMATS:
                raise PhotoError("Use a JPG, PNG, or WebP photo.")
            if probe.width * probe.height > MAX_SOURCE_PIXELS:
                raise PhotoError("That photo is too large. Try one under 40 megapixels.")
            probe.verify()
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            upright = ImageOps.exif_transpose(image)
            rgb = upright.convert("RGB")
    except PhotoError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as error:
        raise PhotoError("That file isn't a photo we can read.") from error
    rgb.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    # A fresh image carries no EXIF, so location and camera details never leave the poster.
    rgb.save(out, "WEBP", quality=WEBP_QUALITY, method=4)
    return out.getvalue()


def new_key() -> str:
    return f"posts/{secrets.token_hex(16)}.webp"


class PhotoStore(Protocol):
    def put(self, key: str, data: bytes) -> None: ...
    def delete(self, key: str) -> None: ...
    def url(self, key: str) -> str: ...


class LocalStore:
    """Development and tests: files in a folder, served by the media route."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def path(self, key: str) -> Path:
        return self.root / key

    def put(self, key: str, data: bytes) -> None:
        target = self.path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def delete(self, key: str) -> None:
        self.path(key).unlink(missing_ok=True)

    def url(self, key: str) -> str:
        return url_for("main.media", key=key)


class R2Store:
    """Cloudflare R2 through its S3 API; photos are read from the bucket's public URL."""

    def __init__(self, client: Any, bucket: str, public_url: str) -> None:
        self.client = client
        self.bucket = bucket
        self.public_url = public_url.rstrip("/")

    def put(self, key: str, data: bytes) -> None:
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType="image/webp",
            CacheControl="public, max-age=31536000, immutable",
        )

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def url(self, key: str) -> str:
        return f"{self.public_url}/{key}"


def r2_client(account_id: str, access_key: str, secret_key: str) -> Any:  # pragma: no cover
    import boto3

    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def init_app(app: Flask) -> None:
    config = app.config
    store: PhotoStore
    if config["R2_BUCKET"]:
        client = config.get("R2_CLIENT") or r2_client(
            config["R2_ACCOUNT_ID"], config["R2_ACCESS_KEY_ID"], config["R2_SECRET_ACCESS_KEY"]
        )
        store = R2Store(client, config["R2_BUCKET"], config["R2_PUBLIC_URL"])
    else:
        store = LocalStore(Path(config["PHOTO_DIR"] or Path(app.instance_path) / "uploads"))
    app.extensions["photo_store"] = store
    app.jinja_env.globals["photo_url"] = photo_url
    app.jinja_env.globals["PHOTO_ACCEPT"] = PHOTO_ACCEPT


def store() -> PhotoStore:
    photo_store: PhotoStore = current_app.extensions["photo_store"]
    return photo_store


def photo_url(key: str) -> str:
    return store().url(key)


def save(data: bytes) -> str:
    key = new_key()
    store().put(key, data)
    return key


def discard(key: str | None) -> None:
    """Remove a stored photo. A failure is logged, never shown: the post change already stands."""
    if not key:
        return
    try:
        store().delete(key)
    except Exception:  # storage can fail in many ways, and the row is already gone
        current_app.logger.exception("Couldn't delete photo %s", key)
