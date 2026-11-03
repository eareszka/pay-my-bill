from collections import Counter

from sqlalchemy import select

from app.extensions import db
from app.models import (
    PUBLIC_STATUSES,
    Donation,
    DonationStatus,
    Post,
    PostKind,
    Reaction,
    ReactionKind,
    open_posts,
)

GOOD_RECORD, NEW_POSTER, POOR_RECORD = 2, 1, 0


def top_post(kind: PostKind | None = None) -> Post | None:
    """The post that gets the big ticket at the top of the board (ADR 0013).

    The spot rewards follow-through: posters with a good record come first, then
    first-time posters, then those whose updates drew more 🤨 than kudos and 👍.
    Anyone with an overdue update is out. Closest to its goal breaks ties.
    """
    query = select(Post).where(open_posts())
    if kind:
        query = query.where(Post.kind == kind)
    candidates = list(db.session.scalars(query))
    if not candidates:
        return None
    poster_ids = {post.user_id for post in candidates}
    owed = db.session.scalars(
        select(Post).where(
            Post.user_id.in_(poster_ids),
            Post.status.in_(PUBLIC_STATUSES),
            Post.donations.any(Donation.status == DonationStatus.CONFIRMED),
        )
    ).all()
    overdue = {post.user_id for post in owed if post.update_overdue}
    updates = Counter(post.user_id for post in owed if post.update_posted_at)
    feedback = reaction_totals(poster_ids)

    def rank(post: Post) -> tuple[int, int, int, int]:
        count, net = updates[post.user_id], feedback[post.user_id]
        tier = POOR_RECORD if net < 0 else GOOD_RECORD if count else NEW_POSTER
        return (tier, count + net, post.progress_percent, -post.id)

    eligible = [post for post in candidates if post.user_id not in overdue]
    return max(eligible, key=rank, default=None)


def reaction_totals(poster_ids: set[int]) -> Counter[int]:
    # Kudos and 👍 raise a poster's record and 🤨 lowers it. A scrubbed update no longer counts.
    rows = db.session.execute(
        select(Post.user_id, Reaction.kind)
        .join(Reaction, Reaction.post_id == Post.id)
        .where(Post.user_id.in_(poster_ids), Post.update_body.is_not(None))
    ).all()
    totals: Counter[int] = Counter()
    for poster_id, kind in rows:
        totals[poster_id] += -1 if kind is ReactionKind.HMM else 1
    return totals
