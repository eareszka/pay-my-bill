from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.extensions import db
from app.models import (
    MIN_ACCOUNT_AGE_DAYS,
    PUBLIC_STATUSES,
    Donation,
    Post,
    PostKind,
    Reaction,
    ReactionKind,
    User,
    as_utc,
    open_posts,
    posts_with_confirmed_gifts,
)

GOOD_RECORD, NEW_POSTER, POOR_RECORD = 2, 1, 0
MAX_FEEDBACK_PER_UPDATE = 3  # T16: a pile of kudos can't outweigh real follow-through


def established(user: User, at: datetime) -> bool:
    # Verified, and old enough when they acted, so an account made for the purpose never
    # counts, even once it ages (T2, T16). A real donor who later left keeps counting (T14);
    # a banned one doesn't (#147).
    old_enough = as_utc(user.created_at) + timedelta(days=MIN_ACCOUNT_AGE_DAYS) <= as_utc(at)
    return old_enough and not user.is_banned and (user.is_verified or user.is_deleted)


def real_gifts(post: Post) -> list[Donation]:
    return [gift for gift in post.confirmed_gifts if established(gift.donor, gift.created_at)]


def real_progress(post: Post) -> int:
    # Closest to its goal, going only by gifts from established accounts.
    return sum(gift.amount_cents for gift in real_gifts(post)) * 100 // post.goal_cents


def top_post(kind: PostKind | None = None) -> Post | None:
    """The post that comes first in the stack (ADR 0013).

    It rewards follow-through: posters with a good record come first, then first-time
    posters, then those whose updates drew more 🤨 than kudos and 👍. Anyone with an
    overdue update, or no way to be paid, is out. Closest to its goal breaks ties.
    """
    with_donors = selectinload(Post.donations).joinedload(Donation.donor)
    query = select(Post).options(joinedload(Post.user), with_donors).where(open_posts())
    if kind:
        query = query.where(Post.kind == kind)
    candidates = [post for post in db.session.scalars(query) if post.user.can_be_paid]
    if not candidates:
        return None
    poster_ids = {post.user_id for post in candidates}
    owed = db.session.scalars(
        select(Post)
        .options(with_donors)
        .where(Post.user_id.in_(poster_ids), posts_with_confirmed_gifts())
    ).all()
    overdue = {post.user_id for post in owed if post.update_overdue}
    # An update earns credit while it can still be read and questioned, and only if
    # someone real gave to that post.
    counted = [post for post in owed if post.update_body and real_gifts(post)]
    updates = Counter(post.user_id for post in counted)
    feedback = reaction_totals(poster_ids, {post.id for post in counted})

    def rank(post: Post) -> tuple[int, int, int, int]:
        count, net = updates[post.user_id], feedback[post.user_id]
        tier = POOR_RECORD if net < 0 else GOOD_RECORD if count else NEW_POSTER
        return (tier, count + net, real_progress(post), -post.id)

    eligible = [post for post in candidates if post.user_id not in overdue]
    return max(eligible, key=rank, default=None)


def reaction_totals(poster_ids: set[int], counted_posts: set[int]) -> Counter[int]:
    # 🤨 always lowers a record, so deleting a post or having it removed can't erase it.
    # Kudos and 👍 only raise it on an update that earned credit, on a post still public,
    # and each update can only raise it so far, so a pile of kudos can't cancel real doubts.
    rows = db.session.execute(
        select(Post.user_id, Post.id, Post.status, Reaction, User)
        .join(Reaction, Reaction.post_id == Post.id)
        .join(User, Reaction.user_id == User.id)
        .where(Post.user_id.in_(poster_ids))
    ).all()
    totals: Counter[int] = Counter()
    raised: Counter[tuple[int, int]] = Counter()
    for poster_id, post_id, status, reaction, user in rows:
        if not established(user, reaction.created_at):
            continue
        if reaction.kind is ReactionKind.HMM:
            totals[poster_id] -= 1
        elif post_id in counted_posts and status in PUBLIC_STATUSES:
            raised[poster_id, post_id] += 1
    for (poster_id, _), points in raised.items():
        totals[poster_id] += min(points, MAX_FEEDBACK_PER_UPDATE)
    return totals
