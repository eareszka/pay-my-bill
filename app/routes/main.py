from flask import Blueprint, render_template, request
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.extensions import db
from app.models import Post, PostKind, PostStatus

bp = Blueprint("main", __name__)

PAGE_SIZE = 20
MAX_PAGE = 1000


@bp.get("/")
def index() -> str:
    kind = request.args.get("kind", type=PostKind)
    page = min(max(request.args.get("page", 1, type=int), 1), MAX_PAGE)
    query = (
        select(Post)
        .options(joinedload(Post.user), selectinload(Post.donations))
        .where(Post.status == PostStatus.OPEN)
        .order_by(Post.created_at.desc(), Post.id.desc())
    )
    if kind:
        query = query.where(Post.kind == kind)
    rows = list(db.session.scalars(query.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)))
    return render_template(
        "index.html",
        posts=rows[:PAGE_SIZE],
        kind=kind.value if kind else None,
        page=page,
        has_next=len(rows) > PAGE_SIZE,
    )


@bp.get("/rules")
def rules() -> str:
    return render_template("rules.html")
