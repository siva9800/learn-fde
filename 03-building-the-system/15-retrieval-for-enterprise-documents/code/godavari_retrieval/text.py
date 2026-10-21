"""Text analysis: the tokenizers, the transliteration fold, and the PAN token.

Two analyzers, on purpose, because they stand for two different things:

* ``lexical_terms`` is the analyzer YOU control (BM25's). It keeps identifiers whole (circular
  numbers, file numbers, PAN tokens, clause numbers), keeps Telugu script words whole, and folds the
  spelling variants Godavari's staff use when they write Telugu in Latin letters.
* ``dense_terms`` imitates what a general-purpose subword embedding model does to the same text: it
  breaks identifiers into pieces and applies no folding. The dense stand-in (dense.py) is built on it.
"""

from __future__ import annotations

import hashlib
import hmac
import re

TELUGU = "ఀ-౿"            # the whole Telugu block, vowel signs (category Mn/Mc) included

# Order matters: identifiers are matched before ordinary words.
_LEXICAL_RE = re.compile(
    r"(?P<circ>[A-Z]{2,4}/[A-Z]{2,4}/\d{4}/\d{3})"      # GFL/CO/2025/027, GFL/CMP/2026/004
    r"|(?P<file>GF-\d{5})"                              # loan file numbers
    r"|(?P<pantok>pan_[0-9a-f]{12})"                    # keyed PAN tokens (never the PAN itself)
    r"|(?P<clause>\b\d{1,2}(?:\.\d{1,2}){1,2}\b)"       # clause numbers 4.2, 3.1.2
    rf"|(?P<tel>[{TELUGU}]+)"                           # Telugu script, kept whole
    r"|(?P<word>[A-Za-z0-9]+)",
    re.IGNORECASE,
)

PAN_RE = re.compile(r"\b[A-Z]{3}[PCHFATBLJG][A-Z]\d{4}[A-Z]\b")   # PAN shape: 4th letter is the holder type

STOPWORDS = frozenset(
    "a an and are as at be by for from has have in is it its of on or that the this to was were will "
    "with what which who whom how can may must should shall not no any all per than then there their "
    "they i we you our your me my do does did into under over about only also if".split()
)

# Spelling variants of transliterated Telugu collapse to one key: aadaayam, aadayam, adayam -> adayam.
_FOLDS = (("aa", "a"), ("ee", "i"), ("ii", "i"), ("oo", "u"), ("uu", "u"),
          ("th", "t"), ("dh", "d"), ("kh", "k"), ("gh", "g"), ("bh", "b"), ("ph", "p"))


def fold(word: str) -> str:
    """Fold one lowercase Latin word. Applied to index and query alike, so it only has to be consistent."""
    w = word
    for a, b in _FOLDS:
        w = w.replace(a, b)
    if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]                                      # proofs -> proof, documents -> document
    return w


def lexical_terms(text: str) -> list[str]:
    """BM25's analyzer: identifiers whole, Telugu whole, Latin words lowercased and folded."""
    out: list[str] = []
    for m in _LEXICAL_RE.finditer(text):
        kind = m.lastgroup
        tok = m.group(0)
        if kind in ("circ", "file"):
            out.append(tok.upper())
        elif kind in ("pantok", "clause", "tel"):
            out.append(tok.lower() if kind == "pantok" else tok)
        else:
            low = tok.lower()
            if low in STOPWORDS:
                continue
            out.append(fold(low))
    return out


_DENSE_RE = re.compile(rf"[{TELUGU}]+|[a-z]+|\d+")


def dense_terms(text: str) -> list[str]:
    """What a subword model sees: lowercase pieces; identifiers fall apart into letters and digits."""
    return [t for t in _DENSE_RE.findall(text.lower()) if t not in STOPWORDS]


def naive_terms(text: str) -> list[str]:
    r"""The tokenizer people write first: ``\w+``. Kept only to show what it does to Telugu (section 02.4)."""
    return re.findall(r"\w+", text.lower())


# ---------------------------------------------------------------------------------------------------
# PAN: the index never holds a PAN. It holds a keyed token, and the query is tokenised the same way.
# In production the key is in the customer's KMS (Day 25); here it is a demo constant.
DEMO_PAN_KEY = b"godavari-demo-key-not-for-production"


def pan_token(pan: str, key: bytes = DEMO_PAN_KEY) -> str:
    digest = hmac.new(key, pan.strip().upper().encode("ascii"), hashlib.sha256).hexdigest()
    return f"pan_{digest[:12]}"


def tokenise_pans(text: str, key: bytes = DEMO_PAN_KEY) -> tuple[str, int]:
    """Replace every PAN-shaped string in a query with its token. Returns (text, how many replaced)."""
    count = 0

    def _sub(m: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return pan_token(m.group(0), key)

    return PAN_RE.sub(_sub, text), count


def redact_pans(text: str) -> str:
    """For logs: a PAN in a query is replaced by a fixed marker, never stored."""
    return PAN_RE.sub("[PAN]", text)


def normalise_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()
