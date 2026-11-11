import re
import unicodedata

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
    # Added after the security audit (#158).
    "company",
    "companies",
    "funding",
    "capital",
    "profit",
    "profitable",
    "return on",
    "angel",
    "shop",
)
# Phrases that need more than a word list: "my brand" but not "my brand new".
FUNDRAISING_PHRASES = (r"my brand(?! new)",)

# Inflections ("invested", "startups", "businesses", "launching") still match. Hyphens
# count as word breaks, so "small-business" and "seed-funding" match too.
_SUFFIXES = r"(?:s|es|ed|d|ing|ment|ments|or|ors|er|ers)?"
_PATTERN = re.compile(
    r"(?<![a-z0-9])(?:"
    + "|".join([*(re.escape(k) for k in FUNDRAISING_KEYWORDS), *FUNDRAISING_PHRASES])
    + r")"
    + _SUFFIXES
    + r"(?![a-z0-9])",
    re.IGNORECASE,
)

# Disguises seen in the audit: hidden characters, look-alike letters from other
# alphabets, digits for letters, and letters spaced out with dots or dashes (#158).
_INVISIBLE = dict.fromkeys(map(ord, "­​‌‍⁠﻿"))
_LOOKALIKES = str.maketrans(
    "аеорсуухіјѕԁӏкмтнвАЕОРСУХІЈЅКМТНВοαεικνρτυΟΑΕΙΚΝΡΤΥ",
    "aeopcyyxijsdlkmthbAEOPCYXIJSKMTHBoaeiknptuOAEIKNPTY",
)
_LEET = str.maketrans("013457@$", "oieastas")
_WORD = re.compile(r"[a-z0-9@$]*[a-z][a-z0-9@$]*")
_SPACED = re.compile(r"(?<![a-z0-9])[a-z0-9@$](?:[ .\-_*·|/]+[a-z0-9@$](?![a-z0-9])){2,}")


def normalize(text: str) -> str:
    """Fold a post's text so disguised words read as the plain words."""
    text = unicodedata.normalize("NFKC", text).translate(_INVISIBLE).translate(_LOOKALIKES)
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    text = text.lower()
    # Join letters spaced out one at a time ("b.u.s.i.n.e.s.s"), then read digits and
    # symbols inside words as letters ("bus1ness"). Plain numbers like $500 stay as they are.
    text = _SPACED.sub(lambda m: re.sub(r"[ .\-_*·|/]+", "", m.group(0)), text)
    text = _WORD.sub(lambda m: m.group(0).translate(_LEET), text)
    return re.sub(r"\s+", " ", text)


def flagged_keywords(*texts: str) -> list[str]:
    found = (m.group(0).lower() for text in texts for m in _PATTERN.finditer(normalize(text)))
    return sorted(set(found))


def is_flagged(*texts: str) -> bool:
    return bool(flagged_keywords(*texts))
