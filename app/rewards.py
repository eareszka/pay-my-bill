from dataclasses import dataclass
from datetime import timedelta
from functools import cached_property

from sqlalchemy import select
from sqlalchemy.orm import aliased, joinedload

from app.extensions import db
from app.models import Donation, DonationStatus, Post, PostStatus, User, utcnow

GIFT_XP = 10
NEW_PERSON_XP = 25
RECIPIENT_MIN_AGE_DAYS = 3


def level_start(level: int) -> int:
    """XP needed to reach a level: 0, 100, 300, 600, 1,000, ..."""
    return 50 * level * (level - 1)


def level_for(xp: int) -> int:
    level = 1
    while level_start(level + 1) <= xp:
        level += 1
    return level


@dataclass(frozen=True)
class Progress:
    xp: int
    people_helped: int

    @cached_property
    def level(self) -> int:
        return level_for(self.xp)

    @property
    def next_level_at(self) -> int:
        return level_start(self.level + 1)

    @property
    def percent(self) -> int:
        start = level_start(self.level)
        return (self.xp - start) * 100 // (self.next_level_at - start)


def confirmed_gifts(user: User) -> list[Donation]:
    """Gifts that earn rewards (ADR 0004, ADR 0010).

    Confirmed, not on a removed post, and to a verified recipient whose account
    is at least 3 days old, so throwaway accounts can't farm XP (T2).
    """
    recipient = aliased(User)
    return list(
        db.session.scalars(
            select(Donation)
            .join(Donation.post)
            .join(recipient, Post.user)
            .options(joinedload(Donation.post).lazyload(Post.donations))
            .where(
                Donation.donor_id == user.id,
                Donation.status == DonationStatus.CONFIRMED,
                Post.status != PostStatus.REMOVED,
                recipient.email_verified_at.is_not(None),
                recipient.created_at <= utcnow() - timedelta(days=RECIPIENT_MIN_AGE_DAYS),
            )
        )
    )


def progress(gifts: list[Donation]) -> Progress:
    people = {gift.post.user_id for gift in gifts}
    return Progress(
        xp=GIFT_XP * len(gifts) + NEW_PERSON_XP * len(people), people_helped=len(people)
    )
