"""Data hygiene for the golden set: it never leaks into a prompt, and real values never leave Godavari.

Two jobs:
  leakage   the test split's distinctive values (file numbers, PANs, mobiles, full names, addresses) must
            not appear in any prompt template, few-shot example or fixture the system can see. A golden
            file in a prompt scores itself; the number goes up and means nothing.
  export    what Kaagaz's product team receives (Day 36) is masked at the boundary: no full PAN, Aadhaar,
            mobile or name, addresses reduced to the PIN code. The full report stays in Godavari's
            environment (Day 24 owns the law behind it).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

PII_PATTERNS = {"pan": r"\b[A-Z]{5}\d{4}[A-Z]\b", "aadhaar": r"\b\d{4}\s?\d{4}\s?\d{4}\b", "mobile": r"\b[6-9]\d{9}\b"}
# Strong identifiers are unique to one file. Names and addresses repeat across real people (there are many
# RAVI TEJAs in Guntur), so a match on them is a "look at this" for a person, not proof of a leak.
STRONG_FIELDS = ("pan", "mobile")
WEAK_FIELDS = ("applicant_name", "address")
TEXT_SUFFIXES = {".txt", ".md", ".j2", ".jinja", ".toml", ".json", ".jsonl", ".yaml", ".yml", ".py"}


def distinctive_values(truth: dict[str, dict[str, Any]], split: str = "test",
                       fields: tuple[str, ...] = STRONG_FIELDS, with_id: bool = True) -> dict[str, list[str]]:
    """file_id -> the strings that would identify that golden file if they showed up somewhere else."""
    out: dict[str, list[str]] = {}
    for fid, rec in truth.items():
        if rec.get("split") != split:
            continue
        vals = ([fid] if with_id else []) + [str(rec["fields"].get(k)) for k in fields if rec["fields"].get(k)]
        out[fid] = [v for v in vals if len(v) >= 8]
    return out


def read_corpora(paths: list[Path]) -> dict[str, str]:
    """Every text file under the given files or folders, keyed by path."""
    corpora: dict[str, str] = {}
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
        for p in files:
            if p.suffix.lower() in TEXT_SUFFIXES and "__pycache__" not in p.parts:
                corpora[str(p)] = p.read_text(encoding="utf-8", errors="replace")
    return corpora


def leaks(truth: dict[str, dict[str, Any]], corpora: dict[str, str], weak: bool = False) -> list[tuple[str, str, str]]:
    """(corpus, golden file, the value found). Empty means clean. weak=True looks for names and addresses."""
    found: list[tuple[str, str, str]] = []
    values_by_file = (distinctive_values(truth, fields=WEAK_FIELDS, with_id=False) if weak
                      else distinctive_values(truth))
    for fid, values in values_by_file.items():
        for name, text in corpora.items():
            upper = text.upper()
            for v in values:
                if v.upper() in upper:
                    found.append((name, fid, v))
    return found


def split_overlap(truth: dict[str, dict[str, Any]], other_ids: set[str]) -> set[str]:
    return {fid for fid, rec in truth.items() if rec.get("split") == "test"} & other_ids


def mask(field_name: str, value: str | None) -> str | None:
    if value is None:
        return None
    if field_name == "pan":
        return value[:2] + "*" * max(0, len(value) - 3) + value[-1:]
    if field_name in ("applicant_name", "co_applicant_name"):
        return " ".join(part[0] + "." for part in value.split())
    if field_name == "mobile":
        return "******" + value[-4:]
    if field_name == "address":
        m = re.search(r"\b\d{6}\b", value)
        return f"[address, PIN {m.group(0)}]" if m else "[address]"
    if field_name == "date_of_birth":
        return "**-**-" + value[-4:]
    return value


def export_rows(field_rows: list[Any]) -> list[dict[str, Any]]:
    """The confidently wrong fields, masked, for the vendor's product team. Strata and statuses travel; values do not."""
    rows: list[dict[str, Any]] = []
    for r in field_rows:
        if r.status != "confident_wrong":
            continue
        rows.append({"file": r.file_id, "product": r.product, "branch": r.branch, "channel": r.channel,
                     "language": r.language, "field": r.field, "model_read": mask(r.field, r.pred),
                     "label": mask(r.field, r.label), "confidence": r.confidence, "route": r.route})
    return rows


def pii_hits(text: str) -> list[tuple[str, str]]:
    return [(k, m.group(0)) for k, p in PII_PATTERNS.items() for m in re.finditer(p, text)]
