from urllib.parse import urlparse

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response

from app.extensions import db

MESSAGES = {
    400: ("That didn't work", "Something about that request wasn't right. Please try again."),
    403: ("You can't do that", "This action isn't open to your account."),
    404: ("We can't find that page", "It may have been removed, or the link may be wrong."),
    405: ("That didn't work", "That action isn't available on this page."),
}
DEFAULT = ("That didn't work", "Something about that request wasn't right. Please try again.")


def safe_referrer() -> str:
    # Only ever send people back to a page on this site.
    referrer = urlparse(request.referrer or "")
    if referrer.netloc == request.host:
        return request.referrer or url_for("main.index")
    return url_for("main.index")


def register(app: Flask) -> None:
    @app.errorhandler(CSRFError)
    def stale_form(_: CSRFError) -> Response:
        flash("That page had gone stale, so nothing was saved. Please try again.", "error")
        return redirect(safe_referrer())

    @app.errorhandler(HTTPException)
    def http_error(error: HTTPException) -> tuple[str, int]:
        code = error.code or 400
        title, message = MESSAGES.get(code, DEFAULT)
        return render_template("error.html", title=title, message=message), code

    @app.errorhandler(500)
    def server_error(_: Exception) -> tuple[str, int]:
        # Stand-alone template: the database may be why this page is showing.
        db.session.rollback()
        return render_template("error_500.html"), 500
