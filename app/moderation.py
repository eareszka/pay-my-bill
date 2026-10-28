import re

# Business, startup, and investment fundraising is banned (PRD, T3). A match only sends
# the post to the review queue, so the list can lean toward false positives.
FUNDRAISING_KEYWORDS = (
    "invest",
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
    "shares",
    "roi",
    "venture",
    "franchise",
    "stock",
    "crypto",
)

# Inflections ("invested", "startups", "businesses", "launching") still match. Hyphens
# count as word breaks, so "small-business" and "seed-funding" match too.
_SUFFIXES = r"(?:s|es|ed|d|ing|ment|ments|or|ors|er|ers)?"
_PATTERN = re.compile(
    r"(?<![a-z0-9])(?:"
    + "|".join(re.escape(k) for k in FUNDRAISING_KEYWORDS)
    + r")"
    + _SUFFIXES
    + r"(?![a-z0-9])",
    re.IGNORECASE,
)


def flagged_keywords(*texts: str) -> list[str]:
    return sorted({m.group(0).lower() for text in texts for m in _PATTERN.finditer(text)})


def is_flagged(*texts: str) -> bool:
    return bool(flagged_keywords(*texts))
