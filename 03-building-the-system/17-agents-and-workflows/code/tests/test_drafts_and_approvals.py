"""Code disposes of the draft, and approval is a state with an owner, a deadline and no default."""

from __future__ import annotations

import json
from datetime import datetime

import pytest
from conftest import make_engine, to_approval

from godavari_workflow import drafts
from godavari_workflow.approvals import SERVICE_ACCOUNT
from godavari_workflow.clock import add_working_hours
from godavari_workflow.engine import ApprovalError
from godavari_workflow.serialize import branch_facing
from godavari_workflow.states import State
from godavari_workflow.tools import checklist_version


def _check(eng, row, **change) -> list[str]:
    run = eng.store.get(row["file_id"])
    draft = drafts.SendBackDraft.model_validate_json(row["draft_json"]).model_copy(update=change)
    return drafts.problems(draft, file_id=run.file_id, branch_facing=branch_facing(run.data["findings"]),
                           checklist_version=checklist_version(run.product, "prototype"),
                           citations_seen=set(draft.policy_citations))


def test_a_good_draft_has_no_problems_and_cites_every_rule(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["multi"])
    assert _check(eng, row) == []
    run = eng.store.get(row["file_id"])
    body = json.loads(row["draft_json"])["body"]
    assert all(f["rule_id"] in body for f in branch_facing(run.data["findings"]))


def test_over_asking_and_under_asking_are_both_rejected(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["multi"])
    items = json.loads(row["draft_json"])["items"]
    unfired = next(r for r in ("TW-DOC-06", "TW-DOC-12", "GL-DOC-08", "GL-DOC-07") if r not in {i["rule_id"] for i in items})
    extra = items + [{"rule_id": unfired, "issue": "to be safe", "what_to_send": "two years of ITR"}]
    assert any("did not fire" in p for p in _check(eng, row, items=[drafts.SendBackItem(**i) for i in extra]))
    fewer = [drafts.SendBackItem(**i) for i in items[:-1]]
    assert any("not in the items" in p for p in _check(eng, row, items=fewer))


@pytest.mark.parametrize("line, words", [
    ("The loan is approved.", "decision language"),
    ("Call the customer on 98490 12345.", "phone number"),
    ("Customer PAN ABCPK1234L.", "customer identifiers"),
    ("Write to her at ravi@example.com.", "email address"),
])
def test_bodies_that_decide_or_carry_contacts_or_identifiers_are_rejected(files, line, words) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    body = json.loads(row["draft_json"])["body"] + "\n" + line
    assert any(words in p for p in _check(eng, row, body=body))


