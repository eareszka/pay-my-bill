from flask import Blueprint, render_template, request
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Post, PostKind, PostStatus

bp = Blueprint("main", __name__)

PAGE_SIZE = 20


@bp.get("/")
def index() -> str:
    kind = request.args.get("kind")
    kind = kind if kind in {k.value for k in PostKind} else None
    page = max(request.args.get("page", 1, type=int) or 1, 1)
    query = (
        select(Post)
        .options(joinedload(Post.user))
        .where(Post.status == PostStatus.OPEN)
        .order_by(Post.created_at.desc(), Post.id.desc())
    )
    if kind:
        query = query.where(Post.kind == PostKind(kind))
    rows = list(db.session.scalars(query.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)))
    return render_template(
        "index.html",
        posts=rows[:PAGE_SIZE],
        kind=kind,
        page=page,
        has_next=len(rows) > PAGE_SIZE,
    )


@bp.get("/rules")
def rules() -> str:
    return render_template("rules.html")
