"""Two pilot weeks, traced end to end: Monday 7 to Friday 11 December, and Monday 14 to Friday 18 December 2026.

Week one is Day 18's week exactly: the same 60 files (GF-61000 onwards), the same model run, the same simulated
analysts, so this chapter's traces describe the week Day 18 reported (a test checks the screen log matches). Week two is
the next 60 files from the same synthetic month, with one change in the world and one change in the system:

  the world   from Tuesday 15 December, Guntur's files carry a sixty-page net-banking statement (statements.py)
  the system  the page filter ships on Wednesday 16 December at 17:00, the last change before the freeze that starts
              on Thursday 17 December; Thursday's 02:00 batch is the first one it sees

For each file the trace holds: the root span (arrival, pages, what the model was shown, the prompt release, the cost),
the classify and extract stages with one span per model call (Day 12's ledger rows), what the pipeline read, the rules
that fired, the route, the analyst's review with one feedback event per correction, and the core write.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from . import paths
from .instrument import MeteredNight, TracedModel, TracedRetrieval, TracedRuleSet, model_call_spans, route_span, traced_push
from .spans import IST, Span, Tracer, trace_id_for
from .statements import FILTER_NAME, filter_for_model, lengthen_statement
from evals import candidates
from evals.golden import GoldenFile, bundle_sha256
from evals.labels import paper_label
from evals.normalise import norm_equal
from godavari_prompts.registry import Registry
from godavari_review import bands as B
from godavari_review import corrections as C
from godavari_review import pilot as day18
from godavari_review.queue import build_item
from intake.catalogue import LoanBundle
from intake.core_write import FakeCoreSandbox, PushLog
from intake.pipeline import process
from intake.reference import BRANCH_CODES
from intake.routing import Route
from intake.synth import GroundTruth, build_file
from evals.day11 import RULESETS

WEEK2 = [date(2026, 12, 14) + timedelta(days=i) for i in range(5)]
LONG_STATEMENTS_FROM = date(2026, 12, 15)       # Tuesday: Guntur starts attaching the full statement
FILTER_FROM = date(2026, 12, 17)                # Thursday's 02:00 batch: the first one after the fix shipped
LONG_BRANCH = "Guntur"
FILES_PER_WEEK_PER_BRANCH = 30


@dataclass
class FileRun:
    file_id: str
    branch: str
    week: int
    arrived: datetime                 # IST
    bundle: LoanBundle                # every page, as the analyst sees it
    shown: LoanBundle                 # the pages the model was shown
    truth: GroundTruth
    pf: Any                           # Day 18's PilotFile
    root: Span
    filtered: int = 0
    finished_s: float = 0.0


@dataclass
class WeekRun:
    number: int
    days: list[date]
    files: list[FileRun]
    week: Any                         # Day 18's Week, with the simulated screen log
    nights: list[MeteredNight] = field(default_factory=list)


def _naive(at: datetime) -> datetime:
    return at.replace(tzinfo=None)


def _ist(at: datetime) -> datetime:
    return at.replace(tzinfo=IST)


def _seed(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)


def week2_arrivals() -> list[datetime]:
    return [datetime(d.year, d.month, d.day, 2, 0) for d in WEEK2 for _ in range(day18.FILES_PER_BRANCH_PER_DAY)]


def plan(number: int) -> list[tuple[Any, datetime, str]]:
    """(Day 7 row, arrival, analyst) for every file of the week, in Day 18's order: Kukatpally first, then Guntur."""
    rows = day18.pilot_rows()
    lo = (number - 1) * FILES_PER_WEEK_PER_BRANCH
    arrivals = day18.arrivals() if number == 1 else week2_arrivals()
    out = []
    for branch, team in day18.BRANCH_TEAM.items():
        mine = [r for r in rows if r.branch == branch][lo:lo + FILES_PER_WEEK_PER_BRANCH]
        for k, (row, arrived) in enumerate(zip(mine, arrivals)):
            out.append((row, arrived, team[k % 3]))
    return out


def pinned_release() -> Any:
    return Registry.load().current("pilot", "extraction")


