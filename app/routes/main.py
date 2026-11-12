import re
from typing import Any

from flask import Blueprint, abort, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from werkzeug.wrappers import Response

from app import stripe_pay
from app.door_photos import door_photos
from app.extensions import db
from app.models import Post, PostKind, open_posts
from app.photos import LocalStore, store
from app.routes.posts import chip_in_context
from app.top_spot import top_post

bp = Blueprint("main", __name__)

PHOTO_KEY = re.compile(r"posts/[0-9a-f]{32}\.webp")


def ticket_at(position: int, kind: PostKind | None, top: Post | None) -> Post | None:
    # The earned ticket comes first (ADR 0013), then the rest of the stack, newest first.
    if top and position == 1:
        return top
    query = (
        select(Post)
        .options(joinedload(Post.user))
        .where(open_posts())
        .order_by(Post.created_at.desc(), Post.id.desc())
    )
    if kind:
        query = query.where(Post.kind == kind)
    if top:
        query = query.where(Post.id != top.id)
    return db.session.scalars(query.offset(position - (2 if top else 1)).limit(1)).first()


@bp.get("/")
def home() -> str | Response:
    # The how-it-works story is for new visitors (#120); everyone else, and old feed links, go on.
    # Tracking tags on a shared link (?utm_source=, ?fbclid=) still show the story.
    args: dict[str, Any] = {k: v for k, v in request.args.items() if k in ("kind", "n")}
    if current_user.is_authenticated or args:
        return redirect(url_for("main.index", **args))
    return render_template(
        "home.html", help_photos=door_photos(funded=False), ask_photos=door_photos(funded=True)
    )


# Each door opens its own story, one step per page, so Back and links work without JavaScript.
STORY_STEPS = {"help": 4, "ask": 3}


@bp.get("/how/<any(help, ask):path>", defaults={"step": 1})
@bp.get("/how/<any(help, ask):path>/<int:step>")
def how(path: str, step: int) -> str:
    total = STORY_STEPS[path]
    if not 1 <= step <= total:
        abort(404)
    other = "ask" if path == "help" else "help"
    # Each step carries three of its door's photos, so neighboring steps never show the same ones.
    pool = door_photos(funded=path == "ask")
    start = (step - 1) % 2 * 3
    return render_template(
        "how/story.html",
        path=path,
        other=other,
        step=step,
        total=total,
        photos=pool[start : start + 3],
    )


@bp.get("/feed")
def index() -> str:
    kind = request.args.get("kind", type=PostKind)
    count = select(func.count()).select_from(Post).where(open_posts())
    if kind:
        count = count.where(Post.kind == kind)
    total = db.session.scalar(count) or 0
    position = request.args.get("n", 1, type=int)
    # An old link can point past the end of a stack that has shrunk.
    if not 1 <= position <= total:
        position = 1
    top = top_post(kind) if total else None
    post = ticket_at(position, kind, top) if total else None
    # The tickets either side go in the page, so a swipe reveals one straight away.
    next_post = ticket_at(position + 1 if position < total else 1, kind, top) if total > 1 else None
    back_post = ticket_at(position - 1, kind, top) if position > 1 else None
    return render_template(
        "index.html",
        post=post,
        next_post=next_post,
        back_post=back_post,
        kind=kind.value if kind else None,
        position=position,
        total=total,
        **(chip_in_context(post) if post else {}),
    )


@bp.get("/rules")
def rules() -> str:
    return render_template("rules.html")


@bp.get("/terms")
def terms() -> str:
    return render_template("legal/terms.html", card_fee=stripe_pay.fee_terms())


@bp.get("/privacy")
def privacy() -> str:
    return render_template("legal/privacy.html")


@bp.get("/media/<path:key>")
def media(key: str) -> Response:
    # Local photos only; in production they come straight from the R2 bucket.
    photo_store = store()
    if not isinstance(photo_store, LocalStore) or not PHOTO_KEY.fullmatch(key):
        abort(404)
    return send_from_directory(photo_store.root, key, mimetype="image/webp", max_age=31536000)
