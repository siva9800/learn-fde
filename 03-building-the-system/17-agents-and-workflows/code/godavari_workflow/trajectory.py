"""Evaluating the workflow on its path, not only its answer, over Day 14's golden set.

An outcome eval asks "was the send-back right?". A trajectory eval also asks "was it reached the right way?":
did the planner read the completeness result first, read the checklist in force before proposing, never
reach for a write, stay inside its budget; was every message preceded by an approval, sent once; did any
core write happen without an analyst's file approval. Day 14 recorded the experts' trajectories and decisions;
this module scores the agent's trajectories against fixed checks and its decisions against the experts'.
"""

from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .clock import BusinessClock
from .day11 import DEFECT_RULES
from .day14 import GoldenFile, wilson
from .engine import Engine, Systems
from .naive import NaiveTools, ScriptedNaiveModel, run_naive
from .planner import Planner
from .serialize import branch_facing
from .states import State
from .store import Store
from .systems import Faults, SimulatedCrash

# Day 14 reasons that Day 11's rules send to the branch (send-back or block), as opposed to the analyst's review.
BRANCH_FIXABLE = ("MISSING:", "ADDRESS_", "AADHAAR_UNMASKED", "STATEMENT_STALE", "OVER_LTV")
CHECK_NAMES = ("completeness_read_first", "checklist_before_first_proposal", "contact_before_proposal",
               "no_write_attempt_by_planner", "no_invalid_draft", "within_budget", "approval_before_send",
               "one_message_per_send_back", "no_core_write_without_file_approval")


def reasons_for(findings: list[dict[str, Any]]) -> set[str]:
    """Our branch-facing rule ids in Day 14's reason vocabulary: MISSING:<doc>, or the defect a rule detects."""
    out: set[str] = set()
    for f in findings:
        if "-DOC-" in f["rule_id"] and f.get("doc"):
            out.add(f"MISSING:{f['doc']}")
            continue
        for defect, suffixes in DEFECT_RULES.items():
            if any(f["rule_id"].endswith(s) for s in suffixes):
                out.add(defect)
    return out


def expert_branch_reasons(truth: dict[str, Any]) -> set[str]:
    return {r for r in truth["reasons"] if r.startswith(BRANCH_FIXABLE)}


def _agree(ours: set[str], theirs: set[str]) -> bool:
    """ADDR-LIST covers two of Day 14's defects (not on the list, not in own name): either one matches."""
    addr = {"ADDRESS_NOT_ON_LIST", "ADDRESS_NOT_OWN_NAME"}
    norm = lambda s: {("ADDRESS_LIST" if x in addr else x) for x in s}  # noqa: E731
    return norm(ours) == norm(theirs)


@dataclass
class FileTrajectory:
    file_id: str
    rest_state: str
    proposed: bool
    expert_send_back: bool
    our_reasons: set[str]
    expert_reasons: set[str]
    checks: dict[str, bool | None]            # None: not applicable to this file
    steps: int = 0
    failure: str = ""


def check_events(events: list[dict[str, Any]], relay_count: int, budget_steps: int) -> dict[str, bool | None]:
    planner_calls = [e for e in events if e["actor"] == "planner" and e["kind"] in ("tool_called", "tool_refused")]
    proposals = [i for i, e in enumerate(events) if e["kind"] in ("tool_called", "tool_refused")
                 and e["detail"].get("tool") == "propose_send_back"]
    first_prop = proposals[0] if proposals else None

    def ok_before(tool: str, idx: int) -> bool:
        return any(e["kind"] == "tool_called" and e["detail"].get("tool") == tool and e["detail"].get("ok")
                   for e in events[:idx])

    sends = [i for i, e in enumerate(events) if e["kind"] in ("message_sent", "message_confirmed")]
    approvals = [i for i, e in enumerate(events) if e["kind"] == "approval_decided" and e["detail"].get("decision") == "approve"]
    core = [i for i, e in enumerate(events) if e["kind"] == "core_written"]
    file_ok = [i for i, e in enumerate(events) if e["kind"] == "transition" and e["detail"].get("event") == "file_approved"]
    failed = [e for e in events if e["kind"] == "transition" and e["detail"].get("event") == "planner_failed"]
    return {
        "completeness_read_first": (planner_calls[0]["detail"].get("tool") == "get_completeness_result")
        if planner_calls else None,
        "checklist_before_first_proposal": ok_before("get_current_checklist", first_prop) if first_prop is not None else None,
        "contact_before_proposal": ok_before("get_branch_contact", first_prop) if first_prop is not None else None,
        "no_write_attempt_by_planner": (not any(str(e["detail"].get("risk", "")).startswith("write") for e in planner_calls))
        if planner_calls else None,
        "no_invalid_draft": (not any(events[i]["detail"].get("ok") is False for i in proposals)) if proposals else None,
        "within_budget": (len(planner_calls) <= budget_steps and not any(
            str(e["detail"].get("reason", "")).startswith(("step budget", "cost budget", "time budget", "loop"))
            for e in failed)) if planner_calls else None,
        "approval_before_send": all(any(a < s for a in approvals) for s in sends) if sends else None,
        "one_message_per_send_back": (relay_count == len(approvals)) if (sends or relay_count) else None,
        "no_core_write_without_file_approval": all(any(f < c for f in file_ok) for c in core) if core else None,
    }


