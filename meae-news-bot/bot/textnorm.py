"""Text normalisation and keyword matching for English and Arabic.

Both the article text and the keywords go through `normalize`, so matching
ignores case, Latin accents (Erdoğan = Erdogan), Arabic diacritics, tatweel
and the usual spelling variants (أ/إ/آ → ا, ى → ي, ة → ه, Persian ی/ک).
"""

import re
import unicodedata
from dataclasses import dataclass, field

_ARABIC = re.compile(r"[؀-ۿ]")
_SEPARATORS = r"[\s\-‐-―_/]+"

_CHAR_MAP = str.maketrans(
    {
        "ى": "ي",
        "ی": "ي",
        "ک": "ك",
        "ة": "ه",
        "ـ": None,  # tatweel
        "ı": "i",  # Turkish dotless i
        **{chr(0x0660 + d): str(d) for d in range(10)},  # Arabic-Indic digits
        **{chr(0x06F0 + d): str(d) for d in range(10)},  # Persian digits
    }
)


def _is_droppable_mark(ch: str) -> bool:
    """Latin accents and Arabic harakat/hamza marks; other scripts are left alone."""
    cp = ord(ch)
    return (
        0x0300 <= cp <= 0x036F
        or 0x0610 <= cp <= 0x061A
        or 0x064B <= cp <= 0x065F
        or cp == 0x0670
        or 0x06D6 <= cp <= 0x06ED
    )


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not _is_droppable_mark(ch))
    text = text.translate(_CHAR_MAP).casefold()
    return re.sub(r"\s+", " ", text).strip()


def is_arabic(text: str) -> bool:
    return bool(_ARABIC.search(text))


def term_regex(term: str) -> str:
    """Regex for one already-normalised term, matched as a whole word.

    Arabic attaches some words to the front of nouns (و، ف، ب، ل، ك، ال), so
    for Arabic terms those prefixes are allowed: أرامكو also matches وأرامكو,
    بأرامكو and للأرامكو.
    """
    parts = [re.escape(p) for p in re.split(_SEPARATORS, term) if p]
    core = _SEPARATORS.join(parts)
    if is_arabic(term):
        alternatives = [rf"(?:[وف])?(?:بال|كال|لل|ال|[بكل])?{core}"]
        if term.startswith("ال") and len(term) > 3:
            # ل + الجزيرة is written للجزيرة: the alef of ال is dropped.
            alternatives.append(rf"(?:[وف])?لل{core[2:]}")
        body = "|".join(alternatives)
    else:
        body = core
    return rf"(?<!\w)(?:{body})(?!\w)"


def _compile(terms: list[str]) -> re.Pattern | None:
    normalized = [normalize(t) for t in terms]
    normalized = [t for t in normalized if t]
    if not normalized:
        return None
    return re.compile("|".join(term_regex(t) for t in normalized))


@dataclass
class KeywordRule:
    """A user's keyword: a main name, other spellings, and words to exclude."""

    id: int
    user_id: int
    name: str
    variants: list[str] = field(default_factory=list)
    excludes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._include = _compile([self.name, *self.variants])
        self._exclude = _compile(self.excludes)

    @property
    def terms(self) -> list[str]:
        return [self.name, *self.variants]

    def is_excluded(self, norm_text: str) -> bool:
        return bool(self._exclude and self._exclude.search(norm_text))

    def matches(self, norm_text: str) -> bool:
        if not self._include or not self._include.search(norm_text):
            return False
        return not self.is_excluded(norm_text)


# ---------------------------------------------------------------- user input

MAX_TERMS = 10
MAX_EXCLUDES = 10
MIN_TERM_LENGTH = 2
MAX_TERM_LENGTH = 80

_EXCLUDE_PREFIXES = ("-", "−", "–", "—")


class KeywordInputError(ValueError):
    """`code` is an i18n key explaining what was wrong."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass
class ParsedKeyword:
    name: str
    variants: list[str]
    excludes: list[str]


def parse_keyword_input(text: str) -> ParsedKeyword:
    """Parse "Aramco, أرامكو, Saudi Aramco, -stock" into name, variants and excludes.

    Items are separated by commas (English or Arabic), semicolons or new lines.
    Items that start with a minus sign are words to exclude.
    """
    items = [item.strip() for item in re.split(r"[,،;\n]", text)]
    terms: list[str] = []
    excludes: list[str] = []
    seen_terms: set[str] = set()
    seen_excludes: set[str] = set()
    for item in items:
        if not item:
            continue
        target, seen = terms, seen_terms
        if item.startswith(_EXCLUDE_PREFIXES):
            item = item.lstrip("".join(_EXCLUDE_PREFIXES)).strip()
            target, seen = excludes, seen_excludes
        item = re.sub(r"\s+", " ", item.strip("\"'«»“”"))
        norm = normalize(item)
        if not norm:
            continue
        if len(norm) < MIN_TERM_LENGTH:
            raise KeywordInputError("err_too_short")
        if len(item) > MAX_TERM_LENGTH:
            raise KeywordInputError("err_too_long")
        if norm not in seen:
            seen.add(norm)
            target.append(item)
    if not terms:
        raise KeywordInputError("err_no_name")
    if len(terms) > MAX_TERMS or len(excludes) > MAX_EXCLUDES:
        raise KeywordInputError("err_too_many")
    return ParsedKeyword(name=terms[0], variants=terms[1:], excludes=excludes)


def format_keyword_input(name: str, variants: list[str], excludes: list[str]) -> str:
    """The inverse of parse_keyword_input, used to show a keyword for editing."""
    return ", ".join([name, *variants, *(f"-{e}" for e in excludes)])
