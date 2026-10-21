"""The machine's shape and the tool registry's permissions, tested without running a single file."""

from __future__ import annotations

from collections import deque

import pytest
from conftest import make_engine, to_approval

from godavari_workflow import states
from godavari_workflow.states import Actor, IllegalTransition, State, check_transition
from godavari_workflow.tools import PLANNER_RISKS, TOOLS, ToolCall, execute, planner_specs


def test_every_state_is_reachable_from_received() -> None:
    seen, todo = {State.RECEIVED}, deque([State.RECEIVED])
    while todo:
        s = todo.popleft()
        for t in states.TRANSITIONS:
            if t.source == s and t.target not in seen:
                seen.add(t.target)
                todo.append(t.target)
    assert seen == set(State)


def test_terminal_states_have_no_way_out() -> None:
    assert not [t for t in states.TRANSITIONS if t.source in states.TERMINAL]


def test_only_a_human_fires_the_two_approvals_and_the_planner_never_leaves_drafting() -> None:
    into = {t.event: t.actor for t in states.TRANSITIONS if t.target in (State.APPROVED, State.SENDING)}
    assert set(into.values()) == {Actor.HUMAN}
    assert {t.source for t in states.TRANSITIONS if t.actor == Actor.PLANNER} == {State.DRAFTING}


@pytest.mark.parametrize("actor", [Actor.SYSTEM, Actor.PLANNER, Actor.BRANCH])
def test_file_approval_by_anything_but_a_human_is_illegal(actor: Actor) -> None:
    with pytest.raises(IllegalTransition, match="must be fired by human"):
        check_transition(State.NEEDS_REVIEW, "file_approved", actor)


def test_an_unknown_event_names_the_allowed_ones() -> None:
    with pytest.raises(IllegalTransition, match="allowed: \\['send_approved', 'send_rejected'\\]"):
        check_transition(State.AWAITING_APPROVAL, "auto_approve", Actor.SYSTEM)


def test_the_diagram_is_generated_from_the_table() -> None:
    text = states.mermaid()
    assert all(f"{t.source} --> {t.target}: {t.event}" in text for t in states.TRANSITIONS)


def test_the_planner_sees_only_read_and_propose_tools() -> None:
    names = {s["name"] for s in planner_specs()}
    assert names == {n for n, t in TOOLS.items() if t.risk in PLANNER_RISKS}
    assert "send_branch_message" not in names and "update_tracker" not in names


def test_every_tool_declares_a_risk_and_a_side_effect() -> None:
    for t in TOOLS.values():
        assert t.risk and t.side_effect and t.description.endswith(".")
        assert (t.side_effect == "none") == (t.risk == "read") or t.name == "search_policy"


def test_a_planner_call_to_a_write_tool_is_refused_and_audited(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    run = eng.store.get(row["file_id"])
    res = execute(eng._tool_ctx(run), ToolCall("send_branch_message", {"approval_id": row["id"]}), Actor.PLANNER)
    assert res.refused and not res.ok
    assert eng.store.events(row["file_id"])[-1]["kind"] == "tool_refused"
    assert eng.sys.relay.count_for(row["file_id"]) == 0


def test_read_tools_are_scoped_to_the_runs_own_file_and_never_return_an_address(files) -> None:
    eng = make_engine()
    bundle, _ = files["address_only"].build()
    eng.receive(bundle)
    for _ in range(3):
        eng.advance(bundle.file_id)                    # RECEIVED -> EXTRACTED -> CHECKED -> DRAFTING
    run = eng.store.get(bundle.file_id)
    assert run.state == State.DRAFTING
    ctx = eng._tool_ctx(run)
    other = execute(ctx, ToolCall("get_completeness_result", {"file_id": "GF-49999"}), Actor.PLANNER)
    assert not other.ok and "only its own file" in other.content
    contact = execute(ctx, ToolCall("get_branch_contact", {"branch": bundle.branch}), Actor.PLANNER)
    assert contact.ok and "@" not in str(contact.content)
    bad = execute(ctx, ToolCall("get_completeness_result", {"file_id": "not-a-file"}), Actor.PLANNER)
    assert not bad.ok and bad.content.startswith("invalid arguments")
