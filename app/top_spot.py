from collections import Counter
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import aliased, joinedload

from app.extensions import db
from app.models import (
    MIN_ACCOUNT_AGE_DAYS,
    PUBLIC_STATUSES,
    Post,
    PostKind,
    Reaction,
    ReactionKind,
    User,
    as_utc,
    open_posts,
    posts_with_confirmed_gifts,
    utcnow,
)

GOOD_RECORD, NEW_POSTER, POOR_RECORD = 2, 1, 0
MAX_FEEDBACK_PER_UPDATE = 3  # T16: a pile of kudos can't outweigh real follow-through


def established(user: User) -> bool:
    # The same bar as rewards: verified accounts this old can't be made on the spot (T2, T16).
    cutoff = utcnow() - timedelta(days=MIN_ACCOUNT_AGE_DAYS)
    return user.is_verified and as_utc(user.created_at) <= cutoff


def top_post(kind: PostKind | None = None) -> Post | None:
    """The post that gets the big ticket at the top of the board (ADR 0013).

    The spot rewards follow-through: posters with a good record come first, then
    first-time posters, then those whose updates drew more 🤨 than kudos and 👍.
    Anyone with an overdue update, or no way to be paid, is out. Closest to its
    goal breaks ties.
    """
    query = select(Post).options(joinedload(Post.user)).where(open_posts())
    if kind:
        query = query.where(Post.kind == kind)
    candidates = [post for post in db.session.scalars(query) if post.user.has_payment_handle]
    if not candidates:
        return None
    poster_ids = {post.user_id for post in candidates}
    owed = db.session.scalars(
        select(Post).where(Post.user_id.in_(poster_ids), posts_with_confirmed_gifts())
    ).all()
    overdue = {post.user_id for post in owed if post.update_overdue}
    # An update only earns credit if someone real gave to that post.
    updates = Counter(
        post.user_id
        for post in owed
        if post.update_posted_at and any(established(g.donor) for g in post.confirmed_gifts)
    )
    feedback = reaction_totals(poster_ids)

    def rank(post: Post) -> tuple[int, int, int, int]:
        count, net = updates[post.user_id], feedback[post.user_id]
        tier = POOR_RECORD if net < 0 else GOOD_RECORD if count else NEW_POSTER
        return (
            tier,
            count + min(net, count * MAX_FEEDBACK_PER_UPDATE),
            post.progress_percent,
            -post.id,
        )

    eligible = [post for post in candidates if post.user_id not in overdue]
    return max(eligible, key=rank, default=None)


def reaction_totals(poster_ids: set[int]) -> Counter[int]:
    # Kudos and 👍 raise a poster's record and 🤨 lowers it. Deleting a post doesn't erase
    # its feedback, so 🤨 can't be wiped away. Moderated posts stop counting either way.
    reactor = aliased(User)
    rows = db.session.execute(
        select(Post.user_id, Reaction.kind, reactor)
        .join(Reaction, Reaction.post_id == Post.id)
        .join(reactor, Reaction.user_id == reactor.id)
        .where(Post.user_id.in_(poster_ids), Post.status.in_(PUBLIC_STATUSES))
    ).all()
    totals: Counter[int] = Counter()
    for poster_id, kind, user in rows:
        if established(user):
            totals[poster_id] += -1 if kind is ReactionKind.HMM else 1
    return totals
