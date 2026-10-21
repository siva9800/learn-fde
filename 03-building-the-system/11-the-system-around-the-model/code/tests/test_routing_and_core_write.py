from __future__ import annotations

from datetime import date

import pytest

from intake.core_write import Approval, FakeCoreSandbox, PushLog, idempotency_key, push_to_core
from intake.reference import BRANCH_AD_GROUP
from intake.routing import Route, decide, visible_to
from intake.ruleset import Action, Finding


def _f(action: Action) -> Finding:
    return Finding("X", "policy", action, "m")


def test_no_findings_means_ready_for_approval_not_approved() -> None:
    assert decide([]) == Route.READY_FOR_APPROVAL


@pytest.mark.parametrize("actions, route", [
    ([Action.REVIEW], Route.REVIEW), ([Action.REVIEW, Action.SEND_BACK], Route.SEND_BACK),
    ([Action.SEND_BACK, Action.BLOCK, Action.REVIEW], Route.BLOCKED), ([Action.BLOCK], Route.BLOCKED)])
def test_the_most_severe_finding_decides(actions: list[Action], route: Route) -> None:
    assert decide([_f(a) for a in actions]) == route
    assert decide([_f(a) for a in reversed(actions)]) == route        # order never matters


def test_branch_visibility_has_no_all_branches_fallback() -> None:
    assert visible_to([BRANCH_AD_GROUP["Guntur"]], "Guntur")
    assert not visible_to([BRANCH_AD_GROUP["Guntur"]], "Kukatpally")
    assert not visible_to([], "Guntur")
    assert not visible_to(["GF-ALL-BRANCHES"], "Guntur")


APPROVAL = Approval("GF-AN-1142", date(2026, 11, 9))


def test_nothing_is_written_without_an_analyst_approval() -> None:
    with pytest.raises(PermissionError):
        push_to_core("GF-25001", "Guntur", Route.READY_FOR_APPROVAL, {}, None, FakeCoreSandbox(), PushLog())


def test_a_send_back_file_is_never_written_even_if_approved() -> None:
    with pytest.raises(PermissionError):
        push_to_core("GF-25001", "Guntur", Route.SEND_BACK, {}, APPROVAL, FakeCoreSandbox(), PushLog())


def test_a_retry_does_not_create_a_second_application() -> None:
    sandbox, log = FakeCoreSandbox(), PushLog()
    first = push_to_core("GF-25001", "Guntur", Route.READY_FOR_APPROVAL, {"pan": "ABCPP1234K"}, APPROVAL, sandbox, log)
    second = push_to_core("GF-25001", "Guntur", Route.READY_FOR_APPROVAL, {"pan": "ABCPP1234K"}, APPROVAL, sandbox, log)
    assert first == second and len(sandbox.records) == 1
    assert [e["action"] for e in log.entries] == ["created", "exists"]


def test_the_fake_sandbox_really_does_duplicate_on_a_blind_create() -> None:
    sandbox = FakeCoreSandbox()             # the reason the push function looks up before it creates
    sandbox.create_application({"file_number": "GF-1"})
    sandbox.create_application({"file_number": "GF-1"})
    assert len(sandbox.records) == 2


def test_idempotency_key_is_stable_and_branch_specific() -> None:
    assert idempotency_key("GF-25001", "Guntur") == idempotency_key("GF-25001", "Guntur")
    assert idempotency_key("GF-25001", "Guntur") != idempotency_key("GF-25001", "Kukatpally")


def test_disbursement_before_sanction_is_refused() -> None:
    bad = Approval("GF-AN-1142", date(2026, 11, 9), sanction_date=date(2026, 11, 10), disbursement_date=date(2026, 11, 9))
    with pytest.raises(ValueError):
        push_to_core("GF-25001", "Guntur", Route.READY_FOR_APPROVAL, {}, bad, FakeCoreSandbox(), PushLog())
