"""Wrappers around the stages that already exist. None of them changes what a stage decides.

  model calls      Day 12's client already writes a ledger row per attempt (tokens, rupees, outcome, timing). Day 12
                   promised that "the ledger row becomes a span"; `model_call_spans` does exactly that, so the trace
                   and the bill are the same numbers by construction.
  the model box    `TracedModel` wraps any Day 11 ExtractionModel: same answer, plus a span saying what it read.
  the rules        `TracedRuleSet` wraps a signed Day 11 RuleSet: same findings, plus the rule ids that fired, the
                   version, the sign-off status and the fingerprint of the code that ran.
  the core write   `traced_push` calls Day 11's push_to_core (the function Day 16's SafeCoreWriter drives) after
                   Day 16's write-window check, and records what happened.
  retrieval        `TracedRetrieval` wraps Day 15's permission-aware search: result counts, never the query.

Until Day 20 wires Day 12's client into Day 11's pipeline, the pipeline's answer comes from Day 11's stub (as in Day
18's pilot week) and the model bill comes from Day 12's production client reading the same pages through its fake
provider, the 02:00 job. Both are real code; the seam is `as_day12_file`, and Day 20 removes it.
"""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any

from . import paths  # noqa: F401
from .spans import (ERROR_TYPE, GEN_AI_CACHE_READ, GEN_AI_CACHE_WRITE, GEN_AI_DATA_SOURCE, GEN_AI_INPUT_TOKENS,
                    GEN_AI_OPERATION, GEN_AI_OUTPUT_TOKENS, GEN_AI_PROMPT_NAME, GEN_AI_PROMPT_VERSION,
                    GEN_AI_PROVIDER, GEN_AI_REQUEST_MODEL, Span, Tracer)
from godavari_integration.clock import IST as DAY16_IST, in_write_freeze, next_write_slot
from godavari_llm.client import LLMClient, ResponseStore
from godavari_llm.contract import Doc as Doc12
from godavari_llm.extractor import CLASSIFY_PROMPT_VERSION, EXTRACT_PROMPT_VERSION, GodavariExtractor, VirtualScheduler
from godavari_llm.fake_provider import FakeConfig, FakeProvider
from godavari_llm.ledger import CostLedger, LedgerRow
from godavari_llm.provider import VirtualClock
from godavari_llm.retry import CircuitBreaker, RetryPolicy
from godavari_llm.synthetic import SyntheticFile, SyntheticPage
from godavari_retrieval.metadata import ROLE_BRANCH, ROLE_COMPLIANCE, ROLE_CREDITOPS
from godavari_retrieval.permissions import StaleDirectoryError
from intake.catalogue import PAGE_TITLES, Doc, LoanBundle, ModelOutput
from intake.core_write import Approval, FakeCoreSandbox, PushLog, push_to_core
from intake.routing import MANDATORY_FIELDS, Route
from intake.ruleset import Action, Finding, RuleContext, RuleSet, check_signoff

PROVIDER_NAME = "fake"                      # Day 12's FakeProvider; the real adapters would say "anthropic", "openai"
CONCURRENCY = 16                            # Day 12's pool size for the 02:00 job
_DAY12_DOCS = {d.value for d in Doc12}


# --- the seam Day 20 closes ---------------------------------------------------------------------------------------
def true_page_type(text: str) -> str:
    """The printed title on the page decides what it is (the synthetic generator writes the titles)."""
    best = (0, Doc.UNKNOWN.value)
    for doc, title in PAGE_TITLES.items():
        if text.startswith(title) and len(title) > best[0]:
            best = (len(title), doc.value)
    return best[1]


def as_day12_file(bundle: LoanBundle) -> SyntheticFile:
    """The same pages, in the shape Day 12's fake provider reads. Image-token sizes are drawn from Day 12's ranges."""
    rng = random.Random(f"day19-pages-{bundle.file_id}")
    pages = []
    for p in bundle.pages:
        kind = true_page_type(p.text)
        pages.append(SyntheticPage(bundle.file_id, p.number, Doc12(kind) if kind in _DAY12_DOCS else Doc12.UNKNOWN,
                                   p.text, rng.randint(1550, 1700), rng.randint(420, 480), {}, {}))
    return SyntheticFile(bundle.file_id, bundle.branch, bundle.product, tuple(pages), {})


