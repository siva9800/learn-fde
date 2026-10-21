"""Side effects happen once: across retries, duplicate uploads, crashes between two lines, and a killed process."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from conftest import make_engine, to_approval

from godavari_workflow.approvals import ASSIGNED_ANALYST
from godavari_workflow.day11 import idempotency_key
from godavari_workflow.engine import Engine
from godavari_workflow.serialize import branch_facing
from godavari_workflow.simulate import fix_bundle
from godavari_workflow.states import Actor, State
from godavari_workflow.systems import Faults, SimulatedCrash
from godavari_workflow.tools import ToolCall, execute


def _approve_and_crash(tmp_path: Path, gf, point: str) -> tuple[Engine, str]:
    eng = make_engine(faults=Faults({point: 1}), folder=tmp_path)
    row = to_approval(eng, gf)
    eng.decide_send(row["id"], row["assigned_to"], "approve")
    with pytest.raises(SimulatedCrash):
        eng.run_until_rest(row["file_id"])
    eng.store.close()
    return make_engine(folder=tmp_path), row["file_id"]          # a new worker on the same files


def test_calling_the_send_tool_twice_sends_one_email(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    eng.decide_send(row["id"], row["assigned_to"], "approve")
    run = eng.store.get(row["file_id"])
    ctx = eng._tool_ctx(run)
    first = execute(ctx, ToolCall("send_branch_message", {"approval_id": row["id"]}), Actor.SYSTEM)
    second = execute(ctx, ToolCall("send_branch_message", {"approval_id": row["id"]}), Actor.SYSTEM)
    assert first.content["sent_now"] and not second.content["sent_now"]
    assert first.content["key"] == second.content["key"]
    assert eng.sys.relay.count_for(row["file_id"]) == 1


@pytest.mark.parametrize("point", ["after_send_before_record", "after_tracker_before_transition"])
def test_a_crash_after_the_email_left_does_not_send_it_again(tmp_path, files, point) -> None:
    eng, fid = _approve_and_crash(tmp_path, files["address_only"], point)
    assert eng.sys.relay.count_for(fid) == 1
    assert eng.recover() == [(fid, "SENDING")]
    assert eng.store.get(fid).state == State.AWAITING_RESUBMISSION
    assert eng.sys.relay.count_for(fid) == 1
    assert eng.sys.tracker.row(fid)["status"] == "sent back"


def test_a_crash_mid_draft_leaves_one_proposal(tmp_path, files) -> None:
    eng = make_engine(faults=Faults({"mid_drafting": 2}), folder=tmp_path)
    bundle, _ = files["address_only"].build()
    eng.receive(bundle)
    with pytest.raises(SimulatedCrash):
        eng.run_until_rest(bundle.file_id)
    assert eng.store.get(bundle.file_id).state == State.DRAFTING
    eng.store.close()
    eng2 = make_engine(folder=tmp_path)
    eng2.recover()
    assert eng2.store.get(bundle.file_id).state == State.AWAITING_APPROVAL
    assert len(eng2.store.approvals()) == 1


def test_a_crash_after_the_core_create_does_not_create_twice(tmp_path, files) -> None:
    eng = make_engine(faults=Faults({"after_core_write_before_record": 1}), folder=tmp_path)
    bundle, _ = files["clean"].build()
    eng.receive(bundle)
    eng.run_until_rest(bundle.file_id)
    eng.approve_file(bundle.file_id, ASSIGNED_ANALYST[bundle.branch])
    with pytest.raises(SimulatedCrash):
        eng.run_until_rest(bundle.file_id)
    assert eng.sys.core.count_for(bundle.file_id) == 1
    eng.store.close()
    eng2 = make_engine(folder=tmp_path)
    eng2.recover()
    assert eng2.store.get(bundle.file_id).state == State.PUSHED_TO_CORE
    assert eng2.sys.core.count_for(bundle.file_id) == 1
    assert eng2.sys.pushlog.entries[-1]["action"] == "exists"         # Day 11's lookup-before-create found it


def test_a_duplicate_upload_is_ignored_and_a_resubmission_is_a_new_cycle(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    eng.decide_send(row["id"], row["assigned_to"], "approve")
    eng.run_until_rest(row["file_id"])
    bundle, _ = files["address_only"].build()
    assert eng.receive(bundle) == "duplicate"
    run = eng.store.get(row["file_id"])
    fixed = fix_bundle(bundle, files["address_only"].row, branch_facing(run.data["findings"]))
    assert eng.receive(fixed) == "resubmission"
    assert eng.receive(fixed) == "duplicate"
    after = eng.store.get(row["file_id"])
    assert (after.cycle, after.bundle_version, after.state) == (1, 1, State.RECEIVED)
    assert after.data["bundle_sha"] != run.data["bundle_sha"]
    # The core key is the business intent (file number and branch code), so it is the same for both bundles.
    assert idempotency_key(row["file_id"], after.branch) == idempotency_key(row["file_id"], run.branch)


def test_the_send_back_cycle_cap_hands_the_file_to_an_analyst(files) -> None:
    eng = make_engine()
    gf = files["address_only"]
    bundle, _ = gf.build()
    eng.receive(bundle)
    for cycle in range(2):
        eng.run_until_rest(bundle.file_id)
        run = eng.store.get(bundle.file_id)
        row = eng.store.approval(run.data["approval_id"])
        assert row["id"].endswith(f"c{cycle}")
        eng.decide_send(row["id"], row["assigned_to"], "approve")
        eng.run_until_rest(bundle.file_id)
        # the branch sends the same pages again, with one blank page added: the same gap
        same = replace(bundle, pages=bundle.pages + (replace(bundle.pages[-1], number=len(bundle.pages) + cycle + 1,
                                                             text=f"THIS PAGE IS INTENTIONALLY LEFT BLANK {cycle}"),))
        eng.receive(same)
    eng.run_until_rest(bundle.file_id)
    run = eng.store.get(bundle.file_id)
    assert run.state == State.NEEDS_REVIEW and run.cycle == 2
    assert eng.sys.relay.count_for(bundle.file_id) == 2


def test_a_killed_process_resumes_without_a_second_email(tmp_path, files) -> None:
    code = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
    fid = files["address_only"].file_id
    out = {}
    for step in ("prepare", "send", "recover"):
        out[step] = subprocess.run([sys.executable, "-m", "godavari_workflow.worker", step, str(tmp_path), fid],
                                   cwd=code, env=env, capture_output=True, text=True, timeout=120)
    assert out["prepare"].returncode == 0
    assert out["send"].returncode == 17 and "never printed" not in out["send"].stdout
    assert out["recover"].returncode == 0
    assert f"emails in the relay for {fid}: 1" in out["recover"].stdout
