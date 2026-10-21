"""The tool registry: every action the workflow can take, each with a risk class, a side-effect label, typed
arguments, the states it may run in and who may call it.

Risk classes (Day 12 named them; this chapter owns them):
  READ                 no side effect. The planner may call these.
  PROPOSE              puts something in front of a human; changes nothing outside our store. The planner may call it.
  WRITE_REVERSIBLE     changes a Godavari system in a way a person can undo (the tracker row). Code only.
  WRITE_IRREVERSIBLE   cannot be taken back (an email to a branch; an application in the 2009 core). Code only,
                       only in its in-flight state, only against an approved, hash-bound proposal, and keyed.

Least privilege shows up as argument design, not only as an allow-list: the send tool takes an approval id
and nothing else, so no caller can choose the recipient or the text; the contact tool returns the branch and
the role, never an address; the completeness tool reads only the run's own file.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from . import drafts
from .approvals import ASSIGNED_ANALYST
from .day11 import REQUIRED_DOC_TEXT, RULESETS, check_signoff
from .serialize import branch_facing
from .states import Actor, State
from .store import Run, Store
from .systems import BranchDirectory, Faults, MailRelay, Tracker


class Risk(StrEnum):
    READ = "read"
    PROPOSE = "propose"
    WRITE_REVERSIBLE = "write-reversible"
    WRITE_IRREVERSIBLE = "write-irreversible"


PLANNER_RISKS = frozenset({Risk.READ, Risk.PROPOSE})


@dataclass(frozen=True)
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    content: Any
    refused: bool = False           # a permission refusal, as opposed to an ordinary error


@dataclass
class ToolContext:
    """What a tool may see: this run, the systems, the time, and what earlier calls in this run returned."""

    store: Store
    run: Run
    now: datetime
    mode: str
    directory: BranchDirectory
    relay: MailRelay
    tracker: Tracker
    faults: Faults
    policy_search: Callable[[str, str, datetime], list[dict[str, str]]] | None = None
    checklist_seen: str | None = None
    citations_seen: set[str] = field(default_factory=set)
    proposal: drafts.SendBackDraft | None = None
    handed_back: str | None = None
    last_problems: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Tool:
    name: str
    description: str               # one sentence on when to use it: the only routing signal a model has
    risk: Risk
    side_effect: str
    args: type[BaseModel]
    states: frozenset[State]
    run: Callable[[ToolContext, Any], Any]

    def spec(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "risk": str(self.risk),
                "side_effect": self.side_effect, "input_schema": self.args.model_json_schema()}


class ToolError(Exception):
    pass


# ---- arguments ---------------------------------------------------------------------------------------
class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FileArg(_Strict):
    file_id: str = Field(pattern=r"^GF-\d{5}$")


class BranchArg(_Strict):
    branch: str = Field(min_length=3, max_length=40)


class ProductArg(_Strict):
    product: Literal["two-wheeler", "gold"]


class QueryArg(_Strict):
    query: str = Field(min_length=5, max_length=300)


class ReasonArg(_Strict):
    reason: str = Field(min_length=10, max_length=300)


class ProposeArgs(_Strict):
    items: list[drafts.SendBackItem] = Field(min_length=1, max_length=20)
    body: str = Field(min_length=20, max_length=2400)
    checklist_version: str
    policy_citations: list[str] = Field(default_factory=list, max_length=5)


class TrackerArgs(_Strict):
    file_id: str = Field(pattern=r"^GF-\d{5}$")
    status: Literal["sent back", "with analyst", "keyed"]
    waiting_on: str = Field(max_length=200)


class ApprovalArg(_Strict):
    approval_id: str = Field(pattern=r"^SB-GF-\d{5}-c\d+$")


# ---- the facts the read tools serve -------------------------------------------------------------------
def checklist_version(product: str, mode: str) -> str:
    """The checklist in force, from the signed code itself: version, sign-off status, code fingerprint.
    Day 6 found that branches work from old printouts (CHECKLIST_DRIFT); this string is how a branch knows."""
    rs = RULESETS[product]
    status = check_signoff(rs, mode)
    return f"{product} checklist v{rs.version} ({status.status}, code {rs.fingerprint()[:12]})"


def _own_file(ctx: ToolContext, file_id: str) -> None:
    if file_id != ctx.run.file_id:
        raise ToolError(f"this run may read only its own file ({ctx.run.file_id}), not {file_id}")


def _completeness(ctx: ToolContext, a: FileArg) -> dict[str, Any]:
    _own_file(ctx, a.file_id)
    findings = ctx.run.data.get("findings", [])
    return {"file_id": a.file_id, "route": ctx.run.data.get("route"), "cycle": ctx.run.cycle,
            "branch": ctx.run.branch, "product": ctx.run.product,
            "branch_facing": [{k: f[k] for k in ("rule_id", "action", "message", "doc")} for f in branch_facing(findings)],
            "review_findings_for_the_analyst": sum(f["action"] == "review" for f in findings)}


def _contact(ctx: ToolContext, a: BranchArg) -> dict[str, Any]:
    if a.branch != ctx.run.branch:
        raise ToolError(f"this run's file is from {ctx.run.branch}; it may not look up {a.branch}")
    c = ctx.directory.get(a.branch)
    if c is None:
        raise ToolError(f"no branch named {a.branch}")
    return {"branch": c.branch, "branch_code": c.branch_code, "addressee": f"the {c.role}, {c.branch} ({c.branch_code})",
            "note": "the mailbox is resolved by code at send time; you never need an address"}


def _checklist(ctx: ToolContext, a: ProductArg) -> dict[str, Any]:
    version = checklist_version(a.product, ctx.mode)
    ctx.checklist_seen = version
    return {"version": version, "required": REQUIRED_DOC_TEXT[a.product]}


def _policy(ctx: ToolContext, a: QueryArg) -> dict[str, Any]:
    if ctx.policy_search is None:
        raise ToolError("the policy search is not configured for this run")
    user = ASSIGNED_ANALYST[ctx.run.branch]
    hits = ctx.policy_search(user, a.query, ctx.now)
    ctx.citations_seen.update(h["citation"] for h in hits)
    return {"searched_as": user, "results": hits}


def _history(ctx: ToolContext, a: FileArg) -> dict[str, Any]:
    _own_file(ctx, a.file_id)
    rows = [r for r in ctx.store.approvals("APPROVED") if r["file_id"] == a.file_id]
    out = []
    for r in rows:
        draft = drafts.SendBackDraft.model_validate_json(r["final_json"])
        out.append({"cycle": r["cycle"], "sent_on": r["decided_at"], "rules": [i.rule_id for i in draft.items]})
    return {"file_id": a.file_id, "earlier_send_backs": out}


def _propose(ctx: ToolContext, a: ProposeArgs) -> dict[str, Any]:
    draft = drafts.SendBackDraft(file_id=ctx.run.file_id, items=a.items, body=a.body,
                                 checklist_version=a.checklist_version, policy_citations=a.policy_citations)
    problems = drafts.problems(draft, file_id=ctx.run.file_id, branch_facing=branch_facing(ctx.run.data["findings"]),
                               checklist_version=checklist_version(ctx.run.product, ctx.mode),
                               citations_seen=ctx.citations_seen)
    if problems:
        ctx.last_problems = problems
        raise ToolError("draft rejected by code: " + "; ".join(problems))
    ctx.proposal = draft
    return {"accepted": True, "note": "queued for the assigned analyst; nothing has been sent"}


def _hand_back(ctx: ToolContext, a: ReasonArg) -> dict[str, Any]:
    ctx.handed_back = a.reason
    return {"handed_back": True}


def _tracker(ctx: ToolContext, a: TrackerArgs) -> dict[str, Any]:
    _own_file(ctx, a.file_id)
    ctx.tracker.upsert(a.file_id, a.status, a.waiting_on, ctx.now.strftime("%Y-%m-%d"), "svc-kaagaz-workflow")
    return {"row": ctx.tracker.row(a.file_id)}


def message_key(file_id: str, cycle: int, final_hash: str) -> str:
    """One message per file per cycle per approved text. Content-derived, so a retry computes the same key."""
    return "msg-" + hashlib.sha256(f"{file_id}|{cycle}|{final_hash}".encode()).hexdigest()[:24]


def _send(ctx: ToolContext, a: ApprovalArg) -> dict[str, Any]:
    row = ctx.store.approval(a.approval_id)
    if row is None or row["file_id"] != ctx.run.file_id:
        raise ToolError(f"no approval {a.approval_id} for {ctx.run.file_id}")
    if row["status"] != "APPROVED":
        raise ToolError(f"approval {a.approval_id} is {row['status']}; nothing is sent without an approval")
    draft = drafts.SendBackDraft.model_validate_json(row["final_json"])
    contact = ctx.directory.get(ctx.run.branch)
    assert contact is not None
    if drafts.proposal_hash(draft, contact.mailbox) != row["final_hash"]:
        raise ToolError("the text or recipient differs from what the analyst approved")
    key = message_key(ctx.run.file_id, row["cycle"], row["final_hash"])
    already = ctx.relay.find_by_key(key)                    # lookup before send: the relay's message trace
    if already:
        ctx.store.outbox_done(key, ctx.now.strftime("%Y-%m-%d %H:%M"), ctx.run.file_id, "message_confirmed",
                              relay_seq=already[0], how="found in the relay's trace; not sent again")
        return {"key": key, "relay_seq": already[0], "sent_now": False}
    subject = f"Documents needed for file {ctx.run.file_id} (send-back {row['cycle'] + 1})"
    seq = ctx.relay.send(key, contact.mailbox, subject, draft.body, ctx.now.strftime("%Y-%m-%d %H:%M"))
    ctx.faults.check("after_send_before_record")
    ctx.store.outbox_done(key, ctx.now.strftime("%Y-%m-%d %H:%M"), ctx.run.file_id, "message_sent",
                          relay_seq=seq, to_role=contact.role, branch_code=contact.branch_code)
    return {"key": key, "relay_seq": seq, "sent_now": True}


TOOLS: dict[str, Tool] = {t.name: t for t in (
    Tool("get_completeness_result", "Read the rule findings for this run's file: what the branch must fix and why. "
         "Call it first.", Risk.READ, "none", FileArg, frozenset({State.DRAFTING}), _completeness),
    Tool("get_branch_contact", "Read who at this file's branch receives a send-back (role and branch code).",
         Risk.READ, "none", BranchArg, frozenset({State.DRAFTING}), _contact),
    Tool("get_current_checklist", "Read the checklist version in force and the wording of each required document. "
         "Call it before proposing; never quote a checklist from memory.", Risk.READ, "none", ProductArg,
         frozenset({State.DRAFTING}), _checklist),
    Tool("search_policy", "Search approved policy circulars for the clause behind an address-proof finding, "
         "as the analyst who will approve.", Risk.READ, "none (logged in the view log)", QueryArg,
         frozenset({State.DRAFTING}), _policy),
    Tool("get_file_history", "Read earlier send-backs for this file, when the cycle is above zero.", Risk.READ,
         "none", FileArg, frozenset({State.DRAFTING}), _history),
    Tool("propose_send_back", "Propose the send-back: one item per fired rule, a short body for the branch manager. "
         "It is checked by code and queued for an analyst; it sends nothing.", Risk.PROPOSE,
         "creates an approval-queue item", ProposeArgs, frozenset({State.DRAFTING}), _propose),
    Tool("hand_to_analyst", "Say you cannot draft this one, and why; an analyst takes the file.", Risk.PROPOSE,
         "moves the file to the analyst's review list", ReasonArg, frozenset({State.DRAFTING}), _hand_back),
    Tool("update_tracker", "Set the tracker row's status and 'waiting on' text for this file.",
         Risk.WRITE_REVERSIBLE, "changes the credit-ops tracker row (an analyst can change it back)", TrackerArgs,
         frozenset({State.SENDING}), _tracker),
    Tool("send_branch_message", "Send the approved send-back to the branch manager's role mailbox.",
         Risk.WRITE_IRREVERSIBLE, "emails a branch manager; cannot be unsent", ApprovalArg,
         frozenset({State.SENDING}), _send),
)}
# push_to_core is not in this registry as a callable: it is Day 11's push_to_core, driven only from the
# PUSHING state by the engine (engine.py), with Day 11's approval and route checks and lookup-before-create.
INVENTORY_EXTRA = [{"name": "push_to_core", "risk": str(Risk.WRITE_IRREVERSIBLE),
                    "side_effect": "creates an application in the 2009 core; we cannot delete it",
                    "who": "engine only, from PUSHING, after an analyst's file approval (Day 11 push_to_core)"}]


def planner_specs() -> list[dict[str, Any]]:
    return [t.spec() for t in TOOLS.values() if t.risk in PLANNER_RISKS]


def execute(ctx: ToolContext, call: ToolCall, actor: Actor) -> ToolResult:
    """Run one call with every check in front of it. Audits the call, whatever happens."""
    tool = TOOLS.get(call.name)
    at = ctx.now.strftime("%Y-%m-%d %H:%M")

    def done(result: ToolResult, risk: str) -> ToolResult:
        ctx.store.audit(at, ctx.run.file_id, str(actor), "tool_refused" if result.refused else "tool_called",
                        tool=call.name, risk=risk, args=_redact(call.args), ok=result.ok,
                        result=_summary(result.content))
        return result

    if tool is None:
        known = sorted(n for n, t in TOOLS.items() if actor != Actor.PLANNER or t.risk in PLANNER_RISKS)
        return done(ToolResult(False, f"no tool named {call.name}; available: {known}", refused=True), "unknown")
    if actor == Actor.PLANNER and tool.risk not in PLANNER_RISKS:
        return done(ToolResult(False, f"{call.name} is {tool.risk}; a planner may only read and propose",
                               refused=True), str(tool.risk))
    if ctx.run.state not in tool.states:
        return done(ToolResult(False, f"{call.name} may run only in {sorted(str(x) for x in tool.states)}, not {ctx.run.state}",
                               refused=True), str(tool.risk))
    try:
        args = tool.args.model_validate(call.args)
    except ValidationError as e:
        err = e.errors()[0]
        return done(ToolResult(False, f"invalid arguments: {'.'.join(map(str, err['loc']))}: {err['msg']}"),
                    str(tool.risk))
    try:
        return done(ToolResult(True, tool.run(ctx, args)), str(tool.risk))
    except ToolError as e:
        return done(ToolResult(False, str(e)), str(tool.risk))


def _redact(args: dict[str, Any]) -> dict[str, Any]:
    """The audit keeps what was asked, not the prose: a body is kept by length and hash, not by text."""
    out = dict(args)
    if "body" in out:
        body = str(out["body"])
        out["body"] = f"<{len(body)} chars, sha256 {hashlib.sha256(body.encode()).hexdigest()[:12]}>"
    if "items" in out:
        out["items"] = [i.get("rule_id") if isinstance(i, dict) else str(i) for i in out["items"]]
    return out


def _summary(content: Any) -> Any:
    text = str(content)
    return text if len(text) <= 160 else text[:157] + "..."