class MeteredNight:
    """One 02:00 drop through Day 12's production client: the classify and extract calls, priced on Day 12's card."""

    def __init__(self, started: datetime, seed: int) -> None:
        self.started = started
        self.clock = VirtualClock()
        self.ledger = CostLedger()
        self.seed = seed

    def run(self, bundles: Sequence[LoanBundle]) -> dict[str, Any]:
        from run_nightly_batch import run_night          # Day 12's re-queue loop (imported, not copied)
        files = [as_day12_file(b) for b in bundles]
        provider = FakeProvider(files, self.clock, FakeConfig(seed=self.seed, outages=[]))
        client = LLMClient(provider, self.ledger, self.clock, policy=RetryPolicy(),
                           breaker=CircuitBreaker(self.clock, failure_threshold=5, cooldown_s=60.0), store=ResponseStore())
        extractor = GodavariExtractor(client, VirtualScheduler(self.clock, CONCURRENCY))
        reports, _passes, _deferred = run_night(files, provider, client, self.clock, extractor)
        return {r.file_id: r for r in reports}

    def at(self, seconds: float) -> datetime:
        return self.started + timedelta(seconds=seconds)


def _prompt_for(stage: str) -> tuple[str, str]:
    return ("classify", CLASSIFY_PROMPT_VERSION) if stage in ("classify", "escalate") else ("extract", EXTRACT_PROMPT_VERSION)


def model_call_spans(tracer: Tracer, night: MeteredNight, parents: dict[str, tuple[Span, Span | None]],
                     rows: list[LedgerRow] | None = None) -> None:
    """One span per ledger row: the attempt, its tokens, its rupees, its outcome. Stage spans get their extent."""
    for r in rows if rows is not None else night.ledger.rows:
        if r.file_id not in parents:
            continue
        root, _ = parents[r.file_id]
        stage_name = "classify" if r.stage in ("classify", "escalate") else "extract"
        stage = next((s for s in tracer.of_trace(root.trace_id) if s.name == stage_name and s.kind == "stage"), None)
        start, end = night.at(r.started_s), night.at(r.started_s + r.elapsed_s)
        if stage is None:
            stage = tracer.span(root.trace_id, stage_name, "stage", start, end, parent=root)
        stage.start, stage.end = min(stage.start, start), max(stage.end, end)
        name, version = _prompt_for(r.stage)
        attrs: dict[str, Any] = {
            GEN_AI_OPERATION: "chat", GEN_AI_PROVIDER: PROVIDER_NAME, GEN_AI_REQUEST_MODEL: r.model,
            GEN_AI_INPUT_TOKENS: r.input_tokens + r.cache_read_tokens + r.cache_write_tokens,   # all input, per the spec
            GEN_AI_OUTPUT_TOKENS: r.output_tokens, GEN_AI_CACHE_READ: r.cache_read_tokens,
            GEN_AI_CACHE_WRITE: r.cache_write_tokens, GEN_AI_PROMPT_NAME: name, GEN_AI_PROMPT_VERSION: version,
            "kaagaz.llm.stage": r.stage, "kaagaz.llm.tier": r.tier, "kaagaz.llm.attempt": r.attempt,
            "kaagaz.llm.outcome": r.outcome, "kaagaz.llm.page": r.page or 0,
            "kaagaz.cost.inr": 0.0 if r.estimated else r.inr, "kaagaz.cost.estimated_inr": r.inr if r.estimated else 0.0,
        }
        status = "ok" if r.outcome in ("ok", "store_hit") else "error"
        if status == "error":
            attrs[ERROR_TYPE] = r.outcome
        tracer.span(root.trace_id, f"chat {r.model}", "model_call", start, end, parent=stage, status=status, **attrs)


# --- the model box and the rules ----------------------------------------------------------------------------------
class TracedModel:
    """Day 11's model interface, unchanged in behaviour. `bind()` tells it which trace the next read belongs to."""

    def __init__(self, inner: Any, tracer: Tracer) -> None:
        self.inner = inner
        self.tracer = tracer
        self.name = inner.name
        self._at: tuple[Span, datetime] | None = None

    def bind(self, root: Span, at: datetime) -> None:
        self._at = (root, at)

    def read(self, bundle: LoanBundle) -> ModelOutput:
        out = self.inner.read(bundle)
        root, at = self._at  # type: ignore[misc]
        wanted = MANDATORY_FIELDS[bundle.product]
        self.tracer.span(root.trace_id, "pipeline.read", "code", at, parent=root, **{
            "kaagaz.model.name": out.model_name,
            "kaagaz.model.fields_unsure": sum(1 for f in wanted if out.fields.get(f) is None or out.fields[f].value is None),
            "kaagaz.model.pages_unclassified": sum(1 for d, _ in out.page_labels.values() if d == Doc.UNKNOWN)})
        return out

    def draft_note(self, bundle: LoanBundle, findings: Sequence[tuple[str, str]]) -> str:
        return self.inner.draft_note(bundle, findings)