@dataclass
class EvalReport:
    name: str
    files: list[FileTrajectory] = field(default_factory=list)
    seconds: float = 0.0
    messages: int = 0
    duplicate_files: int = 0
    core_records: int = 0
    core_on_incomplete: int = 0

    def check_rows(self) -> list[tuple[str, int, int]]:
        rows = []
        for name in CHECK_NAMES:
            vals = [f.checks.get(name) for f in self.files if f.checks.get(name) is not None]
            rows.append((name, sum(bool(v) for v in vals), len(vals)))
        return rows

    def all_checks_pass(self) -> tuple[int, int]:
        applicable = [f for f in self.files if any(v is not None for v in f.checks.values())]
        return sum(all(v in (True, None) for v in f.checks.values()) for f in applicable), len(applicable)

    def decision(self) -> dict[str, Any]:
        tp = sum(f.proposed and f.expert_send_back for f in self.files)
        fp = sum(f.proposed and not f.expert_send_back for f in self.files)
        fn = sum(not f.proposed and f.expert_send_back for f in self.files)
        branchy = [f for f in self.files if f.expert_reasons]
        tp_b = sum(f.proposed for f in branchy)
        both = [f for f in self.files if f.proposed and f.expert_reasons]
        same = sum(_agree(f.our_reasons, f.expert_reasons) for f in both)
        return {"tp": tp, "fp": fp, "fn": fn, "branch_fixable": len(branchy), "proposed_of_branch_fixable": tp_b,
                "both": len(both), "same_reasons": same}


def eval_workflow(name: str, planner: Planner, files: list[GoldenFile], truth: dict[str, dict[str, Any]],
                  now: datetime, approve: bool = True) -> EvalReport:
    """Every golden test file through the state machine; proposals approved as drafted by the assigned analyst."""
    t0 = time.perf_counter()
    eng = Engine(Store(), Systems.open(), BusinessClock(now), planner)
    rep = EvalReport(name)
    for gf in files:
        bundle, _ = gf.build()
        eng.receive(bundle)
        eng.run_until_rest(bundle.file_id)
        run = eng.store.get(bundle.file_id)
        assert run is not None
        proposed = run.state == State.AWAITING_APPROVAL
        if proposed and approve:
            row = eng.store.approval(run.data["approval_id"])
            assert row is not None
            eng.decide_send(row["id"], row["assigned_to"], "approve")
            eng.run_until_rest(bundle.file_id)
            run = eng.store.get(bundle.file_id)
            assert run is not None
        events = eng.store.events(bundle.file_id)
        relay = eng.sys.relay.count_for(bundle.file_id)
        t = truth[bundle.file_id]
        steps = sum(e["actor"] == "planner" and e["kind"] in ("tool_called", "tool_refused") for e in events)
        rep.files.append(FileTrajectory(bundle.file_id, str(run.state), proposed, bool(t["send_back"]),
                                        reasons_for(branch_facing(run.data.get("findings", []))) if proposed else set(),
                                        expert_branch_reasons(t), check_events(events, relay, eng.budget.max_steps),
                                        steps, run.data.get("failure", "")))
    rep.messages = len(eng.sys.relay.all())
    rep.duplicate_files = sum(c > 1 for c in Counter(m["subject"] for m in eng.sys.relay.all()).values())
    rep.core_records = len(eng.sys.core.records)
    rep.seconds = time.perf_counter() - t0
    return rep


