import pytest

from app.moderation import flagged_keywords, is_flagged, normalize


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
        "busi​ness",
        "busіness",
        "Вusiness",
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
        "Café supplies for my mom",
        "U.S. citizen",
        "Workshop fees for school",
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
        ("busi​ness", "business"),
        ("ｂusiness", "business"),
        ("café", "cafe"),
        ("need   $500\nfor rent", "need $500 for rent"),
    ],
)
def test_normalize_folds_disguises(text: str, plain: str) -> None:
    assert normalize(text) == plain
