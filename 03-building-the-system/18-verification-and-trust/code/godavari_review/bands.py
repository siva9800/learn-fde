"""Confidence routing, tuned on the golden set: three bands per field and per stratum, and what each one costs.

  auto-accept  pre-filled and shown with its source; no action needed on the field; the file is still approved by
               a named analyst (decision D07), and auto-accepted fields are spot-checked (sampler.py)
  review       highlighted with its source; the analyst must confirm or correct it
  reject       the value is not offered; the analyst keys it from the page (the model's "unsure" lands here)

A deterministic finding on a field (Day 11's cross-checks, the quote check, formats, lookups) always means review.
The bands decide only among fields that code had nothing to say about, which is exactly where the confidence number
is the only signal left. Thresholds are fitted on Day 14's development split and confirmed on its test split.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from .evidence import FieldEvidence
from .paths import CODE
from evals.stats import wilson

POLICY_PATH = CODE / "band_policy.json"


class Band(StrEnum):
    AUTO = "auto_accept"
    REVIEW = "review"
    REJECT = "reject"


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def grid(policy: dict[str, Any]) -> list[float]:
    g = policy["grid"]
    n = round((g["high"] - g["low"]) / g["step"])
    return [round(g["low"] + i * g["step"], 2) for i in range(n + 1)]


@dataclass
class CellBands:
    field: str
    stratum: str
    accept_at: float | None          # None: no auto-accept band in this cell
    reject_below: float              # 0.0: only "unsure" is rejected
    status: str                      # auto, no_auto_band, withdrawn
    reason: str
    dev_n: int = 0
    dev_auto_n: int = 0
    review_dev_n: int = 0
    review_dev_errors: int = 0
    test: dict[str, Any] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.field}|{self.stratum}"

    def review_risk(self) -> float:
        """Upper 95 percent bound on the share of wrong values among this cell's review-band fields (development)."""
        return wilson(self.review_dev_errors, self.review_dev_n)[1] if self.review_dev_n else 1.0


def candidates(rows: Iterable[FieldEvidence]) -> list[FieldEvidence]:
    """The population the bands decide about: a value exists and no deterministic finding names the field."""
    return [r for r in rows if r.value is not None and not r.det_findings]


def fit(dev_rows: list[FieldEvidence], policy: dict[str, Any]) -> dict[tuple[str, str], CellBands]:
    """Per cell: the lowest confidence above which the development candidates are all correct (with enough of them),
    and the confidence below which they are too often wrong to be worth showing."""
    if any(r.split != "dev" for r in dev_rows):
        raise ValueError("thresholds are fitted on the development split only (Day 14, section 02.5)")
    by_cell: dict[tuple[str, str], list[FieldEvidence]] = defaultdict(list)
    for r in dev_rows:
        by_cell[r.cell].append(r)
    auto, rej = policy["auto_accept"], policy["reject"]
    out: dict[tuple[str, str], CellBands] = {}
    for cell, rows in sorted(by_cell.items()):
        cand = candidates(rows)
        accept_at: float | None = None
        for t in grid(policy):
            above = [r for r in cand if r.confidence >= t]
            if len(above) < auto["min_support_dev"]:
                break
            if sum(not r.correct for r in above) <= auto["max_dev_errors"]:
                # Never accept below the lowest confidence development has shown correct: no extrapolation.
                accept_at = max(t, math.floor(min(r.confidence for r in above) * 100) / 100)
                break
        reject_below = 0.0
        for t in grid(policy):
            below = [r for r in cand if r.confidence < t]
            if len(below) >= rej["min_support_dev"] and sum(r.correct for r in below) / len(below) < rej["below_accuracy"]:
                reject_below = t
        if accept_at is None:
            wrong = sum(not r.correct for r in cand)
            reason = (f"no threshold has {auto['min_support_dev']} or more development candidates above it, all "
                      f"correct ({len(cand)} candidates, {wrong} wrong)")
            status, n_auto = "no_auto_band", 0
        else:
            n_auto = sum(r.confidence >= accept_at for r in cand)
            reason = f"all {n_auto} development candidates at or above {accept_at:.2f} correct"
            status = "auto"
        cb = CellBands(cell[0], cell[1], accept_at, reject_below, status, reason, dev_n=len(rows), dev_auto_n=n_auto)
        review_rows = [r for r in rows if band_for(r, {cell: cb}) == Band.REVIEW]
        cb.review_dev_n, cb.review_dev_errors = len(review_rows), sum(not r.correct for r in review_rows)
        out[cell] = cb
    return out


def band_for(row: FieldEvidence, bands: dict[tuple[str, str], CellBands]) -> Band:
    """The band one field lands in. A cell nobody fitted fails closed to review."""
    if row.value is None:
        return Band.REJECT
    cb = bands.get(row.cell)
    if cb is None:
        return Band.REVIEW
    if row.confidence < cb.reject_below:
        return Band.REJECT
    if row.det_findings:
        return Band.REVIEW
    if cb.status == "auto" and cb.accept_at is not None and row.confidence >= cb.accept_at:
        return Band.AUTO
    return Band.REVIEW


