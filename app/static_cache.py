"""Fast page moves (#219): static files cache for a year, and front-door pages for a minute.

Every static URL carries a hash of the file (`?v=`), so a deploy changes the URL and the
browser never revalidates the CSS and scripts that block each page's first paint.
"""

import hashlib
from pathlib import Path

from flask import Flask, get_flashed_messages, make_response, request
from werkzeug.wrappers import Response

YEAR = 365 * 24 * 60 * 60
FRONT_DOOR_SECONDS = 60
_hashes: dict[str, str | None] = {}


def file_hash(folder: str, filename: str) -> str | None:
    path = Path(folder, filename)
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def version_of(app: Flask, filename: str) -> str | None:
    if app.debug or filename not in _hashes:
        _hashes[filename] = file_hash(str(app.static_folder), filename)
    return _hashes[filename]


def front_door_page(html: str) -> Response:
    """Let the browser keep a logged-out story page briefly, so a prefetched step opens at once.

    A page that showed a flash message isn't kept, or going back would show it again.
    """
    response = make_response(html)
    if not get_flashed_messages():  # the messages this page already rendered
        response.cache_control.private = True
        response.cache_control.max_age = FRONT_DOOR_SECONDS
        # Logging in rewrites the session cookie, so the kept logged-out copy stops matching.
        response.vary.add("Cookie")
    return response


def init_app(app: Flask) -> None:
    @app.url_defaults
    def version_static(endpoint: str, values: dict[str, str]) -> None:
        # Fonts keep plain URLs: app.css loads them by relative path, and a preload must match it.
        filename = values.get("filename", "")
        if (
            endpoint == "static"
            and filename
            and not filename.startswith("fonts/")
            and "v" not in values
        ):
            version = version_of(app, filename)
            if version:
                values["v"] = version

    @app.after_request
    def cache_static(response: Response) -> Response:
        if request.endpoint != "static" or response.status_code not in (200, 304):
            return response
        filename = (request.view_args or {}).get("filename", "")
        # Only the current version is kept for good; an old ?v= still revalidates.
        if request.args.get("v") and request.args["v"] == version_of(app, filename):
            response.cache_control.no_cache = None
            response.cache_control.public = True
            response.cache_control.max_age = YEAR
            response.cache_control.immutable = True
        return response
