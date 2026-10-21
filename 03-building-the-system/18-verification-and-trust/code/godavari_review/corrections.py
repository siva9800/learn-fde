"""Every correction is data: captured with its reason, and sent where it is useful.

  to Day 14   a correction that changes content (not format) is a candidate example for the development split, in
              Day 14's shape, marked single-labeller: it needs a second label and adjudication before it is truth
  to Day 19   every correction, format-only ones included, is an event for the dashboards (correction rate per field,
              per branch, per band, per prompt version)

A correction without a reason is refused. "Format only" is a reason, and it is not a model error: Day 14's
normaliser already forgives it, so it never becomes an eval example, but it says something about the display.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from evals.normalise import norm_equal

REASONS = ("misread character", "wrong page or document", "not in the file", "spelling or transliteration",
           "format only", "model unsure: keyed from the page", "other")


@dataclass(frozen=True)
class Correction:
    file_id: str
    field: str
    stratum: str
    band: str
    model_value: str | None
    analyst_value: str | None
    reason: str
    analyst: str
    at: str
    confidence: float
    model: str
    rules_fingerprint: str
    bands_version: str

    def __post_init__(self) -> None:
        if self.reason not in REASONS:
            raise ValueError(f"a correction needs a reason from the list, not {self.reason!r}")
        if self.reason == "other":
            raise ValueError("'other' needs the analyst's words; use the screen's text box (not simulated here)")

    @property
    def content_change(self) -> bool:
        return not norm_equal(self.field, self.model_value, self.analyst_value)


def reason_for(field_name: str, model_value: str | None, new_value: str | None, evidence: str) -> str:
    """What the simulated analyst picks. On the screen she picks it; nothing guesses it for her."""
    if model_value is None:
        return "not in the file" if new_value is None else "model unsure: keyed from the page"
    if norm_equal(field_name, model_value, new_value):
        return "format only"
    if any(ch.isalpha() for ch in evidence.split(":")[-1]) and any(ch.isdigit() for ch in evidence):
        return "misread character"
    if field_name in ("applicant_name", "address"):
        return "spelling or transliteration"
    return "misread character"


def to_dev_candidate(c: Correction) -> dict[str, Any]:
    """Day 14's development split takes pilot corrections as candidates, never as test files (Day 14, 08.5)."""
    return {"file_id": c.file_id, "field": c.field, "split": "dev", "source": "pilot correction",
            "model_value": c.model_value, "label_a": c.analyst_value, "labeller_a": c.analyst, "reason": c.reason,
            "status": "single-labeller; second label and adjudication pending (Day 14, adjudication rule 2)"}


def to_event(c: Correction) -> dict[str, Any]:
    return {"event": "correction", **asdict(c), "content_change": c.content_change}
