import time

import pytest

from app.moderation import flagged_keywords, is_flagged, normalize, update_flagged_keywords


@pytest.mark.parametrize(
    "text",
    [
        "Help launch my startup",
        "Seed money for my LLC",
        "Looking for INVESTORS",
        "Pre-order my new product",
        "Great ROI on this",
        "Restock inventory for my shop",
        "Buying shares",
        "start-up costs",
        "Help my small-business",
        "seed-funding round",
        "I invested in a rig",
        "Two businesses to fund",
        "Launching my brand",
        "My LLCs need cash",
        "crypto-mining rig",
        # Disguised (#158).
        "bus1ness",
        "b.u.s.i.n.e.s.s",
        "B U S I N E S S plan",
        "busi\u200bness",
        "bus\u0456ness",
        "\u0412usiness",
        "st0ck",
        "r0i",
        "c0mp@ny",
        # Added words (#158).
        "fund my company and get a return",
        "angel funding for my app",
        "Startup capital",
        "Help my companies grow",
        "Very profitable idea",
        "Great return on your money",
        "Open my own shop",
        "Grow my brand",
        "bus!ness",
        "b,u,s,i,n,e,s,s",
        "busi\u034fness",
        "busi\u180eness",
    ],
)
def test_flags_fundraising(text: str) -> None:
    assert is_flagged(text)


@pytest.mark.parametrize(
    "text",
    [
        "I'm too busy to work overtime",
        "Need help with rent this month",
        "Want the new Zelda game",
        "Lunch money for the week",
        "My kids share a room",
        "seedless grapes",
        "busy-ness",
        "I need $500 for rent",
        "Shopping for groceries",
        "My brand new baby needs a crib",
        "3 kids, 1 job, 2 cars",
        "Caf\u00e9 supplies for my mom",
        "U.S. citizen",
        "Workshop fees for school",
        "Moving to Los Angeles for a new job",
        "Capital One froze my card",
        "Stocking up on diapers",
        "Rent at the non-profit shelter",
        "My brand-new baby needs a crib",
        "Thanks! I paid it off!",
    ],
)
def test_ignores_everyday_asks(text: str) -> None:
    assert not is_flagged(text)


def test_checks_every_text_and_reports_matches() -> None:
    assert flagged_keywords("Rent help", "for my Business and my business LLC") == [
        "business",
        "llc",
    ]


@pytest.mark.parametrize(
    ("text", "plain"),
    [
        ("bus1ness", "business"),
        ("B.U.S.I.N.E.S.S", "business"),
        ("busi\u200bness", "business"),
        ("\uff42usiness", "business"),
        ("caf\u00e9", "cafe"),
        ("need   $500\nfor rent", "need $500 for rent"),
    ],
)
def test_normalize_folds_disguises(text: str, plain: str) -> None:
    assert normalize(text) == plain


def test_updates_use_only_the_original_list() -> None:
    assert update_flagged_keywords("Went to the shop with Angel, my company paid the rest") == []
    assert update_flagged_keywords("Now b.u.s.i.n.e.s.s time") == ["business"]


@pytest.mark.parametrize(
    "text",
    [
        "b\nu\ns\ni\nn\ne\ns\ns",
        "b\tu\ts\ti\tn\te\ts\ts",
        "b:u:s:i:n:e:s:s",
        "b+u+s+i+n+e+s+s",
        "bu5!ness",
        "b,u,s,!,n,e,s,s",
        "busi\ufe0fness",
        "busi\u3164ness",
        "busi\u2800ness",
        "bus\u0131ness",
        "bus\u0457ness",
    ],
)
def test_flags_the_re_test_misses(text: str) -> None:
    # From the audit's second re-test (#158).
    assert is_flagged(text)


def test_long_runs_without_letters_stay_fast() -> None:
    # A run with no letter used to be rescanned from every position (#158).
    started = time.perf_counter()
    for run in ("1" * 50_000, "$" * 50_000, "1@" * 25_000):
        normalize(run)
    # Quadratic took about 10 s for these; linear is well under, even with coverage on.
    assert time.perf_counter() - started < 2
