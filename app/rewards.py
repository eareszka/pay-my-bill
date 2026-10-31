from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from functools import cached_property

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import aliased, contains_eager, lazyload

from app.extensions import db
from app.models import (
    DELETED_EMAIL_DOMAIN,
    Donation,
    DonationStatus,
    Post,
    PostStatus,
    User,
    as_utc,
    utcnow,
)

GIFT_XP = 10
NEW_PERSON_XP = 25
MIN_ACCOUNT_AGE_DAYS = 3  # T2: verified accounts this old count toward rewards


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


def rewardable_gifts() -> Select[Donation]:
    """Gifts that earn rewards and rank on leaderboards (ADR 0004, ADR 0010).

    Confirmed, not on a removed post, and to a verified recipient whose account
    is at least 3 days old, so throwaway accounts can't farm XP (T2). Each gift
    comes with its post and recipient loaded.
    """
    recipient = aliased(User)
    return (
        select(Donation)
        .join(Donation.post)
        .join(recipient, Post.user)
        .options(
            contains_eager(Donation.post).options(
                lazyload(Post.donations), contains_eager(Post.user.of_type(recipient))
            )
        )
        .where(
            Donation.status == DonationStatus.CONFIRMED,
            Post.status != PostStatus.REMOVED,
            # A recipient who later deleted their account still counts (T14).
            or_(
                recipient.email_verified_at.is_not(None),
                recipient.email.endswith(DELETED_EMAIL_DOMAIN),
            ),
            recipient.created_at <= utcnow() - timedelta(days=MIN_ACCOUNT_AGE_DAYS),
        )
    )


def confirmed_gifts(user: User) -> list[Donation]:
    return list(db.session.scalars(rewardable_gifts().where(Donation.donor_id == user.id)))


def progress(gifts: list[Donation]) -> Progress:
    people = {gift.post.user_id for gift in gifts}
    return Progress(
        xp=GIFT_XP * len(gifts) + NEW_PERSON_XP * len(people), people_helped=len(people)
    )


def week_of(moment: datetime) -> date:
    """The Monday (UTC) of the week a moment falls in."""
    day = as_utc(moment).astimezone(UTC).date()
    return day - timedelta(days=day.weekday())


def gift_weeks(gifts: list[Donation]) -> set[date]:
    # A gift counts in the week it was confirmed, so a batch of old claims
    # confirmed together can't backfill a streak.
    return {week_of(gift.resolved_at or gift.created_at) for gift in gifts}


def streak(gifts: list[Donation], now: datetime | None = None) -> int:
    """Consecutive weeks with a confirmed gift, ending this week or last week."""
    weeks = gift_weeks(gifts)
    week = week_of(now or utcnow())
    if week not in weeks:
        week -= timedelta(weeks=1)
    count = 0
    while week in weeks:
        count += 1
        week -= timedelta(weeks=1)
    return count


def longest_streak(gifts: list[Donation]) -> int:
    weeks = gift_weeks(gifts)
    best = 0
    for week in weeks:
        if week - timedelta(weeks=1) in weeks:
            continue
        run = 1
        while week + timedelta(weeks=run) in weeks:
            run += 1
        best = max(best, run)
    return best


def place(person: User) -> tuple[str, str] | None:
    if not (person.city and person.state):
        return None
    return person.city.strip().casefold(), person.state.casefold()


@dataclass(frozen=True)
class Badge:
    name: str
    description: str


def badges(user: User, gifts: list[Donation], people_helped: int) -> list[Badge]:
    home = place(user)
    local = {g.post.user_id for g in gifts if home and place(g.post.user) == home}
    earned = [
        (len(gifts) >= 1, Badge("First gift", "Had a gift confirmed")),
        (people_helped >= 5, Badge("Helped 5", "Helped 5 different people")),
        (people_helped >= 25, Badge("Helped 25", "Helped 25 different people")),
        (len(local) >= 3, Badge("Local hero", "Helped 3 people in their own city")),
        (longest_streak(gifts) >= 4, Badge("On a roll", "Gave 4 weeks in a row")),
    ]
    return [badge for won, badge in earned if won]
