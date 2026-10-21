"""Who may approve, by when, and what happens when nobody does.

Approval is a state of the file (AWAITING_APPROVAL), and the queue row is its data: the exact proposal hash,
the person it is assigned to, a deadline in working hours, an escalation level. Three rules, each tested:

1. Only a person approves. The workflow's service account has no approval right, and neither does any
   planner; no tool takes an approval decision as an argument.
2. The approver must be able to see the branch (Day 11's `visible_to`, the AD-group rule of finding A1)
   and must be the assigned analyst or her region's team lead.
3. A deadline that passes escalates to the team lead. It never approves by default.

The people are synthetic. The user names match Day 15's directory so the policy tool runs as the same person.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .clock import add_working_hours, parse, stamp
from .day11 import BRANCH_AD_GROUP, visible_to
from .states import Actor
from .store import Store

HYD = ("Kukatpally", "Dilsukhnagar", "Warangal")
VJW = ("Vijayawada-Benz Circle", "Guntur", "Rajahmundry")
APPROVAL_SLA_HOURS = 4.0          # "tell the branch the same day": four working hours to decide
ESCALATED_SLA_HOURS = 2.0         # the team lead's window before the item is flagged overdue at level 2
SERVICE_ACCOUNT = "svc-kaagaz-workflow"


@dataclass(frozen=True)
class Person:
    user: str
    role: str                     # analyst | team_lead | service
    region: str                   # HYD | VJW | -
    groups: frozenset[str]


def _groups(branches: tuple[str, ...]) -> frozenset[str]:
    return frozenset(BRANCH_AD_GROUP[b] for b in branches)


PEOPLE: dict[str, Person] = {
    "analyst.hyd.07": Person("analyst.hyd.07", "analyst", "HYD", _groups(HYD)),   # Kukatpally pilot queue
    "lakshmi": Person("lakshmi", "analyst", "VJW", _groups(VJW)),                 # Guntur pilot queue
    "bhavani": Person("bhavani", "analyst", "VJW", _groups(VJW)),
    "srinivas": Person("srinivas", "team_lead", "HYD", _groups(HYD)),
    "vjw.team.lead": Person("vjw.team.lead", "team_lead", "VJW", _groups(VJW)),
    SERVICE_ACCOUNT: Person(SERVICE_ACCOUNT, "service", "-", frozenset()),
}
ASSIGNED_ANALYST: dict[str, str] = {"Kukatpally": "analyst.hyd.07", "Dilsukhnagar": "analyst.hyd.07",
                                    "Warangal": "analyst.hyd.07", "Guntur": "lakshmi",
                                    "Vijayawada-Benz Circle": "bhavani", "Rajahmundry": "bhavani"}
TEAM_LEAD: dict[str, str] = {"HYD": "srinivas", "VJW": "vjw.team.lead"}


def region_of(branch: str) -> str:
    return "HYD" if branch in HYD else "VJW"


def authority_problems(user: str, branch: str, assigned_to: str) -> list[str]:
    """Why this user may not decide for this branch's file. Empty means she may."""
    person = PEOPLE.get(user)
    if person is None:
        return [f"{user} is not in the directory"]
    out: list[str] = []
    if person.role not in ("analyst", "team_lead"):
        out.append(f"{user} is a {person.role} account; only a named analyst or team lead decides")
    if not visible_to(person.groups, branch):
        out.append(f"{user} has no group for {branch}; she cannot see the file, so she cannot approve it")
    lead = TEAM_LEAD.get(region_of(branch))
    if user not in (assigned_to, lead):
        out.append(f"the item is assigned to {assigned_to}; {user} is neither the assignee nor the team lead ({lead})")
    return out


def due_at(created: datetime, level: int) -> str:
    return stamp(add_working_hours(created, APPROVAL_SLA_HOURS if level == 0 else ESCALATED_SLA_HOURS))


def escalate_overdue(store: Store, now: datetime) -> list[str]:
    """Move overdue items up one level. Returns the approval ids that moved. Never decides anything."""
    moved: list[str] = []
    for row in store.approvals("PENDING"):
        if parse(row["due_at"]) > now:
            continue
        run = store.get(row["file_id"])
        branch = run.branch if run else ""
        lead = TEAM_LEAD[region_of(branch)]
        if row["level"] == 0:
            store.update_approval(row["id"], stamp(now), row["file_id"], Actor.SYSTEM, "approval_escalated",
                                  {"assigned_to": lead, "level": 1, "due_at": due_at(now, 1)},
                                  from_user=row["assigned_to"], to_user=lead, reason="four working hours passed")
            moved.append(row["id"])
        elif row["level"] == 1:
            store.update_approval(row["id"], stamp(now), row["file_id"], Actor.SYSTEM, "approval_overdue",
                                  {"level": 2, "due_at": "9999-12-31 00:00"}, at_user=lead,
                                  reason="still undecided at the team lead; flagged on the queue, not approved")
            moved.append(row["id"])
    return moved
