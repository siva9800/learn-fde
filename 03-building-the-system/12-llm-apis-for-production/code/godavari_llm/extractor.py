"""The model box of Day 11's diagram, made production-shaped: classify every page on the small tier,
extract fields from the pages that carry them on the large tier, check every answer against the page,
and assemble the file-level contract in code.

ExtractionModel is the seam Day 11 draws (code/intake/model.py in that chapter: `name` and `read(bundle)`).
Day 11's StubModel and its one-call AnthropicExtractionModel sit behind it; this class is the production
implementation of the same method, returning the Pydantic contract instead of Day 11's dataclasses, so the
rules downstream never know which one ran.
"""

from __future__ import annotations

import heapq
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, TypeVar

from .client import LLMClient, RetriesExhausted, StructuredResult, idempotency_key
from .contract import (SCHEMA_VERSION, AmountField, Doc, DocumentPresent, FieldResult, IncomeEvidence,
                       LoanFileExtraction, PageClassification, PageExtraction, TextField, provider_schema)
from .provider import ModelRequest, Tier, VirtualClock
from .retry import CircuitOpen
from .synthetic import SyntheticFile, SyntheticPage

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"
CLASSIFY_PROMPT_VERSION = "classify-v1"
EXTRACT_PROMPT_VERSION = "extract-v1"
EXTRACT_TYPES = {Doc.APPLICATION_FORM, Doc.PAN_CARD, Doc.CO_APPLICANT_KYC, Doc.INCOME_PROOF, Doc.BANK_STATEMENT}
ESCALATE_BELOW = 0.60      # classification confidence under this goes to the large tier
REVIEW_BELOW = 0.75        # a field under this confidence is flagged for the analyst (Day 18 owns the real threshold)
R = TypeVar("R")


class ExtractionModel(Protocol):
    """Day 11's seam, kept by name: bundle in, what the model read out. Raise Deferred to retry later."""

    name: str

    def read(self, bundle: SyntheticFile) -> LoanFileExtraction: ...


class Deferred(Exception):
    """The provider was unavailable (breaker open or retries exhausted). Re-queue the file; completed
    calls are in the response store, so the second pass pays only for what did not finish."""


def parse_amount(text: str) -> int | None:
    """'Loan amount requested: Rs. 1,25,000' -> 125000; 'SALARY ... 35,000.00' -> 35000. Last number wins."""
    digits, current = [], ""
    for ch in text + " ":
        if ch.isdigit():
            current += ch
        elif ch == "," and current:
            continue
        else:
            if current:
                digits.append(current)
                if ch == ".":       # a decimal point after digits: paise are not rupees ("Rs." is not one)
                    break
            current = ""
    return int(digits[-1]) if digits else None


def check_page(ext: PageExtraction, page_text: str) -> list[str]:
    """Valid shape, wrong content? These checks look for the cheap, certain signs. They are the API layer's
    share of Day 11's validation; cross-file and rule checks stay there."""
    problems = []
    for name in ("applicant_name", "applicant_pan", "co_applicant_name", "product", "requested_amount", "monthly_income"):
        f = getattr(ext, name)
        if f.value is None:
            continue
        if not f.evidence or f.evidence not in page_text:
            problems.append(f"{name}: the evidence text is not on the page")
        elif isinstance(f, AmountField) and parse_amount(f.evidence) != f.value:
            problems.append(f"{name}: value {f.value} does not match its evidence {f.evidence!r}")
        elif isinstance(f, TextField) and str(f.value).casefold() not in f.evidence.casefold():
            problems.append(f"{name}: value {f.value!r} is not in its evidence {f.evidence!r}")
    return problems


def pan_matches_surname(pan: str, name: str) -> bool:
    """Day 11's rule: for an individual, the fifth PAN character is the surname's initial."""
    parts = name.split()
    return bool(parts) and len(pan) == 10 and pan[4].upper() == parts[-1][0].upper()


class VirtualScheduler:
    """Runs a stage's calls on a fixed pool of concurrent slots, on virtual time. The production version is
    a worker pool with a semaphore; the arithmetic of waiting for a slot is the same."""

    def __init__(self, clock: VirtualClock, slots: int) -> None:
        self.clock = clock
        self.free = [0.0] * slots
        heapq.heapify(self.free)

    def run(self, tasks: list[Callable[[], R]], ready_at: float) -> tuple[list[R | Exception], float, float]:
        results: list[R | Exception] = []
        first_start, last_end = float("inf"), ready_at
        for task in tasks:
            start = max(heapq.heappop(self.free), ready_at)
            self.clock.set(start)
            try:
                results.append(task())
            except (CircuitOpen, RetriesExhausted) as e:
                results.append(e)
            end = self.clock.now()
            heapq.heappush(self.free, end)
            first_start, last_end = min(first_start, start), max(last_end, end)
        return results, (ready_at if first_start == float("inf") else first_start), last_end


