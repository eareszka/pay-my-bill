from flask import Blueprint, render_template, request
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Post, PostKind, open_posts
from app.routes.posts import chip_in_context
from app.top_spot import top_post

bp = Blueprint("main", __name__)


def ticket_at(position: int, kind: PostKind | None) -> Post | None:
    # The earned ticket comes first (ADR 0013), then the rest of the stack, newest first.
    top = top_post(kind)
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
    post = ticket_at(position, kind) if total else None
    return render_template(
        "index.html",
        post=post,
        kind=kind.value if kind else None,
        position=position,
        total=total,
        **(chip_in_context(post) if post else {}),
    )


@bp.get("/rules")
def rules() -> str:
    return render_template("rules.html")