class TracedRuleSet:
    """Same rules, same order, same findings. The span carries rule ids and counts, never a finding's message:
    Day 11's messages quote the PAN and the names on the form, which is exactly what must not leave the screen."""

    def __init__(self, inner: RuleSet, tracer: Tracer, mode: str = "prototype") -> None:
        self.inner = inner
        self.tracer = tracer
        status = check_signoff(inner, mode)
        self.status = status.status
        self.fingerprint = inner.fingerprint()[:12]
        self._at: tuple[Span, datetime] | None = None

    def __getattr__(self, name: str) -> Any:            # product, version, rules, source_files: the real ones
        return getattr(self.inner, name)

    def bind(self, root: Span, at: datetime) -> None:
        self._at = (root, at)

    def run(self, ctx: RuleContext) -> list[Finding]:
        findings = self.inner.run(ctx)
        root, at = self._at  # type: ignore[misc]
        by = Counter(f.action for f in findings)
        self.tracer.span(root.trace_id, "rules", "code", at, parent=root, **{
            "kaagaz.rules.product": self.inner.product, "kaagaz.rules.version": self.inner.version,
            "kaagaz.rules.status": self.status, "kaagaz.rules.fingerprint": self.fingerprint,
            "kaagaz.rules.fired": sorted({f.rule_id for f in findings}),
            "kaagaz.rules.send_back": by[Action.SEND_BACK], "kaagaz.rules.review": by[Action.REVIEW],
            "kaagaz.rules.block": by[Action.BLOCK]})
        return findings


def route_span(tracer: Tracer, root: Span, at: datetime, result: Any) -> Span:
    return tracer.span(root.trace_id, "route", "code", at, parent=root, **{
        "kaagaz.route": result.route.value,
        "kaagaz.envelope.fired": sorted({f.rule_id for f in result.findings if f.kind == "envelope"}),
        "kaagaz.note.corrected": bool(result.note_corrected)})


# --- the core write -----------------------------------------------------------------------------------------------
def traced_push(tracer: Tracer, root: Span, approved_at: datetime, file_id: str, branch: str, route: Route,
                product: str, analyst: str, sandbox: FakeCoreSandbox, log: PushLog) -> Span:
    """Day 16's window first (writes wait while the evening batch owns the core), then Day 11's push."""
    local = approved_at.astimezone(DAY16_IST)
    held = in_write_freeze(local)
    at = next_write_slot(local).astimezone(approved_at.tzinfo) if held else approved_at
    record = push_to_core(file_id, branch, route, {"product": product}, Approval(analyst, at.date()), sandbox, log)
    entry = log.entries[-1]
    return tracer.span(root.trace_id, "core.write", "write", approved_at, at, parent=root, **{
        "kaagaz.core.action": entry["action"], "kaagaz.core.held_for_window": held, "kaagaz.core.record": record})


# --- retrieval ----------------------------------------------------------------------------------------------------
def role_of(groups: frozenset[str]) -> str:
    if ROLE_COMPLIANCE in groups:
        return "compliance"
    if ROLE_CREDITOPS in groups:
        return "creditops"
    if ROLE_BRANCH in groups:
        return "branch"
    return "service"


class TracedRetrieval:
    """Day 15's search, with a span per query. The query text is never recorded: in the conventions it is an
    opt-in attribute, and at Godavari a query can carry a customer's name ("similar files to Ravi Teja's")."""

    def __init__(self, service: Any, tracer: Tracer, run: str) -> None:
        self.service = service
        self.tracer = tracer
        self.run = run

    def search(self, trace_id: str, user: str, query: str, now: datetime, **kw: Any) -> Any:
        directory = self.service.directory
        age_h = round((now.replace(tzinfo=None) - directory.taken_at).total_seconds() / 3600, 1)
        role = role_of(directory.members.get(user, frozenset()))
        attrs: dict[str, Any] = {GEN_AI_OPERATION: "retrieval", GEN_AI_DATA_SOURCE: "godavari-policy-register",
                                 "kaagaz.retrieval.user_role": role, "kaagaz.retrieval.snapshot_age_h": age_h}
        try:
            resp = self.service.search(user, query, now.replace(tzinfo=None), **kw)
        except StaleDirectoryError:
            self.tracer.span(trace_id, "retrieval godavari-policy-register", "retrieval", now, now, status="error",
                             **attrs, **{ERROR_TYPE: "stale_directory", "kaagaz.retrieval.results": 0})
            return None
        self.tracer.span(trace_id, "retrieval godavari-policy-register", "retrieval", now, now, **attrs, **{
            "kaagaz.retrieval.results": len(resp.results), "kaagaz.retrieval.total_matches": resp.total_matches,
            "kaagaz.retrieval.notices": len(resp.notices)})
        return resp
