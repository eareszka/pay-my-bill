from urllib.parse import urlparse

from flask import Flask, current_app, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
from werkzeug.wrappers import Response

from app.extensions import db

MESSAGES = {
    400: ("That didn't work", "Something about that request wasn't right. Please try again."),
    403: ("You can't do that", "This action isn't open to your account."),
    404: ("We can't find that page", "It may have been removed, or the link may be wrong."),
    405: ("That didn't work", "That action isn't available on this page."),
}
DEFAULT = MESSAGES[400]
NO_SESSION = (
    "Your session ended",
    "Nothing was saved. Go back and try again. If this keeps happening, check that cookies are on.",
)


def back_url() -> str:
    # Back to the page the form was on, if it's on this site and can be opened.
    # A form that failed validation was rendered at a POST-only address.
    home = url_for("main.index")
    try:
        referrer = urlparse(request.referrer or "")
    except ValueError:
        return home
    adapter = current_app.create_url_adapter(request)
    if not adapter or referrer.netloc != request.host:
        return home
    try:
        adapter.match(referrer.path, method="GET")
    except RequestRedirect:
        return referrer.path
    except HTTPException:
        return home
    return referrer.path


def register(app: Flask) -> None:
    @app.errorhandler(CSRFError)
    def stale_form(_: CSRFError) -> Response | tuple[str, int]:
        # With no session cookie a flash can't survive a redirect, so explain it here.
        if app.config["SESSION_COOKIE_NAME"] not in request.cookies:
            title, message = NO_SESSION
            return render_template("error.html", title=title, message=message, back=back_url()), 400
        flash(
            "That page had gone stale, so nothing was saved. Please try again. "
            "If this keeps happening, check that cookies are on.",
            "error",
        )
        return redirect(back_url())

    @app.errorhandler(HTTPException)
    def http_error(error: HTTPException) -> tuple[str, int, list[tuple[str, str]]]:
        code = error.code or 400
        title, message = MESSAGES.get(code, DEFAULT)
        # Keep what the error says about itself, such as Allow on a 405.
        headers = [(k, v) for k, v in error.get_headers() if k.lower() != "content-type"]
        return render_template("error.html", title=title, message=message), code, headers

    @app.errorhandler(500)
    def server_error(_: Exception) -> tuple[str, int]:
        # Skips context processors, which query the database that may be why this is showing.
        db.session.rollback()
        return app.jinja_env.get_template("error_500.html").render(), 500
