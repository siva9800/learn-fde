"""Budgets stop loops, the audit log is complete and tamper-evident, the guards hold, and the evals agree."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import NOW, make_engine, to_approval

from godavari_workflow.budgets import Budget
from godavari_workflow.day11 import RuleSet, SignoffError
from godavari_workflow.day12 import CostLedger, LLMClient, VirtualClock
from godavari_workflow.day14 import pii_hits
from godavari_workflow.engine import ApprovalError
from godavari_workflow.naive import NaiveTools, ScriptedNaiveModel, run_naive
from godavari_workflow.planner import ProviderPlanner, ScriptedPlannerProvider, StubPlanner
from godavari_workflow.simulate import CRASH_POINTS, Week, reconcile
from godavari_workflow.states import State
from godavari_workflow.systems import Faults, SimulatedCrash
from godavari_workflow.trajectory import eval_naive, eval_workflow


def _rest(eng, gf):
    bundle, _ = gf.build()
    eng.receive(bundle)
    eng.run_until_rest(bundle.file_id)
    return eng.store.get(bundle.file_id)


def test_a_looping_planner_is_stopped_with_its_trace(files) -> None:
    run = _rest(make_engine(StubPlanner("loop")), files["address_only"])
    assert run.state == State.FAILED and run.data["failure"].startswith("loop:")
    assert run.data["trace"] == ["get_completeness_result", "get_branch_contact"]


def test_the_step_budget_stops_a_planner_that_never_proposes(files) -> None:
    run = _rest(make_engine(budget=Budget(max_steps=2)), files["address_only"])
    assert run.state == State.FAILED and run.data["failure"].startswith("step budget")


def test_the_time_budget_reads_an_injected_clock(files) -> None:
    ticks = iter(range(0, 1000, 20))
    run = _rest(make_engine(wall=lambda: float(next(ticks))), files["address_only"])
    assert run.state == State.FAILED and run.data["failure"].startswith("time budget")


def test_a_planner_that_reaches_for_a_write_is_stopped_and_nothing_is_sent(files) -> None:
    eng = make_engine(StubPlanner("reach_for_write"))
    run = _rest(eng, files["address_only"])
    assert run.state == State.FAILED and "reached for send_branch_message" in run.data["failure"]
    assert eng.sys.relay.all() == []


def test_the_rupee_budget_is_read_from_day_12s_ledger(files) -> None:
    for budget, expected in ((Budget(), State.AWAITING_APPROVAL), (Budget(max_inr=0.30), State.FAILED)):
        ledger = CostLedger()
        eng = make_engine(ProviderPlanner(LLMClient(ScriptedPlannerProvider("v1"), ledger, VirtualClock())), budget=budget)
        run = _rest(eng, files["address_only"])
        assert run.state == expected
        assert ledger.rows and all(r.stage == "plan" for r in ledger.rows)
        if expected == State.FAILED:
            assert run.data["failure"].startswith("cost budget")


def test_the_model_planner_and_the_stub_propose_the_same_draft(files) -> None:
    stub = make_engine()
    row_a = to_approval(stub, files["multi"])
    model = make_engine(ProviderPlanner(LLMClient(ScriptedPlannerProvider("v1"), CostLedger(), VirtualClock())),
                        budget=Budget(max_inr=10.0))
    row_b = to_approval(model, files["multi"])
    assert row_a["proposal_hash"] == row_b["proposal_hash"]


def test_pilot_mode_refuses_unsigned_rules_and_any_mode_refuses_changed_rules(monkeypatch) -> None:
    with pytest.raises(SignoffError, match="pilot mode runs signed rules only"):
        make_engine(mode="pilot")
    monkeypatch.setattr(RuleSet, "fingerprint", lambda self: "0" * 64)
    with pytest.raises(SignoffError, match="changed since the sign-off record"):
        make_engine()


def test_an_analyst_cannot_approve_a_file_with_open_send_back_findings(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    eng.decide_send(row["id"], row["assigned_to"], "reject")
    with pytest.raises(ApprovalError, match="branch must fix the file first"):
        eng.approve_file(row["file_id"], row["assigned_to"])
    assert eng.sys.core.records == []


def test_every_transition_is_in_the_audit_log_and_the_chain_detects_an_edit(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    eng.decide_send(row["id"], row["assigned_to"], "approve")
    eng.run_until_rest(row["file_id"])
    run = eng.store.get(row["file_id"])
    transitions = [e for e in eng.store.events(row["file_id"]) if e["kind"] == "transition"]
    assert len(transitions) == run.version
    assert eng.store.verify_chain() == (True, None)
    seq = transitions[3]["seq"]
    eng.store.conn.execute("UPDATE events SET detail_json = REPLACE(detail_json, 'analyst', 'someone') WHERE seq = ?",
                           (seq,))
    eng.store.conn.execute("UPDATE events SET actor = 'human' WHERE seq = ?", (seq,))
    assert eng.store.verify_chain() == (False, seq)


def test_the_naive_loop_duplicates_after_a_crash_and_writes_without_approval(files) -> None:
    bundle, _ = files["address_only"].build()
    eng = make_engine()
    tools = NaiveTools(bundle, eng.sys.directory, eng.sys.relay, eng.sys.tracker, eng.sys.core, NOW, NOW.date())
    with pytest.raises(SimulatedCrash):
        run_naive(bundle, tools, ScriptedNaiveModel(), Faults({"naive_after_send_email": 1}))
    run_naive(bundle, tools, ScriptedNaiveModel(), Faults())
    assert eng.sys.relay.count_for(bundle.file_id) == 2
    assert eng.sys.core.count_for(bundle.file_id) == 1          # on a file whose address proof is missing


@pytest.fixture(scope="module")
def evals(golden, truth):
    return (eval_workflow("v1", StubPlanner("v1"), golden, truth, NOW),
            eval_workflow("v2", StubPlanner("stale_checklist"), golden, truth, NOW),
            eval_naive(golden, truth, NOW))


def test_the_trajectory_eval_passes_v1_and_catches_what_the_outcome_eval_misses(evals) -> None:
    v1, v2, naive = evals
    assert v1.all_checks_pass()[0] == v1.all_checks_pass()[1] > 50
    assert v1.decision() == v2.decision()                          # same outcomes...
    rows = {name: (k, n) for name, k, n in v2.check_rows()}
    assert rows["checklist_before_first_proposal"][0] == 0         # ...reached the wrong way
    assert rows["no_invalid_draft"][0] == 0
    assert v1.decision()["fp"] == 0


def test_the_trajectory_eval_fails_the_naive_loop(evals) -> None:
    naive = evals[2]
    rows = {name: (k, n) for name, k, n in naive.check_rows()}
    assert rows["approval_before_send"][0] == 0 and rows["approval_before_send"][1] > 50
    assert naive.duplicate_files > 0 and naive.core_on_incomplete > 0


def test_a_week_with_four_crashes_reconciles_to_zero_duplicates(tmp_path: Path) -> None:
    week = Week(tmp_path)
    log = week.run()
    assert sorted(log.crashes) == sorted(CRASH_POINTS)
    rec = reconcile(week.engine.store, week.engine.sys)
    assert rec["duplicate_messages"] == 0 and rec["duplicate_core_records"] == 0
    assert rec["messages"] == rec["approved_send_backs"] > 10
    assert rec["messages_without_an_approval"] == 0 and rec["messages_to_non_branch_addresses"] == 0
    assert rec["core_records"] == rec["pushed_runs"]
    assert rec["audit_chain_ok"]
    assert log.counts.get("bad_edit_accepted", 0) == 0 and log.counts["edit_refused"] == 1
    assert log.counts["escalations"] >= 1
    audit_text = json.dumps(week.engine.store.events())
    assert pii_hits(audit_text) == []                              # no PAN, Aadhaar or mobile in the audit log
