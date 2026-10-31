from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import StrEnum

from sqlalchemy.orm import aliased, contains_eager

from app.extensions import db
from app.models import Donation, User, utcnow
from app.rewards import rewardable_gifts, week_of

DONOR_MIN_AGE_DAYS = 3
PAIR_WEEKLY_CAP_CENTS = 20_000
TOP = 20


class Scope(StrEnum):
    GLOBAL = "global"
    STATE = "state"
    CITY = "city"


class Period(StrEnum):
    WEEK = "week"
    ALL = "all"


@dataclass(frozen=True)
class Row:
    rank: int
    user: User
    people: int


def _gifts(period: Period, now: datetime) -> list[Donation]:
    donor = aliased(User)
    query = (
        rewardable_gifts()
        .join(donor, Donation.donor)
        .options(contains_eager(Donation.donor.of_type(donor)))
        .where(
            donor.email_verified_at.is_not(None),
            donor.created_at <= now - timedelta(days=DONOR_MIN_AGE_DAYS),
        )
    )
    if period is Period.WEEK:
        start = datetime.combine(week_of(now), datetime.min.time(), tzinfo=now.tzinfo)
        query = query.where(Donation.resolved_at >= start)
    return list(db.session.scalars(query))


def _in_scope(person: User, viewer: User | None, scope: Scope) -> bool:
    if scope is Scope.GLOBAL or viewer is None:
        return True
    if (person.state or "").casefold() != (viewer.state or "").casefold():
        return False
    return scope is Scope.STATE or (
        (person.city or "").strip().casefold() == (viewer.city or "").strip().casefold()
    )


def rank(scope: Scope, period: Period, viewer: User | None) -> list[Row]:
    """Donors ranked by distinct people helped (ADR 0009); ties share a rank."""
    gifts = _gifts(period, utcnow())
    # A donor->recipient pair over $200 in one week is left out for that week (T11).
    pair_week: defaultdict[tuple[int, int, date], int] = defaultdict(int)
    for gift in gifts:
        when = gift.resolved_at or gift.created_at
        pair_week[gift.donor_id, gift.post.user_id, week_of(when)] += gift.amount_cents
    helped: defaultdict[int, set[int]] = defaultdict(set)
    donors: dict[int, User] = {}
    for gift in gifts:
        when = gift.resolved_at or gift.created_at
        key = (gift.donor_id, gift.post.user_id, week_of(when))
        if pair_week[key] > PAIR_WEEKLY_CAP_CENTS or not _in_scope(gift.donor, viewer, scope):
            continue
        helped[gift.donor_id].add(gift.post.user_id)
        donors[gift.donor_id] = gift.donor
    ordered = sorted(donors.values(), key=lambda u: (-len(helped[u.id]), u.username))
    rows: list[Row] = []
    for position, person in enumerate(ordered, 1):
        people = len(helped[person.id])
        tied = rows and rows[-1].people == people
        rows.append(Row(rows[-1].rank if tied else position, person, people))
    return rows