def run_week(number: int, tracer: Tracer, bands: Any, policy: dict[str, Any], sandbox: FakeCoreSandbox,
             pushlog: PushLog) -> WeekRun:
    run = f"pilot-week-{number}"
    release = pinned_release()
    model = TracedModel(candidates.build("baseline", run_id=run), tracer)
    ruleset = RULESETS["two-wheeler"]
    traced_rules = TracedRuleSet(ruleset, tracer)
    version = f"{policy['version']} fitted on Day 14 development, confirmed on test (data/bands.json)"

    by_night: dict[datetime, list[tuple[Any, str]]] = defaultdict(list)
    for row, arrived, analyst in plan(number):
        by_night[arrived].append((row, analyst))

    files: list[FileRun] = []
    nights: list[MeteredNight] = []
    for arrived in sorted(by_night):
        at = _ist(arrived)
        built = []
        for row, analyst in by_night[arrived]:
            bundle, truth = build_file(row)
            if number == 2 and row.branch == LONG_BRANCH and arrived.date() >= LONG_STATEMENTS_FROM:
                bundle = lengthen_statement(bundle)
            shown, filtered = (filter_for_model(bundle) if number == 2 and arrived.date() >= FILTER_FROM
                               else (bundle, 0))
            built.append((row, analyst, bundle, shown, truth, filtered))
        night = MeteredNight(at, seed=_seed(f"{run}-{arrived.isoformat()}"))
        reports = night.run([b[3] for b in built])
        nights.append(night)
        roots: dict[str, tuple[Span, None]] = {}
        for row, analyst, bundle, shown, truth, filtered in built:
            tid = trace_id_for(run, row.file_id)
            root = tracer.span(tid, "loan_file", "file", at, **{
                "kaagaz.run": run, "kaagaz.file.id": row.file_id, "kaagaz.file.branch_code": BRANCH_CODES[row.branch],
                "kaagaz.file.product": row.product, "kaagaz.file.channel": row.channel,
                "kaagaz.file.pages": len(bundle.pages), "kaagaz.file.pages_to_model": len(shown.pages),
                "kaagaz.file.bundle_sha256": bundle_sha256(bundle)[:16], "kaagaz.prompt.release": release.release_id,
                "kaagaz.page_filter": FILTER_NAME if number == 2 and arrived.date() >= FILTER_FROM else "off"})
            roots[row.file_id] = (root, None)
            files.append(FileRun(row.file_id, row.branch, number, at, bundle, shown, truth, None, root, filtered,
                                 reports[row.file_id].finished_at))
        model_call_spans(tracer, night, roots)
        for fr, (row, analyst, bundle, shown, truth, filtered) in zip(files[-len(built):], built):
            done = night.at(fr.finished_s)
            model.bind(fr.root, done)
            traced_rules.bind(fr.root, done)
            result = process(shown, model, traced_rules, arrived.date())     # Day 11's pipeline, unchanged
            route_span(tracer, fr.root, done, result)
            gf = GoldenFile(row.file_id, "pilot", row.product, row.branch, row.channel, row.language_mix, row.pages, row)
            paper = paper_label(gf, bundle, truth).fields
            rows = day18.rows_for(bundle, result, "pilot", paper)
            item = build_item(bundle, result, rows, bands, policy, ruleset, arrived, arrived.date(), version)
            fr.pf = day18.PilotFile(bundle, result, rows, item, analyst, arrived)

    order = {r.file_id: i for i, r in enumerate(plan_ids(number))}
    files.sort(key=lambda f: order[f.file_id])
    week = day18.simulate(day18.Week([f.pf for f in files]), policy)
    wr = WeekRun(number, day18.WEEK if number == 1 else WEEK2, files, week, nights)
    review_and_write(tracer, wr, policy, sandbox, pushlog)
    return wr


def plan_ids(number: int) -> list[Any]:
    return [r for r, _, _ in plan(number)]


def _bucket(c: float) -> str:
    for lo, hi in ((0.0, 0.5), (0.5, 0.7), (0.7, 0.85), (0.85, 0.95)):
        if c < hi:
            return f"{lo}-{hi}"
    return "0.95-1.0"