def test_a_checklist_quoted_from_memory_is_rejected(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    assert any("not the one in force" in p for p in _check(eng, row, checklist_version="two-wheeler checklist v0.2"))


def test_a_citation_the_policy_tool_did_not_return_is_rejected(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    run = eng.store.get(row["file_id"])
    draft = drafts.SendBackDraft.model_validate_json(row["draft_json"]).model_copy(
        update={"policy_citations": ["GFL/CMP/2099/999 · invented"]})
    p = drafts.problems(draft, file_id=run.file_id, branch_facing=branch_facing(run.data["findings"]),
                        checklist_version=checklist_version(run.product, "prototype"), citations_seen=set())
    assert any("not returned by the policy tool" in x for x in p)


@pytest.mark.parametrize("user, reason", [
    (SERVICE_ACCOUNT, "service account"),
    ("analyst.hyd.07", "no group for Guntur"),
    ("bhavani", "neither the assignee nor the team lead"),
])
def test_who_may_not_approve(files, user, reason) -> None:
    eng = make_engine()
    row = to_approval(eng, files["guntur"])
    with pytest.raises(ApprovalError, match=reason):
        eng.decide_send(row["id"], user, "approve")
    assert eng.store.approval(row["id"])["status"] == "PENDING"
    assert eng.store.events(row["file_id"])[-1]["kind"] == "approval_refused"


def test_the_team_lead_may_approve_and_an_edit_is_what_gets_sent(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["guntur"])
    body = json.loads(row["draft_json"])["body"] + "\nPlease ask the customer to bring the originals."
    eng.decide_send(row["id"], "vjw.team.lead", "approve", edited_body=body)
    eng.run_until_rest(row["file_id"])
    assert eng.sys.relay.all()[-1]["body"] == body
    assert eng.store.approval(row["id"])["final_hash"] != row["proposal_hash"]


def test_a_bad_edit_fails_the_same_checks_as_a_draft(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["guntur"])
    body = json.loads(row["draft_json"])["body"] + "\nThe loan is sanctioned."
    with pytest.raises(ApprovalError, match="decision language"):
        eng.decide_send(row["id"], row["assigned_to"], "approve", edited_body=body)
    assert eng.store.get(row["file_id"]).state == State.AWAITING_APPROVAL


def test_an_approval_is_bound_to_the_text_it_approved(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    eng.decide_send(row["id"], row["assigned_to"], "approve")
    tampered = json.loads(eng.store.approval(row["id"])["final_json"])
    tampered["body"] += "\nAlso send the customer's last three salary slips."
    eng.store.conn.execute("UPDATE approvals SET final_json = ? WHERE id = ?", (json.dumps(tampered), row["id"]))
    eng.run_until_rest(row["file_id"])
    run = eng.store.get(row["file_id"])
    assert run.state == State.FAILED and "differs from what the analyst approved" in run.data["failure"]
    assert eng.sys.relay.count_for(row["file_id"]) == 0


def test_a_missed_deadline_escalates_and_never_approves(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["guntur"])
    eng.clock.set(datetime(2026, 11, 26, 14, 30))
    assert eng.tick() == [row["id"]]
    after = eng.store.approval(row["id"])
    assert (after["status"], after["assigned_to"], after["level"]) == ("PENDING", "vjw.team.lead", 1)
    eng.clock.set(datetime(2026, 11, 30, 17, 0))
    eng.tick()
    eng.tick()
    final = eng.store.approval(row["id"])
    assert (final["status"], final["level"]) == ("PENDING", 2)
    assert eng.sys.relay.count_for(row["file_id"]) == 0


def test_deadlines_count_working_hours() -> None:
    assert add_working_hours(datetime(2026, 11, 26, 16, 30), 4) == datetime(2026, 11, 27, 12, 30)
    assert add_working_hours(datetime(2026, 11, 27, 16, 30), 4) == datetime(2026, 11, 30, 12, 30)   # Friday -> Monday
    assert add_working_hours(datetime(2026, 11, 26, 7, 0), 4) == datetime(2026, 11, 26, 13, 30)


def test_a_rejection_sends_nothing_and_hands_the_file_to_the_analyst(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    eng.decide_send(row["id"], row["assigned_to"], "reject", note="I will phone the branch")
    assert eng.store.get(row["file_id"]).state == State.NEEDS_REVIEW
    assert eng.sys.relay.count_for(row["file_id"]) == 0


def test_no_resubmission_in_five_working_days_goes_to_an_analyst_not_a_reminder(files) -> None:
    eng = make_engine()
    row = to_approval(eng, files["address_only"])
    eng.decide_send(row["id"], row["assigned_to"], "approve")
    eng.run_until_rest(row["file_id"])
    due = eng.store.get(row["file_id"]).data["resubmission_due"]
    assert due == "2026-12-03 10:00"                     # Thursday 10:00 plus five working days
    eng.clock.set(datetime(2026, 12, 3, 9, 59))
    assert eng.tick() == []
    eng.clock.set(datetime(2026, 12, 3, 10, 0))
    assert eng.tick() == [row["file_id"]]
    assert eng.store.get(row["file_id"]).state == State.NEEDS_REVIEW
    assert eng.sys.relay.count_for(row["file_id"]) == 1
