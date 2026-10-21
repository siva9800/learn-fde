"""A dense-retrieval STAND-IN that runs offline with no model download. It is not an embedding model.

It has the two properties of a general-purpose embedding model that this chapter needs you to see:

* it matches PARAPHRASE: a small hand-written concept table maps "shop owner", "proprietor" and "trader" to one
  concept, "scooter" and "bike" to another, and Telugu-script words for income, proof and address to the same
  concepts, the way a multilingual model places them near each other;
* it is WEAK on identifiers and on Telugu written in Latin letters: it sees text the way a subword model does
  (``dense_terms``), so GFL/CO/2025/027 becomes "gfl co 2025 027", a PAN token becomes hex fragments, and
  "aadaayam" and "adayam" are unrelated strings (no folding; you do not control a hosted model's tokenizer).

Each text becomes a hashed, signed, L2-normalised sparse vector; similarity is the dot product (cosine). Search
is exact over the allowed chunks, so a filter can never starve it (section 06.4 explains why approximate
indexes behave differently). Swap in a real local model behind the same two methods (section 09.2).
"""

from __future__ import annotations

import hashlib
import math
from collections import Counter
from collections.abc import Sequence

from .chunking import Chunk
from .text import dense_terms

DIM = 2048
WORD_WEIGHT, CONCEPT_WEIGHT = 1.0, 2.0

_CONCEPT_WORDS: dict[str, tuple[str, ...]] = {
    "INCOME": ("income", "earnings", "earning", "earn", "ఆదాయ", "ఆదాయం"),
    "SALARY": ("salary", "salaried", "payslip", "payslips", "wages", "employee", "slips"),
    "PROOF": ("proof", "evidence", "documents", "document", "documentation", "రుజువు", "రుజువుగా"),
    "SELF_EMPLOYED": ("proprietor", "shopkeeper", "trader", "business", "merchant", "vendor", "shop"),
    "TWO_WHEELER": ("scooter", "bike", "motorcycle", "scooty", "wheeler"),
    "ADDRESS": ("address", "residence", "residential", "చిరునామా"),
    "RENT": ("rent", "rental", "lease", "tenancy", "tenant", "landlord", "అద్దె"),
    "AGREEMENT": ("agreement", "contract", "ఒప్పందం"),
    "GOLD": ("gold", "jewellery", "jewelry", "ornaments"),
    "LTV": ("ltv", "value"),
    "MASK": ("mask", "masking", "masked", "unmasked", "redact", "redacted", "redaction", "blackout", "మాస్క్"),
    "AADHAAR": ("aadhaar", "uid", "ఆధార్"),
    "STATEMENT": ("statement", "statements", "passbook", "బ్యాంకు"),
    "AGRICULTURE": ("farmer", "agriculture", "agricultural", "cultivator", "crop", "farming", "farm", "land"),
    "PENSION": ("pension", "pensioner", "retired"),
    "GIG": ("delivery", "gig", "platform", "payout", "payouts"),
    "DEALER": ("dealer", "showroom", "dealers"),
    "QUOTATION": ("quotation", "proforma", "invoice", "quote"),
    "DECLINED": ("declined", "decline", "reject", "rejected", "rejection"),
    "ACCEPTED": ("approved", "sanctioned", "accepted", "acceptable", "allowed"),
    "SENT_BACK": ("returned", "back"),
    "VERIFICATION": ("verification", "visit", "inspection"),
    "UTILITY_BILL": ("electricity", "water", "gas", "utility", "bill", "విద్యుత్", "బిల్లు"),
    "VALIDITY": ("valid", "validity", "expiry", "old", "older"),
    "TENURE": ("tenure", "months"),
    "AGE": ("age", "years"),
    "PHONE": ("whatsapp", "phone", "messaging", "mobile", "వాట్సాప్"),
    "CONSENT": ("consent", "agree", "agrees", "permission"),
    "REPEAT": ("repeat", "previous", "earlier", "prior"),
}
CONCEPTS: dict[str, str] = {w: c for c, ws in _CONCEPT_WORDS.items() for w in ws}
BIGRAM_CONCEPTS: dict[tuple[str, str], str] = {
    ("self", "employed"): "SELF_EMPLOYED", ("shop", "owner"): "SELF_EMPLOYED", ("two", "wheeler"): "TWO_WHEELER",
    ("bank", "statement"): "STATEMENT", ("co", "applicant"): "CO_APPLICANT", ("land", "record"): "AGRICULTURE",
    ("స్వయం", "ఉపాధి"): "SELF_EMPLOYED", ("field", "visit"): "VERIFICATION",
}


def concepts(terms: list[str]) -> list[str]:
    out = [CONCEPTS[t] for t in terms if t in CONCEPTS]
    out += [BIGRAM_CONCEPTS[p] for p in zip(terms, terms[1:]) if p in BIGRAM_CONCEPTS]
    return out


def _slot(feature: str) -> tuple[int, float]:
    h = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(h[:4], "little") % DIM, (1.0 if h[4] & 1 else -1.0)


def embed(text: str) -> dict[int, float]:
    terms = dense_terms(text)
    feats: Counter[str] = Counter()
    for t in terms:
        feats[f"w:{t}"] += WORD_WEIGHT
    for c in concepts(terms):
        feats[f"c:{c}"] += CONCEPT_WEIGHT
    vec: dict[int, float] = {}
    for f, w in feats.items():
        i, sign = _slot(f)
        vec[i] = vec.get(i, 0.0) + sign * (1 + math.log(w))
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {i: v / norm for i, v in vec.items()}


def dot(a: dict[int, float], b: dict[int, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(i, 0.0) for i, v in a.items())


class DenseIndex:
    def __init__(self, chunks: Sequence[Chunk]) -> None:
        self.vectors = [embed(c.index_text) for c in chunks]

    def search(self, query: str, allowed: set[int] | None = None, k: int = 50) -> list[tuple[int, float]]:
        q = embed(query)
        ids = range(len(self.vectors)) if allowed is None else allowed
        scored = [(i, dot(q, self.vectors[i])) for i in ids]
        scored = [(i, s) for i, s in scored if s > 0]
        return sorted(scored, key=lambda kv: (-kv[1], kv[0]))[:k]