@dataclass
class FileReport:
    file_id: str
    pages: int
    status: str = "done"                            # done | deferred
    classify_s: float = 0.0
    extract_s: float = 0.0
    started_at: float = 0.0
    finished_at: float = 0.0
    problems: dict[str, int] = field(default_factory=dict)
    extraction: LoanFileExtraction | None = None

    def count(self, what: str) -> None:
        self.problems[what] = self.problems.get(what, 0) + 1


class GodavariExtractor:
    name = "godavari-production-client"
    def __init__(self, client: LLMClient, scheduler: VirtualScheduler) -> None:
        self.client = client
        self.scheduler = scheduler
        self.classify_system = (PROMPTS / f"{CLASSIFY_PROMPT_VERSION}.txt").read_text(encoding="utf-8")
        self.extract_system = (PROMPTS / f"{EXTRACT_PROMPT_VERSION}.txt").read_text(encoding="utf-8")
        self.classify_schema = provider_schema(PageClassification)
        self.extract_schema = provider_schema(PageExtraction)
        self.page_keys: dict[str, tuple[str, int]] = {}   # idempotency key -> (file, page), for the evaluation

    # --- Day 11's seam -----------------------------------------------------------------------------
    def read(self, bundle: SyntheticFile) -> LoanFileExtraction:
        report = self.extract_with_report(bundle, ready_at=self.scheduler.clock.now())
        if report.extraction is None:
            raise Deferred(bundle.file_id)
        return report.extraction

    # --- the pipeline ------------------------------------------------------------------------------
    def _request(self, bundle: SyntheticFile, page: SyntheticPage, tier: Tier, task: str, user_text: str) -> ModelRequest:
        provider = self.client.provider
        system, schema, version = ((self.classify_system, self.classify_schema, CLASSIFY_PROMPT_VERSION) if task == "classify"
                                   else (self.extract_system, self.extract_schema, EXTRACT_PROMPT_VERSION))
        key = idempotency_key(file_id=bundle.file_id, page_no=page.number, page_sha256=page.sha256, stage=task,
                              prompt_version=version, schema_version=SCHEMA_VERSION, model=provider.model_for(tier))
        self.page_keys[key] = (bundle.file_id, page.number)
        image_estimate = 450 if task == "classify" else 1600
        est = (len(system) + len(json.dumps(schema)) + len(user_text)) // 4 + image_estimate
        return ModelRequest(tier=tier, system=system, user_text=user_text, page_ref=page.ref, json_schema=schema,
                            max_output_tokens=200 if task == "classify" else 1200,
                            timeout_s=15.0 if task == "classify" else 30.0, idempotency_key=key,
                            metadata={"task": task, "est_input_tokens": str(est)})

    def _classify(self, bundle: SyntheticFile, page: SyntheticPage, report: FileReport) -> tuple[Doc, float]:
        text = f"File {bundle.file_id}, page {page.number} of {len(bundle.pages)}. Classify this page."
        res: StructuredResult[PageClassification] = self.client.call_structured(
            self._request(bundle, page, Tier.SMALL, "classify", text), PageClassification,
            file_id=bundle.file_id, page=page.number, stage="classify")
        for p in res.problems:
            report.count(p)
        if res.parsed is not None and res.parsed.confidence >= ESCALATE_BELOW:
            return res.parsed.page_type, res.parsed.confidence
        report.count("escalated_to_large")                  # model tiering: the hard page gets the big model
        big = self.client.call_structured(self._request(bundle, page, Tier.LARGE, "classify", text), PageClassification,
                                          file_id=bundle.file_id, page=page.number, stage="escalate")
        if big.parsed is None:
            return Doc.UNKNOWN, 0.0
        return big.parsed.page_type, big.parsed.confidence

    def _extract_page(self, bundle: SyntheticFile, page: SyntheticPage, doc: Doc, report: FileReport) -> PageExtraction | None:
        text = f"File {bundle.file_id}, page {page.number}. This page was classified as {doc.value}. Extract the fields."
        request = self._request(bundle, page, Tier.LARGE, "extract", text)
        res = self.client.call_structured(request, PageExtraction, file_id=bundle.file_id, page=page.number, stage="extract")
        for p in res.problems:
            report.count(p)
        if res.parsed is None:
            return None
        problems = check_page(res.parsed, page.text)
        if not problems:
            return res.parsed
        report.count("content_check_failed")
        # Valid shape, wrong content: re-ask once, naming the failed check. Never retry blind.
        again = self.client.call_structured(self.client.repair_request(request, "; ".join(problems), round_no=2),
                                            PageExtraction, file_id=bundle.file_id, page=page.number, stage="repair")
        if again.parsed is not None and not check_page(again.parsed, page.text):
            report.count("content_fixed_on_reask")
            return again.parsed
        report.count("content_withheld")                   # discard the failing fields; the analyst sees why
        bad = {p.split(":")[0] for p in problems}
        blank = {name: (AmountField if name in ("requested_amount", "monthly_income") else TextField)(
            value=None, confidence=0.0, evidence="") for name in bad}
        return res.parsed.model_copy(update=blank)

    def extract_with_report(self, bundle: SyntheticFile, ready_at: float) -> FileReport:
        report = FileReport(bundle.file_id, len(bundle.pages))
        results, c_start, c_end = self.scheduler.run(
            [lambda p=p: self._classify(bundle, p, report) for p in bundle.pages], ready_at)
        report.started_at, report.classify_s = c_start, c_end - c_start
        if any(isinstance(r, Exception) for r in results):
            report.status, report.finished_at = "deferred", c_end
            return report
        types: dict[int, tuple[Doc, float]] = {p.number: r for p, r in zip(bundle.pages, results)}  # type: ignore[misc]
        chosen = [p for p in bundle.pages if types[p.number][0] in EXTRACT_TYPES
                  and not (types[p.number][0] == Doc.BANK_STATEMENT and types.get(p.number - 1, (None,))[0] == Doc.BANK_STATEMENT)]
        ex_results, _, e_end = self.scheduler.run(
            [lambda p=p: self._extract_page(bundle, p, types[p.number][0], report) for p in chosen], c_end)
        report.extract_s, report.finished_at = e_end - c_end, e_end
        if any(isinstance(r, Exception) for r in ex_results):
            report.status = "deferred"
            return report
        pages = {p.number: r for p, r in zip(chosen, ex_results) if r is not None}  # type: ignore[misc]
        report.extraction = self._merge(bundle.file_id, types, pages)  # type: ignore[arg-type]
        return report

    # --- deterministic assembly: code, not the model, builds the file-level answer -------------------
    @staticmethod
    def _merge(file_id: str, types: dict[int, tuple[Doc, float]], pages: dict[int, PageExtraction]) -> LoanFileExtraction:
        reasons: list[str] = []

        def pick(name: str, required: bool) -> FieldResult:
            cands = [(n, getattr(e, name)) for n, e in sorted(pages.items()) if getattr(e, name).value is not None]
            if not cands:
                if required:
                    reasons.append(f"{name}: not found on any page")
                return FieldResult(value=None, confidence=0.0, page=None, evidence="")
            distinct = {str(f.value).casefold() for _, f in cands}
            if len(distinct) > 1:
                where = ", ".join(f"page {n}: {f.value}" for n, f in cands)
                reasons.append(f"{name}: pages disagree ({where})")
                return FieldResult(value=None, confidence=0.0, page=None, evidence="", flags=["conflict"])
            n, best = max(cands, key=lambda c: c[1].confidence)
            flags = ["low_confidence"] if best.confidence < REVIEW_BELOW else []
            if flags:
                reasons.append(f"{name}: confidence {best.confidence:.2f} on page {n}")
            return FieldResult(value=best.value, confidence=best.confidence, page=n, evidence=best.evidence, flags=flags)

        name, pan = pick("applicant_name", True), pick("applicant_pan", True)
        if isinstance(name.value, str) and isinstance(pan.value, str) and not pan_matches_surname(pan.value, name.value):
            reasons.append(f"applicant_pan {pan.value} does not match the surname in {name.value!r}")
            name.flags.append("pan_surname_mismatch")
            pan.flags.append("pan_surname_mismatch")
        income = [IncomeEvidence(doc=types[n][0], page=n, monthly_income=e.monthly_income.value,
                                 confidence=e.monthly_income.confidence)
                  for n, e in sorted(pages.items()) if e.monthly_income.value is not None]
        docs: dict[Doc, list[int]] = {}
        for n, (doc, _) in sorted(types.items()):
            if doc != Doc.UNKNOWN:
                docs.setdefault(doc, []).append(n)
        present = [DocumentPresent(doc=d, pages=ns, confidence=min(types[n][1] for n in ns)) for d, ns in docs.items()]
        if any(doc == Doc.UNKNOWN for doc, _ in types.values()):
            reasons.append("one or more pages could not be classified")
        return LoanFileExtraction(
            file_id=file_id, applicant_name=name, applicant_pan=pan,
            co_applicant_name=pick("co_applicant_name", False), product=pick("product", True),
            requested_amount=pick("requested_amount", True), income_evidence=income, documents_present=present,
            needs_review=bool(reasons), review_reasons=reasons)
