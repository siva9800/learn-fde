"""The weekly quality job: is it getting worse, without ground truth?

Production has no answer key. What it has are signals, each a proxy, each compared with something:

  correction rate per field     analysts' content corrections per file reviewed, against the error rate the golden
                                set measured for that field (Day 14's baseline run); outside both intervals is a finding
  review-band overrides         corrections in the review band against the bands' expected wrong share (Day 18)
  rubber-stamp sessions         Day 18's detector, on the screen's log, never on the truth
  spot checks                   blind second reads of auto-accepted fields (Day 18's sampler): the only signal that
                                measures confident-wrong values directly
  rule and envelope fire rates  this week against week one, per branch: a rule that suddenly fires is a change in the
                                files, the model or the rule, and the trace says which
  unsure and unclassified       the model saying "cannot tell" more, or less, than before (Day 13, 7.4)
  retrieval                     zero results and refusals on the policy panel (Day 15)

The job reads the trace store and, for the two Day 18 signals that need it, the screen's own log, inside Godavari's
environment. It writes counts and statuses, never values. Its last output is a list of candidates for Day 14's
development split: the kinds of file production is seeing that the golden set does not contain.
"""

from __future__ import annotations

import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

from . import paths
from .costs import BRANCH_OF
from .store import TraceStore
from evals.normalise import norm_equal
from evals.stats import wilson
from godavari_review import bands as B
from godavari_review import sampler, stamping
from intake.routing import MANDATORY_FIELDS
from run_pilot_week import SAMPLE_KEY, SECOND_READER        # Day 18's draw key and second readers, imported

FIELDS = MANDATORY_FIELDS["two-wheeler"]


def golden_baseline() -> dict[str, Any]:
    return json.loads((paths.DAY14_DATA / "eval-baseline.json").read_text(encoding="utf-8"))


def expected_review_share() -> float:
    return json.loads((paths.DAY18_DATA / "bands.json").read_text(encoding="utf-8"))["summary"][
        "expected_wrong_share_in_review"]


@dataclass(frozen=True)
class FieldSignal:
    field: str
    files: int
    changed: int
    rate: float
    lo: float
    hi: float
    golden_rate: float
    golden_lo: float
    golden_hi: float
    status: str


def _runs(store: TraceStore) -> dict[str, tuple[str, str]]:
    return {r["trace_id"]: (r["attrs"]["kaagaz.run"], BRANCH_OF[r["attrs"]["kaagaz.file.branch_code"]])
            for r in store.by_name("loan_file")}


def field_signals(store: TraceStore, run: str, branch: str | None = None) -> list[FieldSignal]:
    runs = _runs(store)
    files = [r for r in store.by_name("review") if runs[r["trace_id"]][0] == run
             and (branch is None or runs[r["trace_id"]][1] == branch)]
    ids = {r["trace_id"] for r in files}
    changed = Counter(e["attrs"]["kaagaz.feedback.field"] for e in store.events("feedback")
                      if e["trace_id"] in ids and e["attrs"].get("kaagaz.feedback.content_change"))
    gold = golden_baseline()["strata"]
    out = []
    for f in FIELDS:
        g = gold.get(f"field={f}")
        if g is None:
            continue
        n, k = len(files), changed[f]
        lo, hi = wilson(k, n)
        g_lo, g_hi = 1 - g["accuracy_ci"][1], 1 - g["accuracy_ci"][0]
        status = ("higher than the golden set" if lo > g_hi else
                  "lower than the golden set" if hi < g_lo else "in line")
        out.append(FieldSignal(f, n, k, k / n if n else 0.0, lo, hi, 1 - g["accuracy"], g_lo, g_hi, status))
    return out


def branch_signals(store: TraceStore, run: str) -> dict[str, dict[str, float]]:
    runs = _runs(store)
    per: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for r in store.by_name("loan_file"):
        rn, br = runs[r["trace_id"]]
        if rn == run:
            per[br]["files"] += 1
            per[br]["pages"] += r["attrs"]["kaagaz.file.pages"]
    for r in store.by_name("route"):
        rn, br = runs[r["trace_id"]]
        if rn == run:
            per[br][f"route {r['attrs']['kaagaz.route']}"] += 1
            per[br]["envelope ENV-GROUND"] += "ENV-GROUND" in r["attrs"]["kaagaz.envelope.fired"]
    for r in store.by_name("pipeline.read"):
        rn, br = runs[r["trace_id"]]
        if rn == run:
            per[br]["unsure fields"] += r["attrs"]["kaagaz.model.fields_unsure"]
            per[br]["unclassified pages"] += r["attrs"]["kaagaz.model.pages_unclassified"]
    for e in store.events("feedback"):
        rn, br = runs[e["trace_id"]]
        if rn == run:
            per[br]["content corrections"] += bool(e["attrs"].get("kaagaz.feedback.content_change"))
            per[br]["format-only corrections"] += e["attrs"].get("kaagaz.feedback.reason") == "format only"
    return {b: dict(v) for b, v in sorted(per.items())}


