"""Day 17 project: Godavari's send-back workflow as a state machine with a bounded planner inside, offline.

    python -X utf8 run_demo.py            (from this chapter's code/ folder, in the venv)

  A  the machine: states, transitions, the tool inventory with risk labels, the sign-off gate
  B  one file, two designs: the naive model-directed loop after a crash, and the state machine
  C  budgets and loops: a looping planner, a planner that reaches for a write, the rupee ceiling
  D  approval as a state: who may approve, a bad edit, the deadline that escalates and never approves
  E  the trajectory eval over Day 14's 150 golden test files: v1, a candidate v2, and the naive loop
  F  a synthetic week on the pilot branches with four crashes, then the reconciliation

Writes data/run-report.md (this output), data/trajectory-eval.md, data/state-machine.md,
data/tool-inventory.md, data/approval-queue.json, data/audit-log.jsonl and data/week-log.txt. Under a minute.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

from godavari_workflow import states
from godavari_workflow.approvals import SERVICE_ACCOUNT
from godavari_workflow.budgets import Budget
from godavari_workflow.clock import BusinessClock
from godavari_workflow.day11 import SignoffError
from godavari_workflow.day12 import CostLedger, LLMClient, VirtualClock
from godavari_workflow.day14 import load_truth, select, truth_sha256
from godavari_workflow.engine import ApprovalError, Engine, Systems
from godavari_workflow.naive import NaiveTools, ScriptedNaiveModel, run_naive
from godavari_workflow.planner import ProviderPlanner, ScriptedPlannerProvider, StubPlanner
from godavari_workflow.simulate import Week, reconcile
from godavari_workflow.store import Store
from godavari_workflow.systems import Faults, SimulatedCrash
from godavari_workflow.tools import INVENTORY_EXTRA, TOOLS, ToolCall, execute
from godavari_workflow.trajectory import decision_lines, disagreements, eval_naive, eval_workflow, report_lines

CODE = Path(__file__).resolve().parent
DATA = CODE.parent / "data"
NOW = datetime(2026, 11, 26, 10, 0)          # Thursday of engagement week 5, prototype mode
OUT: list[str] = []


def say(line: str = "") -> None:
    print(line)
    OUT.append(line)


def fresh(planner=None, budget: Budget | None = None, faults: Faults | None = None,
          store: Store | None = None, systems: Systems | None = None) -> Engine:
    return Engine(store or Store(), systems or Systems.open(), BusinessClock(NOW), planner or StubPlanner(),
                  budget=budget, faults=faults)


def pick_files() -> tuple[object, object]:
    """Two golden test files: one whose only gap is the address proof (the naive model's favourite shortcut),
    and one from Guntur for the approval part."""
    test, _ = select()
    probe = fresh()
    address_only = guntur = None
    for gf in test:
        bundle, _ = gf.build()
        tools = NaiveTools(bundle, probe.sys.directory, probe.sys.relay, probe.sys.tracker, probe.sys.core, NOW, NOW.date())
        facing = tools.get_completeness_result(bundle.file_id)["branch_facing"]
        rules = [f["rule_id"] for f in facing]
        if address_only is None and rules and all(r.endswith("DOC-05") for r in rules) and bundle.product == "two-wheeler":
            address_only = gf
        if guntur is None and rules and bundle.branch == "Guntur":
            guntur = gf
        if address_only and guntur:
            return address_only, guntur
    raise RuntimeError("no suitable files in the golden set")


def part_a() -> None:
    say("-- A. The machine --")
    say(f"   {len(states.State)} states, {len(states.TRANSITIONS)} transitions, terminal: "
        f"{', '.join(sorted(states.TERMINAL))}; resting (waits for a person or a branch): "
        f"{', '.join(sorted(states.RESTING - states.TERMINAL))}")
    by_actor = Counter(str(t.actor) for t in states.TRANSITIONS)
    say("   who fires transitions: " + ", ".join(f"{a} {n}" for a, n in sorted(by_actor.items())))
    say("   tools, by risk (the planner sees only read and propose):")
    for t in TOOLS.values():
        say(f"     {t.risk:<20s} {t.name:<24s} {t.side_effect}")
    for t in INVENTORY_EXTRA:
        say(f"     {t['risk']:<20s} {t['name']:<24s} {t['side_effect']}")
    eng = fresh()
    for st in eng.signoff:
        say(f"   rules: {st.banner}")
    try:
        Engine(Store(), Systems.open(), BusinessClock(NOW), StubPlanner(), mode="pilot")
        say("   pilot mode: STARTED (this would be a bug)")
    except SignoffError as e:
        say(f"   pilot mode refused: {e}")
    say()


def part_b(gf) -> None:
    say(f"-- B. One file, two designs: {gf.file_id} ({gf.branch}, {gf.product}), whose only gap is the address proof --")
    bundle, _ = gf.build()
    sysm = Systems.open()
    tools = NaiveTools(bundle, sysm.directory, sysm.relay, sysm.tracker, sysm.core, NOW, NOW.date())
    try:
        run_naive(bundle, tools, ScriptedNaiveModel(), Faults({"naive_after_send_email": 1}))
    except SimulatedCrash as c:
        say(f"   naive loop: the process dies at {c}; the restart has no memory and runs again")
    res = run_naive(bundle, tools, ScriptedNaiveModel(), Faults())
    say("   naive loop, second run: " + " -> ".join(t["tool"] for t in res.trace))
    say(f"   naive result: {sysm.relay.count_for(bundle.file_id)} emails to the branch for one send-back; "
        f"{sysm.core.count_for(bundle.file_id)} core application(s) for a file with its address proof missing; "
        f"approvals asked for: 0")
    say()

    # The state machine, same file: a planner that reaches for a write is refused and stopped.
    eng = fresh(StubPlanner("reach_for_write"))
    eng.receive(bundle)
    eng.run_until_rest(bundle.file_id)
    run = eng.store.get(bundle.file_id)
    refused = [e for e in eng.store.events(bundle.file_id) if e["kind"] == "tool_refused"]
    say(f"   state machine, planner variant reach_for_write: {run.state}; "
        f"refused: {refused[0]['detail']['tool']} ({refused[0]['detail']['result'][:70]})")
    say(f"     failure recorded with the trace: {run.data['failure']}; trace {run.data['trace']}")

    # The state machine with the v1 planner, and a crash after the email left but before it was recorded.
    store_path = Path(tempfile.mkdtemp(prefix="day17-b-"))
    try:
        sys_b = Systems.open(store_path)
        eng = fresh(faults=Faults({"after_send_before_record": 1}), store=Store(store_path / "workflow.sqlite"),
                    systems=sys_b)
        eng.receive(bundle)
        eng.run_until_rest(bundle.file_id)
        row = eng.store.approval(eng.store.get(bundle.file_id).data["approval_id"])
        say(f"   state machine, planner v1: proposal {row['id']} waits for {row['assigned_to']} "
            f"(due {row['due_at']}); emails so far: {sys_b.relay.count_for(bundle.file_id)}")
        try:
            execute(eng._tool_ctx(eng.store.get(bundle.file_id)),
                    ToolCall("send_branch_message", {"approval_id": row["id"]}), states.Actor.PLANNER)
        except Exception as e:  # pragma: no cover - execute never raises
            say(f"   unexpected: {e}")
        last = eng.store.events(bundle.file_id)[-1]
        say(f"   a planner calling send_branch_message directly: {last['kind']}: {last['detail']['result'][:80]}")
        try:
            eng.approve_file(bundle.file_id, row["assigned_to"])
        except ApprovalError as e:
            say(f"   approving the file into the core now: refused: {e}")
        eng.decide_send(row["id"], row["assigned_to"], "approve")
        try:
            eng.run_until_rest(bundle.file_id)
        except SimulatedCrash as c:
            say(f"   approved; the worker dies at {c}: the relay has {sys_b.relay.count_for(bundle.file_id)} email, "
                f"our outbox says {eng.store.outbox_row(eng._msg_key(eng.store.get(bundle.file_id)))['state']}")
        eng.store.close()
        eng2 = fresh(store=Store(store_path / "workflow.sqlite"), systems=Systems.open(store_path))
        resumed = eng2.recover()
        ev = [e for e in eng2.store.events(bundle.file_id) if e["kind"] in ("message_sent", "message_confirmed")]
        say(f"   new worker, recover(): resumed {resumed}; {ev[-1]['kind']} ({ev[-1]['detail']['how']}); "
            f"emails in the relay: {eng2.sys.relay.count_for(bundle.file_id)}; state {eng2.store.get(bundle.file_id).state}")
        say(f"   tracker row: {eng2.sys.tracker.row(bundle.file_id)}")
        eng2.store.close()
    finally:
        shutil.rmtree(store_path, ignore_errors=True)

    # The same crash with a real process kill: three separate Python processes.
    folder = Path(tempfile.mkdtemp(prefix="day17-proc-"))
    try:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
        for step in ("prepare", "send", "recover"):
            p = subprocess.run([sys.executable, "-m", "godavari_workflow.worker", step, str(folder), gf.file_id],
                               cwd=CODE, env=env, capture_output=True, text=True, timeout=120)
            lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
            say(f"   process '{step}': exit code {p.returncode}; " + (" | ".join(lines) if lines else p.stderr[-200:]))
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    say()


def part_c(gf) -> None:
    say("-- C. Budgets and loops --")
    bundle, _ = gf.build()
    eng = fresh(StubPlanner("loop"))
    eng.receive(bundle)
    eng.run_until_rest(bundle.file_id)
    run = eng.store.get(bundle.file_id)
    say(f"   planner variant loop: {run.state}: {run.data['failure']}; trace {run.data['trace']}")
    eng = fresh(StubPlanner("over_ask"))
    eng.receive(bundle)
    eng.run_until_rest(bundle.file_id)
    run = eng.store.get(bundle.file_id)
    reason = next(e["detail"]["reason"] for e in eng.store.events(bundle.file_id)
                  if e["detail"].get("event") == "handed_back")
    say(f"   planner variant over_ask ('to be safe'): {run.state}: {reason[:150]}")

    for label, budget in (("default budget (Rs 2.00)", Budget()), ("tight budget (Rs 0.30)", Budget(max_inr=0.30))):
        ledger = CostLedger()
        client = LLMClient(ScriptedPlannerProvider("v1"), ledger, VirtualClock())
        eng = fresh(ProviderPlanner(client), budget=budget)
        eng.receive(bundle)
        eng.run_until_rest(bundle.file_id)
        run = eng.store.get(bundle.file_id)
        rows = [r for r in ledger.rows if r.file_id == bundle.file_id]
        say(f"   model planner through Day 12's client, {label}: {run.state}; {len(rows)} model calls, "
            f"{sum(r.input_tokens for r in rows):,} input and {sum(r.output_tokens for r in rows):,} output tokens, "
            f"Rs {sum(r.inr for r in rows):.2f} on the ledger")
        if run.state == states.State.FAILED:
            say(f"     stopped: {run.data['failure']}")
        else:
            per_turn = [f"{r.inr:.2f}" for r in rows]
            say(f"     rupees per turn (each turn resends the tools and the history): {', '.join(per_turn)}")
    say()


def part_d(gf) -> None:
    say(f"-- D. Approval as a state: {gf.file_id} ({gf.branch}) --")
    bundle, _ = gf.build()
    eng = fresh()
    eng.receive(bundle)
    eng.run_until_rest(bundle.file_id)
    run = eng.store.get(bundle.file_id)
    row = eng.store.approval(run.data["approval_id"])
    say(f"   proposal {row['id']} assigned to {row['assigned_to']}, due {row['due_at']}")
    for user in (SERVICE_ACCOUNT, "analyst.hyd.07", "bhavani"):
        try:
            eng.decide_send(row["id"], user, "approve")
            say(f"   {user}: APPROVED (this would be a bug)")
        except ApprovalError as e:
            say(f"   {user}: refused: {e}")
    body = json.loads(row["draft_json"])["body"]
    try:
        eng.decide_send(row["id"], row["assigned_to"], "approve", edited_body=body + "\nThe loan is approved.")
    except ApprovalError as e:
        say(f"   {row['assigned_to']} edits in 'The loan is approved.': refused: {str(e)[-110:]}")
    eng.clock.set(datetime(2026, 11, 26, 14, 30))
    moved = eng.tick()
    row = eng.store.approval(row["id"])
    say(f"   14:30, nobody decided: tick() moved {moved}; status {row['status']}, now assigned to {row['assigned_to']} "
        f"(level {row['level']}), due {row['due_at']}")
    eng.clock.set(datetime(2026, 11, 27, 9, 30))
    eng.tick()
    row = eng.store.approval(row["id"])
    say(f"   next morning, still undecided: status {row['status']}, level {row['level']} (flagged overdue; "
        f"no default approval)")
    eng.decide_send(row["id"], row["assigned_to"], "approve", note="checked against the pages")
    eng.run_until_rest(bundle.file_id)
    say(f"   {row['assigned_to']} approves: {eng.store.get(bundle.file_id).state}; one email: "
        f"{eng.sys.relay.count_for(bundle.file_id)}")
    msg = eng.sys.relay.all()[-1]
    say(f"   the email, to {msg['recipient']} (from the directory, never from the model):")
    for line in msg["body"].splitlines():
        say(f"     | {line}")
    say()


def part_e() -> list[str]:
    say("-- E. The trajectory eval: Day 14's golden test split --")
    test, _ = select()
    truth = load_truth()
    say(f"   {len(test)} files; truth file sha256 {truth_sha256()[:16]}; every proposal approved as drafted")
    reps = [eval_workflow("machine, planner v1", StubPlanner("v1"), test, truth, NOW),
            eval_workflow("candidate v2 (memory)", StubPlanner("stale_checklist"), test, truth, NOW),
            eval_naive(test, truth, NOW)]
    lines = report_lines(reps)
    for ln in lines:
        say("   " + ln)
    say("   decisions against the experts (planner v1; the same for v2, which differs only in its path):")
    dl = decision_lines(reps[0])
    for ln in dl:
        say(" " + ln)
    dis = disagreements(reps[0])
    say("   where the workflow and the experts differ:")
    for ln in dis:
        say(" " + ln)
    states_v1 = Counter(f.rest_state for f in reps[0].files)
    say(f"   where the files rest (v1): {dict(states_v1)}")
    say()
    return lines + [""] + dl + [""] + dis


def part_f() -> tuple[list[str], dict]:
    say("-- F. A synthetic week: Kukatpally and Guntur, 26 November to 4 December 2026, four crashes --")
    folder = DATA / "state"
    folder.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    week = Week(folder)
    log = week.run()
    for ln in log.lines:
        if "recovered" in ln or "resumed" in ln or "CRASH" in ln or "refused" in ln or "twice" in ln or "received" in ln:
            say("   " + ln[:230])
    say(f"   people and branches: {dict(sorted(log.counts.items()))}")
    rec = reconcile(week.engine.store, week.engine.sys)
    say("   reconciliation (counted in the relay, the core sandbox and the audit log, not in our own counters):")
    for k, v in rec.items():
        say(f"     {k:34s} {v}")
    say(f"   the week took {time.perf_counter() - t0:.1f} s")
    # exports
    (DATA / "approval-queue.json").write_text(json.dumps(
        [{k: v for k, v in r.items() if k not in ("draft_json", "final_json")} for r in week.engine.store.approvals()],
        indent=1) + "\n", encoding="utf-8", newline="\n")
    with (DATA / "audit-log.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for e in week.engine.store.events():
            fh.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
    (DATA / "week-log.txt").write_text("\n".join(log.lines) + "\n", encoding="utf-8", newline="\n")
    week.engine.store.close()
    say()
    return log.lines, rec


def write_static() -> None:
    (DATA / "state-machine.md").write_text(
        "# The send-back workflow: states and transitions\n\nGenerated by `run_demo.py` from "
        "`godavari_workflow/states.py`, so the picture cannot drift from the code.\n\n```mermaid\n"
        + states.mermaid() + "\n```\n\n| Event | From | To | Fired by | Meaning |\n|---|---|---|---|---|\n"
        + "\n".join(f"| {t.event} | {t.source} | {t.target} | {t.actor} | {t.note} |" for t in states.TRANSITIONS)
        + "\n", encoding="utf-8", newline="\n")
    rows = [f"| {t.name} | {t.risk} | {t.side_effect} | {', '.join(sorted(t.states))} | "
            f"{'planner and engine' if t.risk in ('read', 'propose') else 'engine only'} | {t.description} |"
            for t in TOOLS.values()]
    rows += [f"| {t['name']} | {t['risk']} | {t['side_effect']} | PUSHING | {t['who']} | Day 11's push_to_core |"
             for t in INVENTORY_EXTRA]
    (DATA / "tool-inventory.md").write_text(
        "# Tool inventory: risk class, side effect, who may call\n\nGenerated by `run_demo.py` from "
        "`godavari_workflow/tools.py`.\n\n| Tool | Risk | Side effect | States | Who may call | When to use |\n"
        "|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    started = time.perf_counter()
    DATA.mkdir(exist_ok=True)
    say("== Day 17 · Godavari's send-back workflow: a state machine with a planner inside ==")
    say(f"as of {NOW:%A %d %B %Y %H:%M} IST; prototype mode; synthetic files only; no network, no API key")
    say()
    address_only, guntur = pick_files()
    part_a()
    part_b(address_only)
    part_c(address_only)
    part_d(guntur)
    eval_lines = part_e()
    week_lines, rec = part_f()
    write_static()
    say(f"done in {time.perf_counter() - started:.1f} s; wrote data/run-report.md, trajectory-eval.md, state-machine.md, "
        "tool-inventory.md, approval-queue.json, audit-log.jsonl, week-log.txt")
    (DATA / "run-report.md").write_text("# Day 17 run report\n\nThe output of `python -X utf8 run_demo.py`, verbatim.\n\n"
                                        "```text\n" + "\n".join(OUT) + "\n```\n", encoding="utf-8", newline="\n")
    (DATA / "trajectory-eval.md").write_text("# Trajectory eval on Day 14's golden test split\n\n```text\n"
                                             + "\n".join(eval_lines) + "\n```\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
