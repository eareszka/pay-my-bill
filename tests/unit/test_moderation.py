import pytest

from app.moderation import flagged_keywords, is_flagged


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
    ],
)
def test_ignores_everyday_asks(text: str) -> None:
    assert not is_flagged(text)


def test_checks_every_text_and_reports_matches() -> None:
    assert flagged_keywords("Rent help", "for my Business and my business LLC") == [
        "business",
        "llc",
    ]