@dataclass(frozen=True)
class RuleMove:
    rule: str
    branch: str
    before: int
    before_n: int
    after: int
    after_n: int
    moved: bool


def rule_moves(store: TraceStore, before: str = "pilot-week-1", after: str = "pilot-week-2") -> list[RuleMove]:
    """Share of files on which each rule (or envelope check) fired, week against week, per branch. 'Moved' means this
    week's share is outside the 95 percent interval of last week's: a reason to open traces, not a verdict."""
    runs = _runs(store)
    fired: dict[tuple[str, str, str], int] = defaultdict(int)
    n: dict[tuple[str, str], int] = defaultdict(int)
    for name, key in (("rules", "kaagaz.rules.fired"), ("route", "kaagaz.envelope.fired")):
        for r in store.by_name(name):
            rn, br = runs[r["trace_id"]]
            if name == "rules":
                n[(rn, br)] += 1
            for rule in r["attrs"][key]:
                fired[(rn, br, rule)] += 1
    out = []
    for rule, br in sorted({(k[2], k[1]) for k in fired}):
        b, a = fired[(before, br, rule)], fired[(after, br, rule)]
        bn, an = n[(before, br)], n[(after, br)]
        lo, hi = wilson(b, bn)
        rate = a / an if an else 0.0
        out.append(RuleMove(rule, br, b, bn, a, an, not (lo <= rate <= hi) and abs(a - b) >= 3))
    return out


def overrides(week: Any) -> list[dict[str, Any]]:
    return stamping.weekly_overrides(week.log, expected_review_share())


def suspected_sessions(week: Any) -> list[Any]:
    return [s for s in (stamping.judge(x) for x in stamping.sessions(week.log)) if s.verdict != "ok"]


def spot_checks(week: Any, seed: str) -> dict[str, Any]:
    """Day 18's draw of approved files, read again blind against the paper. The second reader is simulated with Day 18's
    slip rates; a disagreement goes to the team leads, who read the paper."""
    approved = [(p.item.file_id, p.item.branch) for p in week.files
                if any(f.band == B.Band.AUTO and not f.forced for f in p.item.fields)]
    targeted = {fid for s in suspected_sessions(week) if s.verdict.startswith("suspected") for fid in s.files}
    picks = sampler.sample(approved, SAMPLE_KEY, targeted)
    final = {(e["file_id"], e["field"]): e["new_value"] for e in week.log if e["event"] == "field"}
    items = {p.item.file_id: p for p in week.files}
    rng = random.Random(seed)
    checked = wrong = 0
    for pk in [p for p in picks if p.why == "random"]:
        _who, slip = SECOND_READER[pk.branch]
        for f in items[pk.file_id].item.fields:
            if f.band != B.Band.AUTO or f.forced:
                continue
            checked += 1
            reader = f.row.label if rng.random() > slip else (f.row.label or "") + "7"
            approved_value = final[(pk.file_id, f.row.field)]
            if not norm_equal(f.row.field, approved_value, reader) and not norm_equal(f.row.field, approved_value,
                                                                                      f.row.label):
                wrong += 1
    lo, hi = wilson(wrong, checked)
    return {"files": len([p for p in picks if p.why == "random"]), "targeted": len([p for p in picks if p.why != "random"]),
            "fields": checked, "wrong": wrong, "upper": hi}


def retrieval_signals(store: TraceStore) -> dict[str, int]:
    rows = store.by_name("retrieval godavari-policy-register")
    return {"asked": len(rows), "refused": sum(r["status"] == "error" for r in rows),
            "empty": sum(r["status"] == "ok" and r["attrs"]["kaagaz.retrieval.results"] == 0 for r in rows)}


def golden_candidates(store: TraceStore, run: str) -> list[str]:
    """What the golden set should grow by: shapes production saw that the 150 files do not have."""
    out = []
    pages = [r["attrs"]["kaagaz.file.pages"] for r in store.by_name("loan_file") if r["attrs"]["kaagaz.run"] == run]
    long_files = sum(p > 60 for p in pages)
    if long_files:
        out.append(f"{long_files} files over 60 pages this week (the longest of the golden set's 200 files has 40): add "
                   "five masked long-statement files to Day 14's development split, labelled and adjudicated as usual")
    for s in field_signals(store, run):
        if s.status != "in line":
            out.append(f"{s.field}: correction rate {s.rate:.1%} is {s.status} ({s.golden_rate:.1%}); pull this week's "
                       "corrected files for that field into the next labelling session")
    return out


def filter_on_golden_set() -> dict[str, int]:
    """The page filter run over Day 14's 200 golden files. Zero pages held back means the regression gate passes it
    trivially: the gate can only judge the shapes the golden set contains."""
    from evals.golden import select
    from .statements import filter_for_model
    test, dev = select()
    held = files = 0
    for gf in (*dev, *test):
        bundle, _ = gf.build()
        files += 1
        held += filter_for_model(bundle)[1]
    return {"files": files, "pages_held_back": held}
