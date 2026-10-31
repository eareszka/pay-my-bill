from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.models import Donation
from app.rewards import Progress, level_for, level_start, streak


@pytest.mark.parametrize(
    ("xp", "level"), [(0, 1), (99, 1), (100, 2), (299, 2), (300, 3), (600, 4), (1_000, 5)]
)
def test_level_thresholds(xp: int, level: int) -> None:
    assert level_for(xp) == level


def test_level_start() -> None:
    assert [level_start(n) for n in range(1, 6)] == [0, 100, 300, 600, 1_000]


def test_progress_toward_next_level() -> None:
    p = Progress(xp=340, people_helped=6)
    assert (p.level, p.next_level_at, p.percent) == (3, 600, 13)
    assert Progress(xp=0, people_helped=0).percent == 0


def gift_on(day: datetime) -> Donation:
    return Donation(created_at=day, resolved_at=day)


NOW = datetime(2026, 11, 18, 12, tzinfo=UTC)  # a Wednesday


@pytest.mark.parametrize(
    ("days_ago", "expected"),
    [
        ([], 0),
        ([0], 1),
        ([0, 7, 14], 3),
        ([7, 14], 2),  # nothing yet this week; last week still counts
        ([14, 21], 0),  # a full missed week breaks it
        ([0, 1, 2], 1),  # several gifts in one week count once
        ([0, 14], 1),
    ],
)
def test_streak(days_ago: list[int], expected: int) -> None:
    gifts = [gift_on(NOW - timedelta(days=d)) for d in days_ago]
    assert streak(gifts, now=NOW) == expected


def test_streak_handles_naive_times() -> None:
    assert streak([gift_on(NOW.replace(tzinfo=None))], now=NOW) == 1


def test_streak_week_boundaries_are_utc_mondays() -> None:
    sunday_late = datetime(2026, 11, 15, 23, 59, tzinfo=UTC)
    monday_early = datetime(2026, 11, 16, 0, 0, tzinfo=UTC)
    assert streak([gift_on(sunday_late), gift_on(monday_early)], now=NOW) == 2
    eastern = timezone(timedelta(hours=-5))
    # Monday 02:00 UTC is still Sunday evening in New York, but counts as Monday.
    assert streak([gift_on(monday_early.astimezone(eastern) + timedelta(hours=2))], now=NOW) == 1


def test_streak_counts_the_week_a_gift_was_confirmed() -> None:
    old_claim = Donation(created_at=NOW - timedelta(weeks=3), resolved_at=NOW)
    assert streak([old_claim], now=NOW) == 1