def confirm(test_rows: list[FieldEvidence], bands: dict[tuple[str, str], CellBands],
            policy: dict[str, Any]) -> dict[str, Any]:
    """Apply the development-fitted bands to the test split. A cell whose auto band lets a wrong value through is
    withdrawn (it can only lose automation here, never gain it). Returns the pooled numbers before and after."""
    if any(r.split != "test" for r in test_rows):
        raise ValueError("confirmation runs on the test split")
    limit = policy["confirm"]["max_test_errors_per_cell"]
    before = [r for r in test_rows if band_for(r, bands) == Band.AUTO]
    for cb in bands.values():
        mine = [r for r in test_rows if r.cell == (cb.field, cb.stratum)]
        auto_rows = [r for r in mine if band_for(r, bands) == Band.AUTO]
        errs = [r for r in auto_rows if not r.correct]
        cb.test = {"n": len(mine), "auto": len(auto_rows), "auto_errors": len(errs),
                   "auto_upper": round(wilson(len(errs), len(auto_rows))[1], 4) if auto_rows else None,
                   "examples": [f"{r.file_id} read {r.value!r}, truth {r.label!r} at {r.confidence:.2f} from {r.evidence!r}"
                                for r in errs[:3]]}
    withdrawn: list[str] = []
    blocked: list[str] = []
    proof = policy["proof_before_auto"]
    for cb in bands.values():
        if cb.status == "auto" and cb.test["auto_errors"] > limit:
            cb.status = "withdrawn"
            cb.reason = f"confirmation failed: {cb.test['auto_errors']} wrong of {cb.test['auto']} auto-accepted test fields"
            withdrawn.append(cb.key)
        elif cb.status == "auto" and cb.stratum in proof["strata"] and (cb.test["auto_upper"] or 1.0) > proof["max_upper_bound"]:
            need = fields_to_prove(proof["max_upper_bound"])
            cb.status = "blocked_until_proven"
            cb.reason = (f"{cb.test['auto_errors']} wrong of {cb.test['auto']} auto-accepted test fields, upper bound "
                         f"{cb.test['auto_upper']:.1%}; proof needs {need} or more with none wrong")
            blocked.append(cb.key)
    after = [r for r in test_rows if band_for(r, bands) == Band.AUTO]
    k_b, k_a = sum(not r.correct for r in before), sum(not r.correct for r in after)
    return {"auto_before": len(before), "auto_errors_before": k_b, "upper_before": wilson(k_b, len(before))[1],
            "auto_after": len(after), "auto_errors_after": k_a, "upper_after": wilson(k_a, len(after))[1],
            "pooled_limit": policy["confirm"]["pooled_upper_bound_max"], "withdrawn": withdrawn, "blocked": blocked}


def fields_to_prove(upper: float) -> int:
    """The smallest number of fields, all correct, whose 95 percent Wilson upper bound is at or below `upper`."""
    n = 1
    while wilson(0, n)[1] > upper:
        n += 1
    return n


def standing_forced_look(bands: dict[tuple[str, str], CellBands]) -> set[tuple[str, str]]:
    """Cells whose confirmation failed: every file with such a field gets that field as its forced look."""
    return {k for k, cb in bands.items() if cb.status == "withdrawn"}


# --- What each way of assigning bands costs --------------------------------------------------------------
def placeholder_band(row: FieldEvidence) -> Band:
    """Day 11's placeholder thresholds as Day 14 measured them: any finding on the field means a look."""
    if row.value is None:
        return Band.REJECT
    return Band.REVIEW if row.placeholder_flagged else Band.AUTO


def everything_reviewed(row: FieldEvidence) -> Band:
    return Band.REJECT if row.value is None else Band.REVIEW


def cost(rows: list[FieldEvidence], band_of: Callable[[FieldEvidence], Band], policy: dict[str, Any]) -> dict[str, Any]:
    """Analyst seconds and wrong values per band, for one way of assigning bands."""
    s = policy["seconds"]
    per: dict[str, dict[str, float]] = {b.value: {"fields": 0, "wrong": 0, "seconds": 0.0} for b in Band}
    for r in rows:
        b = band_of(r)
        cell = per[b.value]
        cell["fields"] += 1
        cell["wrong"] += not r.correct
        if b == Band.AUTO:
            cell["seconds"] += s["auto_glance"]
        elif b == Band.REVIEW:
            cell["seconds"] += s["review_confirm"] + (s["review_correct_extra"] if not r.correct else 0)
        else:
            cell["seconds"] += s["key_in"]
    files = len({r.file_id for r in rows})
    total = sum(c["seconds"] for c in per.values())
    return {"files": files, "bands": per, "minutes_per_file": total / 60 / files if files else 0.0,
            "hours_per_month": total / files * policy["files_per_month"] / 3600 if files else 0.0,
            "auto_wrong": per[Band.AUTO.value]["wrong"], "review_wrong": per[Band.REVIEW.value]["wrong"]}


def save(bands: dict[tuple[str, str], CellBands], summary: dict[str, Any], policy: dict[str, Any], path: Path) -> None:
    doc = {"policy_version": policy["version"], "fitted_on": "Day 14 development split (50 files)",
           "confirmed_on": "Day 14 test split (150 files)", "summary": summary,
           "cells": {cb.key: asdict(cb) for cb in bands.values()}}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def load(path: Path) -> dict[tuple[str, str], CellBands]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    return {(c["field"], c["stratum"]): CellBands(**c) for c in doc["cells"].values()}
