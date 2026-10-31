from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Donation, DonationStatus, User

GIFT_XP = 10
NEW_PERSON_XP = 25


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

    @property
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
    # Only recipient-confirmed gifts earn anything (ADR 0004).
    return list(
        db.session.scalars(
            select(Donation)
            .options(joinedload(Donation.post))
            .where(Donation.donor_id == user.id, Donation.status == DonationStatus.CONFIRMED)
            .order_by(Donation.created_at, Donation.id)
        )
    )


def progress(gifts: list[Donation]) -> Progress:
    people = {gift.post.user_id for gift in gifts}
    return Progress(
        xp=GIFT_XP * len(gifts) + NEW_PERSON_XP * len(people), people_helped=len(people)
    )
