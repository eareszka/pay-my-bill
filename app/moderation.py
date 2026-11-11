import re
import unicodedata

# Business, startup, and investment fundraising is banned (PRD, T3). A match on a post
# only sends it to the review queue, so the list can lean toward false positives.
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
# Added after the security audit (#158). Posts only: a results update is refused, not
# reviewed, so everyday words like "shop" would leave a poster stuck rewording a thank-you.
POST_ONLY_KEYWORDS = (
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
POST_ONLY_PHRASES = (r"my brand(?![ -]new)",)
# Everyday phrases that contain a listed word, taken out before matching.
_EVERYDAY = re.compile(
    r"(?<![a-z0-9])(?:los angeles|capital one|stock(?:s|ed|ing)? up|non-?profits?)(?![a-z0-9])"
)

# Inflections ("invested", "startups", "businesses", "launching") still match. Hyphens
# count as word breaks, so "small-business" and "seed-funding" match too.
_SUFFIXES = r"(?:s|es|ed|d|ing|ment|ments|or|ors|er|ers)?"


def _pattern(words: tuple[str, ...], phrases: tuple[str, ...] = ()) -> re.Pattern[str]:
    alternatives = [*(re.escape(w) for w in words), *phrases]
    return re.compile(
        r"(?<![a-z0-9])(?:" + "|".join(alternatives) + r")" + _SUFFIXES + r"(?![a-z0-9])"
    )


_POST_PATTERN = _pattern(FUNDRAISING_KEYWORDS + POST_ONLY_KEYWORDS, POST_ONLY_PHRASES)
_UPDATE_PATTERN = _pattern(FUNDRAISING_KEYWORDS)

# Disguises seen in the audit: hidden characters, look-alike letters from other
# alphabets, digits and symbols for letters, and letters spaced out one at a time (#158).
_LOOKALIKES = str.maketrans(
    "\u0430\u0435\u043e\u0440\u0441\u0443\u0445\u0456\u0458\u0455\u0501\u04cf\u043a\u043c\u0442\u043d\u0432\u03bf\u03b1\u03b5\u03b9\u03ba\u03bd\u03c1\u03c4\u03c5",
    "aeopcyxijsdlkmthboaeiknptu",
)
_LEET = str.maketrans("013457@$", "oieastas")
_WORD = re.compile(r"[a-z0-9@$]*[a-z][a-z0-9@$]*")
_GAP = r"[ .,\-_*\u00b7|/]+"
_SPACED = re.compile(r"(?<![a-z0-9])[a-z0-9@$](?:" + _GAP + r"[a-z0-9@$](?![a-z0-9])){2,}")
# "bus!ness", "bus|ness": an i stand-in only when letters sit on both sides.
_I_INSIDE = re.compile(r"(?<=[a-z])[!|](?=[a-z])")


def _visible(c: str) -> bool:
    # Format characters (zero-width spaces, joiners, soft hyphens) and the combining
    # grapheme joiner render as nothing, so they can hide inside a word.
    return unicodedata.category(c) != "Cf" and c != "\u034f"


def normalize(text: str) -> str:
    """Fold a post's text so disguised words read as the plain words."""
    text = "".join(c for c in unicodedata.normalize("NFKC", text) if _visible(c))
    text = text.lower().translate(_LOOKALIKES)
    text = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    # Join letters spaced out one at a time ("b.u.s.i.n.e.s.s"), then read digits and
    # symbols inside words as letters ("bus1ness"). Plain numbers like $500 stay as they are.
    text = _SPACED.sub(lambda m: re.sub(_GAP, "", m.group(0)), text)
    text = _I_INSIDE.sub("i", text)
    text = _WORD.sub(lambda m: m.group(0).translate(_LEET), text)
    text = re.sub(r"\s+", " ", text)
    return _EVERYDAY.sub(" ", text)


def flagged_keywords(*texts: str, pattern: re.Pattern[str] = _POST_PATTERN) -> list[str]:
    found = (m.group(0) for text in texts for m in pattern.finditer(normalize(text)))
    return sorted(set(found))


def is_flagged(*texts: str) -> bool:
    return bool(flagged_keywords(*texts))


def update_flagged_keywords(text: str) -> list[str]:
    """The narrower check for results updates, which are refused rather than reviewed."""
    return flagged_keywords(text, pattern=_UPDATE_PATTERN)
