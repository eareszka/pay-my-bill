from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import StrEnum

from sqlalchemy import Select, select
from sqlalchemy.orm import aliased, contains_eager

from app.extensions import db
from app.models import Donation, DonationStatus, User, utcnow
from app.rewards import MIN_ACCOUNT_AGE_DAYS, place, rewardable_gifts, week_of

PAIR_WEEKLY_CAP_CENTS = 20_000
TOP = 20

PairWeek = tuple[int, int, date]


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


def _since(query: Select[Donation], period: Period, now: datetime) -> Select[Donation]:
    if period is Period.ALL:
        return query
    start = datetime.combine(week_of(now), datetime.min.time(), tzinfo=now.tzinfo)
    return query.where(Donation.resolved_at >= start)


def _pair_week(gift: Donation) -> PairWeek:
    return gift.donor_id, gift.post.user_id, week_of(gift.resolved_at or gift.created_at)


def _over_cap(period: Period, now: datetime) -> set[PairWeek]:
    # Every confirmed gift counts toward the $200 pair cap, even ones that earn
    # nothing (a removed post), so the cap can't be dodged (T11).
    totals: defaultdict[PairWeek, int] = defaultdict(int)
    query = select(Donation).join(Donation.post).options(contains_eager(Donation.post))
    query = query.where(Donation.status == DonationStatus.CONFIRMED)
    for gift in db.session.scalars(_since(query, period, now)):
        totals[_pair_week(gift)] += gift.amount_cents
    return {key for key, cents in totals.items() if cents > PAIR_WEEKLY_CAP_CENTS}


def _gifts(period: Period, now: datetime) -> list[Donation]:
    donor = aliased(User)
    query = (
        rewardable_gifts()
        .join(donor, Donation.donor)
        .options(contains_eager(Donation.donor.of_type(donor)))
        .where(
            donor.email_verified_at.is_not(None),
            donor.created_at <= now - timedelta(days=MIN_ACCOUNT_AGE_DAYS),
        )
    )
    return list(db.session.scalars(_since(query, period, now)))


def _in_scope(person: User, viewer: User | None, scope: Scope) -> bool:
    if scope is Scope.GLOBAL or viewer is None:
        return True
    mine, theirs = place(viewer), place(person)
    if mine is None or theirs is None:
        return False
    return theirs[1] == mine[1] if scope is Scope.STATE else theirs == mine


def rank(scope: Scope, period: Period, viewer: User | None) -> list[Row]:
    """Donors ranked by distinct people helped (ADR 0009); ties share a rank."""
    now = utcnow()
    capped = _over_cap(period, now)
    helped: defaultdict[int, set[int]] = defaultdict(set)
    donors: dict[int, User] = {}
    for gift in _gifts(period, now):
        if _pair_week(gift) in capped or not _in_scope(gift.donor, viewer, scope):
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
