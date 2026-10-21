"""One row per mandatory field: what the model read, where, how sure it said it was, and what code said about it.

The rows come from running Day 11's pipeline (imported) over Day 14's golden files (imported), scored with Day 14's
normaliser against Day 14's adjudicated truth file. Nothing is re-labelled here. The one thing this chapter needs
that Day 14's per-field report does not keep is the split between the two reasons a field can be flagged:

  det_findings   deterministic findings that name the field (a cross-check, the quote, a format, a lookup);
                 these always send the field to review, whatever its confidence
  confidence     the model's own number, the only input the bands below are fitted on
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from . import paths  # noqa: F401  (puts Day 11, Day 14 and Day 15 on the path)
from evals import candidates
from evals.day11 import RULESETS
from evals.golden import GoldenFile, bundle_sha256, select
from evals.harness import AS_OF
from evals.labels import source_page
from evals.normalise import norm_equal
from evals.store import load_truth, read_manifest
from intake.catalogue import LoanBundle
from intake.model import ExtractionModel
from intake.pipeline import FileResult, process
from intake.routing import MANDATORY_FIELDS

CONFIDENCE_RULE = "ENV-CONFIDENCE"     # Day 11's placeholder-threshold finding; the bands replace it


@dataclass(frozen=True)
class FieldEvidence:
    file_id: str
    split: str                  # dev, test or pilot
    product: str
    branch: str
    channel: str
    field: str
    stratum: str                # "handwritten_telugu" or "printed": a property of the field's source page
    value: str | None
    label: str | None           # the adjudicated truth (golden) or what is on the paper (pilot simulation)
    confidence: float
    page: int | None
    evidence: str
    det_findings: tuple[str, ...]
    placeholder_flagged: bool   # flagged under Day 11's placeholder thresholds (what Day 14 measured)

    @property
    def correct(self) -> bool:
        return norm_equal(self.field, self.value, self.label)

    @property
    def cell(self) -> tuple[str, str]:
        return (self.field, self.stratum)


def stratum_of(bundle: LoanBundle, field_name: str) -> str:
    src = source_page(bundle, field_name)
    return "handwritten_telugu" if src is not None and src.handwritten and src.telugu else "printed"


def rows_for(bundle: LoanBundle, result: FileResult, split: str, labels: dict[str, str | None]) -> list[FieldEvidence]:
    out = result.output
    assert out is not None
    rows: list[FieldEvidence] = []
    for name in MANDATORY_FIELDS[bundle.product]:
        fv = out.fields.get(name)
        named = [f for f in result.findings if f.field_name == name]
        rows.append(FieldEvidence(
            bundle.file_id, split, bundle.product, bundle.branch, bundle.channel, name, stratum_of(bundle, name),
            fv.value if fv else None, labels.get(name), fv.confidence if fv else 0.0, fv.page if fv else None,
            fv.evidence if fv else "", tuple(sorted({f.rule_id for f in named if f.rule_id != CONFIDENCE_RULE})),
            bool(named)))
    return rows


class PagesChanged(RuntimeError):
    pass


def golden_rows(model: ExtractionModel | None = None, splits: Iterable[str] = ("dev", "test")) -> list[FieldEvidence]:
    """Day 11's pipeline over Day 14's golden files. Refuses if a file's pages differ from what was labelled."""
    model = model or candidates.build("baseline")
    truth = load_truth()
    sha = {r["file_id"]: r["bundle_sha256"] for r in read_manifest()}
    test, dev = select()
    chosen: list[GoldenFile] = [gf for gf in (*dev, *test) if gf.split in set(splits)]
    rows: list[FieldEvidence] = []
    for gf in chosen:
        bundle, _hidden = gf.build()
        if bundle_sha256(bundle) != sha[gf.file_id]:
            raise PagesChanged(f"{gf.file_id}: pages differ from the ones the analysts labelled")
        result = process(bundle, model, RULESETS[gf.product], AS_OF)
        rows.extend(rows_for(bundle, result, gf.split, truth[gf.file_id]["fields"]))
    return rows


def crop(bundle: LoanBundle, page_no: int | None, quote: str, context: int = 1) -> tuple[int | None, list[tuple[int, str, bool]]]:
    """The text stand-in for an image crop: the quoted line and its neighbours, numbered, quote marked.

    A real deployment crops the page image at the OCR bounding box of the quote. The synthetic pages are text,
    so the "crop" is the lines around the quote. Either way the rule is the same: the analyst sees the source,
    not the model's restatement of it. Returns (line number of the quote, [(line no, text, is_quote_line)])."""
    page = bundle.page(page_no) if page_no is not None else None
    if page is None or not quote:
        return None, []
    lines = page.text.splitlines()
    hit = next((i for i, line in enumerate(lines) if quote.strip() and quote.strip() in line), None)
    if hit is None:
        return None, []
    lo, hi = max(0, hit - context), min(len(lines), hit + context + 1)
    return hit + 1, [(i + 1, lines[i], i == hit) for i in range(lo, hi)]
