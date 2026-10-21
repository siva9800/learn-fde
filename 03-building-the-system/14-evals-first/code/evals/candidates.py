"""Candidate model changes to put through the golden set and the gate.

Every candidate wraps Day 11's `StubModel` (imported, not copied). Two layers:

  the change   what the candidate does differently: nothing (baseline, rerun) or a trimmed prompt.
  run noise    Day 11's stub is perfectly repeatable; a real model is not. Re-run the same prompt on the
               same file and the reported confidences move a little, and now and then a smudged character
               on a handwritten page or a phone photo is read differently. `RunNoise` adds that, seeded by
               a run id, to every candidate, so the gate is tested against what a real model does to it.

  baseline   stub-model-v1 as run on main (run "main").
  rerun      the same model, run again (run "rerun-1"): nothing changed, so the gate must pass it.
  trimmed    a prompt change in the style of Day 13's extraction 2.1.0 token trim: the instruction about
             handwritten Telugu income declarations is gone, so the figure is read at twelve times its
             value, and the reminder to "say unsure" is gone, so handwritten pages come back about 0.08
             more confident than before. The average barely moves; one stratum breaks.
"""

from __future__ import annotations

import random
import re
from collections.abc import Sequence
from dataclasses import replace

from .day11 import DAY11_CODE  # noqa: F401
from .labels import CONFUSE
from intake.catalogue import FieldValue, LoanBundle, ModelOutput
from intake.model import ExtractionModel, StubModel

MISREAD_RATE = 0.008        # per field, on handwritten pages and phone photos only
CONFIDENCE_JITTER = 0.03


class TrimmedPromptStub:
    """The deliberately worse change. See the module docstring."""

    name = "stub-model-v1 + trimmed prompt (2.1.0-style)"
    INCOME_FIELDS = ("monthly_income", "form_monthly_income")

    def __init__(self) -> None:
        self.inner = StubModel()

    def read(self, bundle: LoanBundle) -> ModelOutput:
        out = self.inner.read(bundle)
        fields: dict[str, FieldValue] = {}
        for k, v in out.fields.items():
            page = bundle.page(v.page) if v.page is not None else None
            if v.value is None or page is None:
                fields[k] = v
                continue
            value, conf = v.value, v.confidence
            if page.handwritten:
                conf = min(0.99, conf + 0.08)
            if k in self.INCOME_FIELDS and page.telugu and ":" in v.evidence:
                read = re.sub(r"\D", "", v.evidence.split(":", 1)[1])
                if read:
                    value, conf = str(int(read) * 12), max(conf, 0.91)
            fields[k] = replace(v, value=value, confidence=round(conf, 2))
        return replace(out, model_name=self.name, fields=fields)

    def draft_note(self, bundle: LoanBundle, findings: Sequence[tuple[str, str]]) -> str:
        return self.inner.draft_note(bundle, findings)


class RunNoise:
    """One run of a model: the same model, with the run-to-run variation a real model shows."""

    def __init__(self, inner: ExtractionModel, run_id: str) -> None:
        self.inner = inner
        self.run_id = run_id
        self.name = f"{inner.name} [run {run_id}]"

    def read(self, bundle: LoanBundle) -> ModelOutput:
        out = self.inner.read(bundle)
        rng = random.Random(f"{self.run_id}-{bundle.file_id}")
        fields: dict[str, FieldValue] = {}
        for k in sorted(out.fields):
            v = out.fields[k]
            jitter = rng.uniform(-CONFIDENCE_JITTER, CONFIDENCE_JITTER)
            misread = rng.random() < MISREAD_RATE
            spot = rng.random()
            if v.value is None or v.page is None:
                fields[k] = v
                continue
            page = bundle.page(v.page)
            value = v.value
            if misread and page is not None and (page.handwritten or bundle.channel == "phone_photo"):
                spots = [i for i, ch in enumerate(value) if ch in CONFUSE]
                if spots:
                    i = spots[int(spot * len(spots))]
                    value = value[:i] + CONFUSE[value[i]] + value[i + 1:]
            conf = round(min(0.99, max(0.05, v.confidence + jitter)), 2)
            fields[k] = replace(v, value=value, confidence=conf)
        return replace(out, model_name=self.name, fields=fields)

    def draft_note(self, bundle: LoanBundle, findings: Sequence[tuple[str, str]]) -> str:
        return self.inner.draft_note(bundle, findings)


def build(name: str, run_id: str | None = None) -> ExtractionModel:
    """baseline (run 'main'), rerun (run 'rerun-1'), trimmed (run 'candidate-1'); `run_id` overrides."""
    if name == "baseline":
        return RunNoise(StubModel(), run_id or "main")
    if name == "rerun":
        return RunNoise(StubModel(), run_id or "rerun-1")
    if name == "trimmed":
        return RunNoise(TrimmedPromptStub(), run_id or "candidate-1")
    raise ValueError(f"unknown candidate {name!r}; use baseline, rerun or trimmed")
