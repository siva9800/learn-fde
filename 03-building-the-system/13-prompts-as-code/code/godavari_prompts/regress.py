"""Score extraction results against labelled files: correct, unsure (null) or wrong, per field.

A small regression check for prompt pull requests. It is deliberately plain: three outcomes per field,
counts not percentages on a set this small, and slices you can name. The golden set, labelling rules,
adjudication, judges and confidence intervals are Day 14's.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from statistics import mean
from typing import Any

from .pipeline import FileResult
from .synth import LoanFile, fields_for


def normalise(fld: str, value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    if fld in ("requested_amount", "monthly_income", "on_road_price"):
        return "".join(ch for ch in text if ch.isdigit()) or None
    if fld == "net_weight_g":
        try:
            return f"{float(text):.1f}"
        except ValueError:
            return text
    return " ".join(text.split())


def outcome(fld: str, predicted: dict[str, Any], truth: str) -> str:
    got = normalise(fld, predicted.get("value"))
    if got is None:
        return "unsure"
    return "correct" if got == normalise(fld, truth) else "wrong"


def set_hash(files: list[LoanFile]) -> str:
    h = hashlib.sha256()
    for f in sorted(files, key=lambda x: x.file_id):
        h.update(f.file_id.encode() + f.sha256.encode() + repr(sorted(f.truth.items())).encode())
    return h.hexdigest()


def score(results: list[FileResult], files: list[LoanFile], set_name: str, *,
          only: str | None = None) -> dict[str, Any]:
    """Per-field counts. `only` restricts to one slice: "co_applicant", "telugu_income", "kukatpally"..."""
    by_id = {f.file_id: f for f in files}
    per_field: dict[str, dict[str, int]] = defaultdict(lambda: {"n": 0, "correct": 0, "unsure": 0, "wrong": 0})
    picked = []
    for r in results:
        f = by_id[r.file_id]
        if only == "co_applicant" and f.truth["co_applicant_name"] == "none":
            continue
        if only == "telugu_income" and not f.telugu_income:
            continue
        picked.append(r)
        for fld in fields_for(f.product):
            o = outcome(fld, r.fields[fld], f.truth[fld])
            per_field[fld]["n"] += 1
            per_field[fld][o] += 1
    total = sum(v["n"] for v in per_field.values()) or 1
    return {
        "set": set_name, "set_sha256": set_hash(files), "n_files": len(picked),
        "per_field": dict(sorted(per_field.items())),
        "correct_rate": round(sum(v["correct"] for v in per_field.values()) / total, 4),
        "wrong_rate": round(sum(v["wrong"] for v in per_field.values()) / total, 4),
        "input_tokens_per_file": {tier: round(mean(r.tokens(tier) for r in picked)) if picked else 0
                                  for tier in ("small", "large")},
    }


def by_page_band(results: list[FileResult], files: list[LoanFile], bands: list[tuple[int, int]]) -> list[tuple[str, int, int]]:
    """Accuracy by where the evidence sits in the file: (band, fields there, fields read correctly)."""
    by_id = {f.file_id: f for f in files}
    rows = []
    for lo, hi in bands:
        n = ok = 0
        for r in results:
            f = by_id[r.file_id]
            for fld in fields_for(f.product):
                page = _evidence_page(f, fld)
                if page is not None and lo <= page <= hi:
                    n += 1
                    ok += outcome(fld, r.fields[fld], f.truth[fld]) == "correct"
        rows.append((f"pages {lo}-{hi}", n, ok))
    return rows


def _evidence_page(f: LoanFile, fld: str) -> int | None:
    """Where the right answer is printed (the last page that carries it, as the annexure overrides the form)."""
    where = {"applicant_name": "application_form", "applicant_pan": "pan_card", "requested_amount": "application_form",
             "monthly_income": "income_proof", "on_road_price": "dealer_quotation", "net_weight_g": "gold_appraisal",
             "business_name": "application_form", "employer_name": "income_proof"}
    if fld == "co_applicant_name":
        doc = "co_applicant_kyc" if f.truth[fld] != "none" else "application_form"
    else:
        doc = where[fld]
    pages = [p.number for p in f.pages if p.doc == doc]
    return pages[0] if pages else None


def table(evaluation: dict[str, Any]) -> str:
    lines = [f"{'field':<20}{'n':>4}{'correct':>9}{'unsure':>8}{'wrong':>7}"]
    for fld, c in evaluation["per_field"].items():
        lines.append(f"{fld:<20}{c['n']:>4}{c['correct']:>9}{c['unsure']:>8}{c['wrong']:>7}")
    lines.append(f"{'all fields':<20}{'':>4}{evaluation['correct_rate']:>9.1%}{'':>8}{evaluation['wrong_rate']:>7.1%}")
    return "\n".join(lines)
