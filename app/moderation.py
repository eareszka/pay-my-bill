import re

# Business, startup, and investment fundraising is banned (PRD, T3). A match only sends
# the post to the review queue, so the list can lean toward false positives.
FUNDRAISING_KEYWORDS = (
    "invest",
    "investing",
    "investment",
    "investor",
    "investors",
    "startup",
    "start-up",
    "business",
    "equity",
    "seed",
    "llc",
    "inventory",
    "pre-order",
    "preorder",
    "launch",
    "crowdfund",
    "crowdfunding",
    "shares",
    "roi",
    "venture",
    "franchise",
    "stock",
    "stocks",
    "crypto",
)

_PATTERN = re.compile(
    r"(?<![\w-])(?:" + "|".join(re.escape(k) for k in FUNDRAISING_KEYWORDS) + r")(?![\w-])",
    re.IGNORECASE,
)


def flagged_keywords(*texts: str) -> list[str]:
    return sorted({m.group(0).lower() for text in texts for m in _PATTERN.finditer(text)})


def is_flagged(*texts: str) -> bool:
    return bool(flagged_keywords(*texts))
