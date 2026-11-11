import re

from flask import Blueprint, abort, render_template, request, send_from_directory
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from werkzeug.wrappers import Response

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
    return render_template("legal/terms.html")


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
