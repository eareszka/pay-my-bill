import pytest

from app.rewards import Progress, level_for, level_start


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