def review_and_write(tracer: Tracer, wr: WeekRun, policy: dict[str, Any], sandbox: FakeCoreSandbox,
                     pushlog: PushLog) -> None:
    events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in wr.week.log:
        events[e["file_id"]].append(e)
    for fr in wr.files:
        ev = events[fr.file_id]
        opened = _ist(datetime.fromisoformat(next(e for e in ev if e["event"] == "open")["at"]))
        approve = next(e for e in ev if e["event"] == "approve")
        approved = _ist(datetime.fromisoformat(approve["at"]))
        fields = [e for e in ev if e["event"] == "field"]
        forced = next((e for e in fields if e["forced"]), None)
        actions = defaultdict(int)
        for e in fields:
            actions[e["action"]] += 1
        attrs: dict[str, Any] = {
            "kaagaz.review.analyst": approve["analyst"], "kaagaz.review.fields_shown": len(fields),
            "kaagaz.review.accepted": actions["accepted"], "kaagaz.review.confirmed": actions["confirmed"],
            "kaagaz.review.corrected": actions["corrected"], "kaagaz.review.keyed": actions["keyed"],
            "kaagaz.review.not_in_file": actions["not_in_file"],
            "kaagaz.review.queue_wait_h": round((opened - fr.arrived).total_seconds() / 3600, 2),
            "kaagaz.review.bands_version": policy["version"]}
        if forced:
            attrs["kaagaz.review.forced_field"] = forced["field"]
            attrs["kaagaz.review.forced_seconds"] = forced["seconds"]
        review = tracer.span(fr.root.trace_id, "review", "human", opened, approved, parent=fr.root, **attrs)
        rows = {r.field: r for r in fr.pf.rows}
        for e in fields:
            if e["action"] not in ("corrected", "keyed", "not_in_file"):
                continue
            row = rows[e["field"]]
            review.event("feedback", _ist(datetime.fromisoformat(e["at"])), **{
                "kaagaz.feedback.field": e["field"],
                "kaagaz.feedback.reason": C.reason_for(e["field"], e["model_value"], e["new_value"], row.evidence),
                "kaagaz.feedback.band": e["band"], "kaagaz.feedback.stratum": e["stratum"],
                "kaagaz.feedback.action": e["action"],
                "kaagaz.feedback.content_change": not norm_equal(e["field"], e["model_value"], e["new_value"]),
                "kaagaz.feedback.confidence_bucket": _bucket(e["confidence"])})
        route = Route(fr.pf.item.route)
        if route in (Route.REVIEW, Route.READY_FOR_APPROVAL):
            w = traced_push(tracer, fr.root, approved, fr.file_id, fr.branch, route, fr.pf.bundle.product,
                            approve["analyst"], sandbox, pushlog)
            outcome = "written to core"
            end = w.end
        else:
            outcome = "sent back" if route == Route.SEND_BACK else "blocked"
            end = approved
        cost = sum(s.attrs.get("kaagaz.cost.inr", 0.0) for s in tracer.of_trace(fr.root.trace_id) if s.kind == "model_call")
        est = sum(s.attrs.get("kaagaz.cost.estimated_inr", 0.0) for s in tracer.of_trace(fr.root.trace_id)
                  if s.kind == "model_call")
        fr.root.attrs.update({"kaagaz.file.outcome": outcome, "kaagaz.cost.inr": round(cost, 6),
                              "kaagaz.cost.estimated_inr": round(est, 6),
                              "kaagaz.llm.calls": sum(1 for s in tracer.of_trace(fr.root.trace_id) if s.kind == "model_call")})
        fr.root.end = max(end, *(s.end for s in tracer.of_trace(fr.root.trace_id)))


# --- the policy panel: Day 15's search, a few times a day --------------------------------------------------------
SYNC_FAILS_ON = date(2026, 12, 17)       # Thursday: the 02:00 HR-to-AD export does not run (Day 15's sync)


def run_retrieval(tracer: Tracer, days: list[date], run: str) -> dict[str, Any]:
    import json
    from godavari_retrieval.chunking import chunk_corpus
    from godavari_retrieval.corpus import build_corpus
    from godavari_retrieval.directory_data import members
    from godavari_retrieval.permissions import Directory, SearchFilter, POLICY_TYPES
    from godavari_retrieval.service import RetrievalService
    queries = [q for q in json.loads((paths.DAY15_DATA / "labelled-queries.json").read_text(encoding="utf-8"))
               if q["scope"] == "policy" and q["user"] in ("lakshmi", "srinivas")]
    docs, _ = build_corpus()
    chunks = chunk_corpus(docs)
    member_sets = {u: frozenset(g) for u, g in members(True).items()}
    asked = refused = empty = 0
    k = 0
    snapshot = None
    for d in days:
        if d != SYNC_FAILS_ON or snapshot is None:
            snapshot = datetime(d.year, d.month, d.day, 2, 0)
        service = TracedRetrieval(RetrievalService(chunks, Directory(snapshot, member_sets, f"ad-groups-{snapshot:%Y-%m-%d}")),
                                  tracer, run)
        for hour in (11, 15):
            for _ in range(3):
                q = queries[k % len(queries)]
                k += 1
                at = datetime(d.year, d.month, d.day, hour, 0, tzinfo=IST)
                resp = service.search(trace_id_for(run, f"retrieval-{k}"), q["user"], q["text"], at,
                                      f=SearchFilter(as_of=d, doc_types=POLICY_TYPES))
                asked += 1
                refused += resp is None
                empty += resp is not None and not resp.results
    return {"asked": asked, "refused": refused, "empty": empty}
