"""The traces are complete, consistent with the ledger, and the wrappers change nothing they wrap."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

from godavari_obs import paths
from godavari_obs.instrument import TracedModel, TracedRuleSet
from godavari_obs.spans import Tracer
from godavari_review import stamping
from evals import candidates
from evals.day11 import RULESETS
from intake.pipeline import process
from intake.ruleset import check_signoff

STAGES = ("classify", "extract", "pipeline.read", "rules", "route", "review")


def test_one_trace_per_sftp_arrival(run: dict[str, Any], store: Any) -> None:
    roots = store.by_name("loan_file")
    assert len(roots) == sum(len(w.files) for w in run["weeks"]) == 120
    assert len({r["attrs"]["kaagaz.file.id"] for r in roots}) == 120
    assert len({r["trace_id"] for r in roots}) == 120


def test_every_file_trace_has_every_stage_and_valid_parents(store: Any) -> None:
    by_trace: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in store.rows():
        by_trace[r["trace_id"]].append(r)
    for r in store.by_name("loan_file"):
        spans = by_trace[r["trace_id"]]
        names = Counter(s["name"] for s in spans)
        assert all(names[s] == 1 for s in STAGES), (r["attrs"]["kaagaz.file.id"], names)
        ids = {s["span_id"] for s in spans}
        assert all(s["parent_id"] in ids for s in spans if s["parent_id"] is not None)
        assert all(r["start"] <= s["start"] and s["end"] <= r["end"] for s in spans)
        ordered = [next(s for s in spans if s["name"] == n)["start"] for n in ("classify", "rules", "review")]
        assert ordered == sorted(ordered)


def test_trace_rupees_equal_ledger_rupees(run: dict[str, Any], store: Any) -> None:
    traced = sum(r["attrs"]["kaagaz.cost.inr"] for r in store.by_name("loan_file"))
    calls = sum(r["attrs"]["kaagaz.cost.inr"] for r in store.rows("kind = 'model_call'"))
    assert abs(traced - run["ledger_inr"]) < 1e-6
    assert abs(calls - run["ledger_inr"]) < 1e-6


def test_input_tokens_follow_the_convention(store: Any) -> None:
    for r in store.rows("kind = 'model_call'"):
        a = r["attrs"]
        assert a["gen_ai.usage.input_tokens"] >= a["gen_ai.usage.cache_read.input_tokens"] + a["gen_ai.usage.cache_write.input_tokens"]
        assert r["name"] == f"chat {a['gen_ai.request.model']}"


def test_failed_attempts_are_error_spans_with_a_type(store: Any) -> None:
    errors = [r for r in store.rows("kind = 'model_call'") if r["status"] == "error"]
    assert errors and all(r["attrs"]["error.type"] == r["attrs"]["kaagaz.llm.outcome"] for r in errors)


def test_week_one_is_day18s_week(run: dict[str, Any]) -> None:
    mine = [json.dumps(stamping.visible(e), sort_keys=True, ensure_ascii=False) for e in run["weeks"][0].week.log]
    theirs = (paths.DAY18_DATA / "pilot-week-1" / "action-log.jsonl").read_text(encoding="utf-8").splitlines()
    assert mine == theirs


def test_rules_span_names_the_code_that_ran(store: Any) -> None:
    rs = RULESETS["two-wheeler"]
    for r in store.by_name("rules"):
        assert r["attrs"]["kaagaz.rules.fingerprint"] == rs.fingerprint()[:12]
        assert r["attrs"]["kaagaz.rules.status"] == check_signoff(rs, "prototype").status


def test_wrappers_change_no_decision(run: dict[str, Any]) -> None:
    tracer = Tracer("check")
    for fr in run["weeks"][1].files[:12]:
        model = candidates.build("baseline", run_id="pilot-week-2")
        plain = process(fr.shown, model, RULESETS["two-wheeler"], fr.arrived.date())
        tm = TracedModel(candidates.build("baseline", run_id="pilot-week-2"), tracer)
        tr = TracedRuleSet(RULESETS["two-wheeler"], tracer)
        root = tracer.span("d" * 32, "loan_file", "file", fr.arrived)
        tm.bind(root, fr.arrived)
        tr.bind(root, fr.arrived)
        traced = process(fr.shown, tm, tr, fr.arrived.date())
        assert traced.route == plain.route and traced.findings == plain.findings and traced.note == plain.note


def test_core_writes_once_per_approved_file(run: dict[str, Any], store: Any) -> None:
    writes = store.by_name("core.write")
    written = [r for r in store.by_name("loan_file") if r["attrs"]["kaagaz.file.outcome"] == "written to core"]
    assert len(writes) == len(written)
    assert {r["trace_id"] for r in writes} == {r["trace_id"] for r in written}
    routes = {r["trace_id"]: r["attrs"]["kaagaz.route"] for r in store.by_name("route")}
    assert all(routes[r["trace_id"]] in ("review", "ready_for_approval") for r in writes)
    held = [r for r in writes if r["attrs"]["kaagaz.core.held_for_window"]]
    assert all(r["end"].hour == 20 and r["end"].minute == 0 for r in held)
