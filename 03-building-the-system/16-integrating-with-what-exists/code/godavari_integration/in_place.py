"""The data you are not allowed to copy: read it in place, for one file, for one person, and forget it.

The customer's name, PAN and mobile live in the core. Our components (the queue, the journal, the logs,
the reconciliation report, anything a model sees in a prompt it did not need) keep a masked form or a
hash. When an analyst opens a file, OnDemandApplicant reads the identifiers from the core through the
SOAP port, for that analyst, for a stated purpose; keeps them in process memory for at most the TTL the
mapping's data class allows; and logs the view every time, cache hit or not (the CISO's "who viewed this
file", finding A6). Nothing here writes an identifier to disk.

The contract terms behind this (the DPA, retention, subprocessors) are Day 23's; the law (DPDP Act, RBI
outsourcing directions, residency) is Day 24's. This module is the engineering that makes those terms true.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .clock import BusinessClock
from .soap.port import CorePort
from .translate import Mapping

PURPOSES = frozenset({"analyst_review", "branch_callback", "audit_query"})
IDENTIFIERS = ("APPL_NM", "PAN_NO", "MOB_NO")


def mask_pan(pan: str) -> str:
    return "XXXXX" + pan[5:9] + "X" if len(pan) == 10 else "XXXXXXXXXX"


def mask_mobile(mobile: str) -> str:
    return "XXXXXX" + mobile[-4:] if len(mobile) == 10 else "XXXXXXXXXX"


def mask_name(name: str) -> str:
    return " ".join(part[0] + "." for part in name.split() if part)


def token(value: str, salt: str = "godavari-sbx") -> str:
    """A stable stand-in for joining records without the value itself (salted SHA-256, 16 hex)."""
    return hashlib.sha256(f"{salt}|{value}".encode()).hexdigest()[:16]


def safe_for_log(mapping: Mapping, core_record: dict[str, str]) -> dict[str, str]:
    """Direct identifiers out, everything else as is. Used for every log line and the report."""
    out = {}
    hidden = mapping.direct_identifier_fields()
    for k, v in core_record.items():
        if k in hidden:
            out[k] = "PAN " + mask_pan(v) if k == "PAN_NO" else f"<{k} withheld>"
        else:
            out[k] = v
    return out


@dataclass(frozen=True)
class View:
    at: str
    analyst: str
    file_no: str
    purpose: str
    cache_hit: bool


@dataclass
class OnDemandApplicant:
    port: CorePort
    mapping: Mapping
    clock: BusinessClock
    ttl_s: float = 900.0
    now: Callable[[], float] = time.monotonic
    views: list[View] = field(default_factory=list)
    _cache: dict[tuple[str, str], tuple[float, dict[str, str]]] = field(default_factory=dict)

    def view(self, file_no: str, analyst_id: str, purpose: str) -> dict[str, str]:
        if purpose not in PURPOSES:
            raise PermissionError(f"purpose {purpose!r} is not one the compliance head allowed")
        if not analyst_id:
            raise PermissionError("a named analyst opens a file; a service account does not")
        key = (file_no, analyst_id)
        hit = key in self._cache and self.now() - self._cache[key][0] < self.ttl_s
        if not hit:
            apps = [s for s in self.port.get_by_file_number(file_no) if not s.is_shell]
            if len(apps) != 1:
                raise LookupError(f"{file_no}: {len(apps)} applications in the core; nothing to show")
            detail = self.port.get_application(apps[0].appl_id)
            self._cache[key] = (self.now(), {k: detail.get(k, "") for k in IDENTIFIERS})
        self.views.append(View(self.clock.now().strftime("%Y%m%d%H%M%S"), analyst_id, file_no, purpose, hit))
        return dict(self._cache[key][1])

    def purge(self) -> int:
        expired = [k for k, (t, _) in self._cache.items() if self.now() - t >= self.ttl_s]
        for k in expired:
            del self._cache[k]
        return len(expired)

    def cached_files(self) -> list[str]:
        return sorted({k[0] for k in self._cache})


def describe_cache_policy(mapping: Mapping) -> list[tuple[str, str, str, str]]:
    """(data class, may it leave Godavari's systems, where it may be stored, cache) for the report."""
    rows = []
    for name, rules in mapping.data_classes.items():
        rows.append((name, "yes" if rules["copy_out_of_godavari_systems"] else "no",
                     str(rules["store_in_kaagaz_components"]), str(rules["cache"])))
    return rows


def contains_identifier(text: str, values: list[str]) -> list[str]:
    """Which of these raw values appear in a blob of text (a log, a journal dump, a report)."""
    return [v for v in values if v and v in text]


__all__ = ["OnDemandApplicant", "PURPOSES", "View", "contains_identifier", "describe_cache_policy", "mask_mobile",
           "mask_name", "mask_pan", "safe_for_log", "token", "Any"]
