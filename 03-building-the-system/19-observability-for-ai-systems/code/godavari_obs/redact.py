"""The logging boundary: what may enter the trace store, and the proof that nothing else does.

Two layers, in this order:

  1. An allowlist of attribute keys, each with a validator: an enumeration, an identifier pattern, a number. A key
     that is not on the list is dropped. A value that does not fit its key's validator is dropped. No key accepts free
     text, which is the only reliable way to keep customer names out: a name has no pattern a regex can find, so the
     schema must not have a place where one could go.
  2. Scanners over everything that survived: PAN, an unmasked Aadhaar number (twelve digits passing Day 11's Verhoeff
     check), a mobile number, an e-mail address, each bounded so that hex ids and hashes do not trip them. A hit quarantines the whole span. It should never fire; when it does,
     the validator for some key is too loose, and that is a bug to fix the same day.

What is dropped is counted by key and reason, never by value. Key names are themselves checked before they are
counted, because a key built from data (f"value:{pan}") would otherwise carry the PAN into the counter.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from . import paths  # noqa: F401  (puts Day 11 and Day 18 on the path)
from godavari_review.corrections import REASONS
from intake.routing import MANDATORY_FIELDS, Route
from intake.validators import verhoeff_valid

Validator = Callable[[Any], bool]


def pattern(rx: str) -> Validator:
    comp = re.compile(rf"^(?:{rx})$")
    return lambda v: isinstance(v, str) and comp.fullmatch(v) is not None


def one_of(*values: str) -> Validator:
    allowed = frozenset(values)
    return lambda v: isinstance(v, str) and v in allowed


def number(lo: float = 0.0, hi: float = 1e9) -> Validator:
    return lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and lo <= v <= hi


def integer(lo: int = 0, hi: int = 10**9) -> Validator:
    return lambda v: isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def boolean(v: Any) -> bool:
    return isinstance(v, bool)


def list_of(inner: Validator, max_len: int = 64) -> Validator:
    return lambda v: isinstance(v, list) and len(v) <= max_len and all(inner(x) for x in v)


FILE_ID = pattern(r"GF-\d{5}")
RULE_ID = pattern(r"(TW|GL|ENV|KYC|ADDR)(-[A-Z0-9]+){1,3}")
FIELD = one_of(*sorted({f for fs in MANDATORY_FIELDS.values() for f in fs}))
MODEL = pattern(r"[a-z][a-z0-9]*(-[a-z0-9.]+)+( \[run [a-z0-9-]+\])?")
HEX = pattern(r"[0-9a-f]{8,64}")
ANALYST = pattern(r"[HV]\d")                  # the simulation's pseudonyms; production uses a keyed pseudonym
REASON = one_of(*[r for r in REASONS if r != "other"])   # "other" carries the analyst's words: free text, never here

SCHEMA: dict[str, Validator] = {
    # the file and its pages
    "kaagaz.file.id": FILE_ID,
    "kaagaz.file.branch_code": pattern(r"[A-Z]{3}\d{2}"),
    "kaagaz.file.product": one_of("two-wheeler", "gold"),
    "kaagaz.file.channel": one_of("sftp_scan", "phone_photo", "mixed"),
    "kaagaz.file.pages": integer(0, 2000),
    "kaagaz.file.pages_to_model": integer(0, 2000),
    "kaagaz.file.bundle_sha256": HEX,
    "kaagaz.file.outcome": one_of("written to core", "sent back", "blocked"),
    "kaagaz.run": pattern(r"pilot-week-\d"),
    "kaagaz.prompt.release": pattern(r"[a-z]+@\d+\.\d+\.\d+\+[a-z0-9-]+"),
    "kaagaz.page_filter": one_of("off", "statement-continuation-v1"),
    # model calls: OpenTelemetry names first, then ours
    "gen_ai.operation.name": one_of("chat", "retrieval"),
    "gen_ai.provider.name": pattern(r"[a-z][a-z0-9._]{1,30}"),
    "gen_ai.request.model": MODEL,
    "gen_ai.usage.input_tokens": integer(),
    "gen_ai.usage.output_tokens": integer(),
    "gen_ai.usage.cache_read.input_tokens": integer(),
    "gen_ai.usage.cache_write.input_tokens": integer(),
    "gen_ai.prompt.name": one_of("classify", "extract"),
    "gen_ai.prompt.version": pattern(r"[a-z]+-v\d+"),
    "gen_ai.data_source.id": one_of("godavari-policy-register"),
    "error.type": one_of("rate_limited", "overloaded", "server_error", "timeout", "circuit_open", "bad_request",
                         "spend_cap", "stale_directory"),
    "kaagaz.llm.stage": one_of("classify", "escalate", "extract", "repair"),
    "kaagaz.llm.tier": one_of("small", "large"),
    "kaagaz.llm.attempt": integer(0, 20),
    "kaagaz.llm.outcome": one_of("ok", "store_hit", "rate_limited", "overloaded", "server_error", "timeout",
                                 "circuit_open", "bad_request", "spend_cap"),
    "kaagaz.llm.page": integer(0, 2000),
    "kaagaz.llm.calls": integer(),
    "kaagaz.cost.inr": number(0, 10_000),
    "kaagaz.cost.estimated_inr": number(0, 10_000),
    # the pipeline (Day 11)
    "kaagaz.model.name": MODEL,
    "kaagaz.model.fields_unsure": integer(0, 100),
    "kaagaz.model.pages_unclassified": integer(0, 2000),
    "kaagaz.rules.product": one_of("two-wheeler", "gold"),
    "kaagaz.rules.version": pattern(r"\d+\.\d+"),
    "kaagaz.rules.status": one_of("draft", "reviewed-draft", "signed"),
    "kaagaz.rules.fingerprint": HEX,
    "kaagaz.rules.fired": list_of(RULE_ID),
    "kaagaz.rules.send_back": integer(0, 100),
    "kaagaz.rules.review": integer(0, 100),
    "kaagaz.rules.block": integer(0, 100),
    "kaagaz.envelope.fired": list_of(RULE_ID),
    "kaagaz.route": one_of(*[r.value for r in Route]),
    "kaagaz.note.corrected": boolean,
    # the review screen (Day 18)
    "kaagaz.review.analyst": ANALYST,
    "kaagaz.review.fields_shown": integer(0, 100),
    "kaagaz.review.accepted": integer(0, 100),
    "kaagaz.review.confirmed": integer(0, 100),
    "kaagaz.review.corrected": integer(0, 100),
    "kaagaz.review.keyed": integer(0, 100),
    "kaagaz.review.not_in_file": integer(0, 100),
    "kaagaz.review.forced_field": FIELD,
    "kaagaz.review.forced_seconds": number(0, 86_400),
    "kaagaz.review.queue_wait_h": number(0, 10_000),
    "kaagaz.review.bands_version": pattern(r"bands-policy-\d+\.\d+"),
    # feedback events: one per correction. The values stay in Day 18's screen log, inside Godavari's boundary.
    "kaagaz.feedback.field": FIELD,
    "kaagaz.feedback.reason": REASON,
    "kaagaz.feedback.band": one_of("auto_accept", "review", "reject"),
    "kaagaz.feedback.stratum": one_of("printed", "handwritten_telugu"),
    "kaagaz.feedback.action": one_of("corrected", "keyed", "not_in_file"),
    "kaagaz.feedback.content_change": boolean,
    "kaagaz.feedback.confidence_bucket": one_of("0.0-0.5", "0.5-0.7", "0.7-0.85", "0.85-0.95", "0.95-1.0"),
    # the core write (Day 11's push, Day 16's write window)
    "kaagaz.core.action": one_of("created", "exists"),
    "kaagaz.core.held_for_window": boolean,
    "kaagaz.core.record": pattern(r"CORE-\d{6}"),
    # retrieval (Day 15)
    "kaagaz.retrieval.user_role": one_of("creditops", "compliance", "branch", "service"),
    "kaagaz.retrieval.results": integer(0, 100),
    "kaagaz.retrieval.total_matches": integer(0, 100_000),
    "kaagaz.retrieval.notices": integer(0, 100),
    "kaagaz.retrieval.snapshot_age_h": number(0, 10_000),
}
EVENT_NAMES = frozenset({"feedback"})

# Token boundaries exclude letters, digits and a decimal point, so a hex trace id, a SHA-256 or the digits after the
# point in a rupee amount never look like a mobile number or an Aadhaar number.
_B, _A = r"(?<![0-9A-Za-z.])", r"(?![0-9A-Za-z]|\.\d)"
_PAN = re.compile(rf"{_B}[A-Z]{{5}}[0-9]{{4}}[A-Z]{_A}")
_MOBILE = re.compile(rf"{_B}[6-9]\d{{9}}{_A}")
_AADHAAR = re.compile(rf"{_B}(\d{{4}})[ -]?(\d{{4}})[ -]?(\d{{4}}){_A}")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_SAFE_KEY = re.compile(r"^[a-z_][a-z0-9_.]{0,60}$")
SPAN_NAME = re.compile(r"^(loan_file|intake|classify|extract|pipeline\.read|rules|route|review|core\.write|"
                       r"chat [a-z0-9.\-]+|retrieval godavari-policy-register)$")


def pii_hits(text: str) -> list[str]:
    """Which kinds of identifier appear in the text: never the identifiers themselves."""
    kinds = []
    if _PAN.search(text):
        kinds.append("pan")
    if any(verhoeff_valid("".join(m.groups())) and m.group(1)[0] not in "01" for m in _AADHAAR.finditer(text)):
        kinds.append("aadhaar")            # twelve digits, first digit 2 to 9, passing the Verhoeff check (Day 11)
    if _MOBILE.search(text):
        kinds.append("mobile")
    if _EMAIL.search(text):
        kinds.append("email")
    return kinds


@dataclass
class RedactionReport:
    dropped: Counter[str] = field(default_factory=Counter)       # "key: reason" -> count
    quarantined: Counter[str] = field(default_factory=Counter)   # span name -> count


def _key_label(key: object) -> str:
    return key if isinstance(key, str) and _SAFE_KEY.match(key) else "<unsafe key name>"


def clean(attrs: dict[str, Any], report: RedactionReport) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in attrs.items():
        check = SCHEMA.get(k) if isinstance(k, str) else None
        if check is None:
            report.dropped[f"{_key_label(k)}: not on the allowlist"] += 1
        elif not check(v):
            report.dropped[f"{k}: value does not fit the key"] += 1
        else:
            out[k] = v
    return out


def admit(name: str, attrs: dict[str, Any], events: list[dict[str, Any]],
          report: RedactionReport) -> tuple[dict[str, Any], list[dict[str, Any]]] | None:
    """The cleaned attributes and events of one span, or None if the span must not be stored at all."""
    if not SPAN_NAME.match(name):           # span names are code-defined and low-cardinality: never a value
        report.quarantined["<span name not on the list>"] += 1
        return None
    kept = clean(attrs, report)
    kept_events = []
    for e in events:
        if e.get("name") not in EVENT_NAMES:
            report.dropped[f"event {_key_label(e.get('name'))}: not on the allowlist"] += 1
            continue
        kept_events.append({"name": e["name"], "at": e["at"], "attrs": clean(e.get("attrs", {}), report)})
    blob = json.dumps([kept, [ev["attrs"] for ev in kept_events]], ensure_ascii=False, sort_keys=True)
    if pii_hits(blob):
        report.quarantined[name] += 1
        return None
    return kept, kept_events