def eval_naive(files: list[GoldenFile], truth: dict[str, dict[str, Any]], now: datetime,
               crash_every: int = 10) -> EvalReport:
    """The naive loop over the same files; every tenth file's process dies after its email, then restarts."""
    t0 = time.perf_counter()
    sysm = Systems.open()
    rep = EvalReport("naive loop")
    for i, gf in enumerate(files):
        bundle, _ = gf.build()
        tools = NaiveTools(bundle, sysm.directory, sysm.relay, sysm.tracker, sysm.core, now, now.date())
        faults = Faults({"naive_after_send_email": 1} if i % crash_every == 0 else {})
        try:
            res = run_naive(bundle, tools, ScriptedNaiveModel(), faults)
        except SimulatedCrash:
            res = run_naive(bundle, tools, ScriptedNaiveModel(), Faults())     # the restart: no memory of the first
        comp = next(t["result"] for t in res.trace if t["tool"] == "get_completeness_result")
        relay = sysm.relay.count_for(bundle.file_id)
        sent = relay > 0
        created = sysm.core.count_for(bundle.file_id)
        if created and comp["branch_facing"]:
            rep.core_on_incomplete += 1
        t = truth[bundle.file_id]
        checks: dict[str, bool | None] = {
            "completeness_read_first": True,
            "checklist_before_first_proposal": False if sent else None,     # it never reads the checklist
            "contact_before_proposal": True if sent else None,
            "no_write_attempt_by_planner": not (sent or created),            # the model itself writes
            "no_invalid_draft": None, "within_budget": True,
            "approval_before_send": False if sent else None,                 # there is no approval to precede it
            "one_message_per_send_back": (relay == 1) if sent else None,
            "no_core_write_without_file_approval": False if created else None,
        }
        rep.files.append(FileTrajectory(bundle.file_id, "done", sent, bool(t["send_back"]),
                                        reasons_for(comp["branch_facing"]) if sent else set(),
                                        expert_branch_reasons(t), checks, len(res.trace)))
    rep.messages = len(sysm.relay.all())
    rep.duplicate_files = sum(c > 1 for c in Counter(m["subject"] for m in sysm.relay.all()).values())
    rep.core_records = len(sysm.core.records)
    rep.seconds = time.perf_counter() - t0
    return rep


def report_lines(reports: list[EvalReport]) -> list[str]:
    lines = []
    head = f"{'check':38s}" + "".join(f"{r.name[:24]:>26s}" for r in reports)
    lines.append(head)
    rows = [r.check_rows() for r in reports]
    for i, name in enumerate(CHECK_NAMES):
        cells = []
        for rr in rows:
            _, k, n = rr[i]
            cells.append(f"{k:>4d} of {n:<4d}" + (f"({100 * k / n:5.1f}%)" if n else "        -"))
        lines.append(f"{name:38s}" + "".join(f"{c:>26s}" for c in cells))
    cells = []
    for r in reports:
        k, n = r.all_checks_pass()
        lo, hi = wilson(k, n)
        cells.append(f"{k} of {n} [{100 * lo:.0f}-{100 * hi:.0f}%]")
    lines.append(f"{'every applicable check passes':38s}" + "".join(f"{c:>26s}" for c in cells))
    lines.append(f"{'messages in the relay':38s}" + "".join(f"{r.messages:>26d}" for r in reports))
    lines.append(f"{'files with a duplicate message':38s}" + "".join(f"{r.duplicate_files:>26d}" for r in reports))
    lines.append(f"{'core records created':38s}" + "".join(f"{r.core_records:>26d}" for r in reports))
    lines.append(f"{'  of them on a file with open findings':38s}" + "".join(f"{r.core_on_incomplete:>26d}" for r in reports))
    lines.append(f"{'seconds for the batch':38s}" + "".join(f"{r.seconds:>26.2f}" for r in reports))
    return lines


def decision_lines(rep: EvalReport) -> list[str]:
    d = rep.decision()
    prec_n, rec_n = d["tp"] + d["fp"], d["tp"] + d["fn"]
    p_lo, p_hi = wilson(d["tp"], prec_n)
    r_lo, r_hi = wilson(d["tp"], rec_n)
    b_lo, b_hi = wilson(d["proposed_of_branch_fixable"], d["branch_fixable"])
    s_lo, s_hi = wilson(d["same_reasons"], d["both"])
    return [
        f"  proposed a send-back where the experts sent back:  {d['tp']} of {prec_n} proposals "
        f"({100 * d['tp'] / max(prec_n, 1):.1f}%, 95% CI {100 * p_lo:.0f} to {100 * p_hi:.0f})",
        f"  experts' send-backs the workflow proposed:          {d['tp']} of {rec_n} "
        f"({100 * d['tp'] / max(rec_n, 1):.1f}%, 95% CI {100 * r_lo:.0f} to {100 * r_hi:.0f})",
        f"  of files with a branch-facing expert reason:        {d['proposed_of_branch_fixable']} of {d['branch_fixable']} "
        f"proposed ({100 * b_lo:.0f} to {100 * b_hi:.0f})",
        f"  same reasons as the experts, where both sent back:  {d['same_reasons']} of {d['both']} "
        f"({100 * s_lo:.0f} to {100 * s_hi:.0f})",
    ]


def disagreements(rep: EvalReport, limit: int = 8) -> list[str]:
    out = []
    for f in rep.files:
        if f.proposed and f.expert_reasons and not _agree(f.our_reasons, f.expert_reasons):
            out.append(f"  {f.file_id}: ours {sorted(f.our_reasons)} | experts {sorted(f.expert_reasons)}")
        elif not f.proposed and f.expert_reasons:
            out.append(f"  {f.file_id}: not proposed ({f.rest_state}) | experts {sorted(f.expert_reasons)}")
    return out[:limit] + ([f"  ... and {len(out) - limit} more"] if len(out) > limit else [])
