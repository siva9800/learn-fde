"""The workflow engine: one handler per state, one transition per step, everything persisted before the next.

    receive(bundle)        a bundle version arrives (new file, resubmission, or a duplicate upload)
    advance(file_id)       do the work of the current state and take exactly one transition
    run_until_rest(id)     advance until the file waits for a person, for the branch, or is terminal
    decide_send(...)       an analyst approves, edits and approves, or rejects a send-back proposal
    approve_file(...)      an analyst approves a file for core entry (never a sanction)
    tick(now)              escalate overdue approvals; move overdue resubmissions to an analyst
    recover()              after a crash: resume every run that was mid-way, repeating no side effect

The model reads (EXTRACTED) and the planner drafts (DRAFTING). Everything else is code: the rules, the route,
who may approve, the send, the core write. That is Day 11's split, applied to a multi-step workflow.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from . import drafts
from .approvals import ASSIGNED_ANALYST, authority_problems, due_at, escalate_overdue
from .budgets import Budget, Meter
from .clock import BusinessClock, add_working_days, parse, stamp
from .day11 import (RULESETS, Approval, ExtractionModel, LoanBundle, PushLog, Route, RuleContext, StubModel,
                    check_signoff, decide, envelope, idempotency_key, push_to_core)
from .day14 import bundle_sha256
from .planner import Planner, PlannerContext, PlannerError
from .serialize import bundle_from_json, bundle_to_json, branch_facing, finding_to_json, output_from_json, output_to_json
from .states import RESTING, Actor, State
from .store import Run, Store
from .systems import BranchDirectory, CoreSandbox, Faults, MailRelay, Tracker
from .tools import PLANNER_RISKS, TOOLS, ToolCall, ToolContext, ToolError, execute, message_key, planner_specs

CORE_FIELDS = ("applicant_name", "pan", "requested_amount")     # what Day 11's run pushes; Day 16 maps the rest


class ApprovalError(PermissionError):
    pass


class WorkflowLoop(RuntimeError):
    pass


@dataclass
class Systems:
    directory: BranchDirectory
    relay: MailRelay
    tracker: Tracker
    core: CoreSandbox
    pushlog: PushLog = field(default_factory=PushLog)

    @classmethod
    def open(cls, folder: Path | None = None) -> Systems:
        if folder is None:
            return cls(BranchDirectory(), MailRelay(), Tracker(), CoreSandbox())
        folder.mkdir(parents=True, exist_ok=True)
        return cls(BranchDirectory(), MailRelay(folder / "godavari-mail-relay.sqlite"),
                   Tracker(folder / "godavari-tracker.sqlite"), CoreSandbox(folder / "core-sandbox.json"))


def day15_policy_search(user: str, query: str, now: datetime) -> list[dict[str, str]]:
    """Day 15's permission-aware search, as `user`. A stale group snapshot becomes a tool error, not a crash."""
    from .day15 import POLICY_FILTER, StaleDirectoryError, policy_service
    try:
        resp = policy_service().search(user, query, now, k=2, f=POLICY_FILTER)
    except StaleDirectoryError as e:
        raise ToolError(f"policy search refused: {e}") from None
    return [{"citation": r.citation, "excerpt": r.chunk.text.splitlines()[0][:160]} for r in resp.results]


class Engine:
    def __init__(self, store: Store, systems: Systems, clock: BusinessClock, planner: Planner, *,
                 model: ExtractionModel | None = None, budget: Budget | None = None, faults: Faults | None = None,
                 mode: str = "prototype", as_of: date | None = None,
                 policy_search: Callable[[str, str, datetime], list[dict[str, str]]] | None = day15_policy_search,
                 wall: Callable[[], float] = time.monotonic) -> None:
        # The signed rules are checked before anything runs: pilot mode refuses unsigned rules, and either
        # mode refuses rules whose code changed since the compliance head's record (Day 11).
        self.signoff = [check_signoff(rs, mode) for rs in RULESETS.values()]
        self.store, self.sys, self.clock, self.planner = store, systems, clock, planner
        self.model = model or StubModel()
        self.budget = budget or Budget()
        self.faults = faults or Faults()
        self.mode = mode
        self.as_of = as_of or clock.now().date()
        self.policy_search = policy_search
        self.wall = wall

    # ---- helpers -----------------------------------------------------------------------------------
    def _at(self) -> str:
        return stamp(self.clock.now())

    def _bundle(self, run: Run) -> LoanBundle:
        return bundle_from_json(self.store.bundle(run.file_id, run.bundle_version)[1])

    def _tool_ctx(self, run: Run) -> ToolContext:
        return ToolContext(self.store, run, self.clock.now(), self.mode, self.sys.directory, self.sys.relay,
                           self.sys.tracker, self.faults, self.policy_search)

    # ---- arrivals ----------------------------------------------------------------------------------
    def receive(self, bundle: LoanBundle) -> str:
        sha = bundle_sha256(bundle)
        at = self._at()
        version = self.store.put_bundle(bundle.file_id, sha, bundle_to_json(bundle), at)
        if version is None:
            self.store.audit(at, bundle.file_id, Actor.BRANCH, "duplicate_upload_ignored", bundle_sha=sha[:12])
            return "duplicate"
        run = self.store.get(bundle.file_id)
        if run is None:
            self.store.create_run(bundle.file_id, bundle.branch, bundle.product, at, {"bundle_sha": sha})
            return "new"
        if run.state == State.AWAITING_RESUBMISSION:
            self.store.transition(run, "resubmitted", Actor.BRANCH, at, cycle=run.cycle + 1, bundle_version=version,
                                  data={"bundle_sha": sha}, bundle_sha=sha[:12], cycle_now=run.cycle + 1)
            return "resubmission"
        self.store.audit(at, bundle.file_id, Actor.BRANCH, "bundle_staged", state=run.state, version=version,
                         note="not picked up: the run is not waiting for documents")
        return "staged"

    # ---- one step ----------------------------------------------------------------------------------
    def advance(self, file_id: str) -> bool:
        run = self.store.get(file_id)
        if run is None:
            raise KeyError(file_id)
        handler = {State.RECEIVED: self._extract, State.EXTRACTED: self._check, State.CHECKED: self._route,
                   State.DRAFTING: self._draft, State.SENDING: self._send, State.APPROVED: self._start_push,
                   State.PUSHING: self._push}.get(run.state)
        if handler is None:
            return False                         # resting: a person, the branch, or nothing at all
        handler(run)
        return True

    def run_until_rest(self, file_id: str) -> State:
        for _ in range(self.budget.max_transitions):
            run = self.store.get(file_id)
            assert run is not None
            if run.state in RESTING:
                return run.state
            self.advance(file_id)
        self.store.audit(self._at(), file_id, Actor.SYSTEM, "workflow_loop", limit=self.budget.max_transitions)
        raise WorkflowLoop(f"{file_id}: {self.budget.max_transitions} transitions without resting")

    def runnable(self) -> list[str]:
        return [r.file_id for r in self.store.runs() if r.state not in RESTING]

    # ---- handlers ----------------------------------------------------------------------------------
    def _extract(self, run: Run) -> None:
        out = self.model.read(self._bundle(run))
        self.faults.check("after_model_read")
        self.store.transition(run, "extracted", Actor.SYSTEM, self._at(), data={"extraction": output_to_json(out)},
                              model=out.model_name, bundle_version=run.bundle_version)

    def _check(self, run: Run) -> None:
        bundle, out = self._bundle(run), output_from_json(run.data["extraction"])
        env_findings, documents, uncertain = envelope(bundle, out)
        ctx = RuleContext(bundle, out, documents, self.as_of, uncertain)
        rs = RULESETS[run.product]
        findings = env_findings + rs.run(ctx)
        route = decide(findings)
        fields = {k: (out.fields[k].value or "") for k in CORE_FIELDS if k in out.fields}
        self.store.transition(run, "checked", Actor.SYSTEM, self._at(),
                              data={"findings": [finding_to_json(f) for f in findings], "route": str(route),
                                    "fields": fields, "rules": f"{rs.product} v{rs.version} {rs.fingerprint()[:12]}"},
                              route=str(route), fired=sorted({f.rule_id for f in findings}))

    def _route(self, run: Run) -> None:
        facing = branch_facing(run.data["findings"])
        if facing and run.cycle < self.budget.max_cycles:
            self.store.transition(run, "route_send_back", Actor.SYSTEM, self._at(),
                                  rules=[f["rule_id"] for f in facing], cycle=run.cycle)
        else:
            reason = ("nothing for the branch; the analyst reviews and approves" if not facing else
                      f"{run.cycle} send-backs already; the analyst calls the branch herself")
            self.store.transition(run, "route_review", Actor.SYSTEM, self._at(), reason=reason)

    def _draft(self, run: Run) -> None:
        tctx = self._tool_ctx(run)
        approver = ASSIGNED_ANALYST[run.branch]
        spent0 = self.planner.spend_inr(run.file_id)
        meter = Meter(self.budget, self.wall, lambda: self.planner.spend_inr(run.file_id) - spent0)
        history: list[dict[str, Any]] = []
        specs = planner_specs()
        self.store.audit(self._at(), run.file_id, Actor.PLANNER, "planner_started", planner=self.planner.name,
                         cycle=run.cycle, budget={"steps": self.budget.max_steps, "inr": self.budget.max_inr,
                                                  "seconds": self.budget.max_seconds})

        def fail(reason: str) -> None:
            self.store.transition(run, "planner_failed", Actor.SYSTEM, self._at(),
                                  data={"failure": reason, "trace": [h["name"] for h in history]},
                                  reason=reason, steps=meter.steps, inr=round(meter.spend_inr(), 4))

        while True:
            stop = meter.before_call()
            if stop:
                return fail(stop)
            try:
                call = self.planner.next_call(PlannerContext(run.file_id, run.branch, run.product, run.cycle,
                                                             approver, specs, list(history)))
            except PlannerError as e:
                return fail(str(e))
            loop = meter.record(call.name, call.args)
            if loop:
                self.store.audit(self._at(), run.file_id, Actor.PLANNER, "loop_detected", tool=call.name, reason=loop)
                return fail(loop)
            result = execute(tctx, call, Actor.PLANNER)
            history.append({"name": call.name, "args": call.args, "ok": result.ok, "content": result.content})
            self.faults.check("mid_drafting")
            tool = TOOLS.get(call.name)
            if result.refused and tool is not None and tool.risk not in PLANNER_RISKS:
                return fail(f"the planner reached for {call.name} ({tool.risk}); refused, and the run stopped")
            if call.name == "propose_send_back" and not result.ok:
                meter.invalid_drafts += 1
                if meter.invalid_drafts >= self.budget.max_invalid_drafts:
                    return fail(f"{meter.invalid_drafts} drafts rejected by code: {tctx.last_problems}")
            if tctx.handed_back:
                self.store.transition(run, "handed_back", Actor.PLANNER, self._at(), reason=tctx.handed_back,
                                      steps=meter.steps)
                return None
            if tctx.proposal is not None:
                return self._enqueue(run, tctx.proposal, meter)

    def _enqueue(self, run: Run, draft: drafts.SendBackDraft, meter: Meter) -> None:
        contact = self.sys.directory.get(run.branch)
        assert contact is not None
        phash = drafts.proposal_hash(draft, contact.mailbox)
        now = self.clock.now()
        approval_id = f"SB-{run.file_id}-c{run.cycle}"
        row = {"id": approval_id, "file_id": run.file_id, "cycle": run.cycle, "proposal_hash": phash,
               "draft_json": draft.model_dump_json(), "assigned_to": ASSIGNED_ANALYST[run.branch],
               "created_at": stamp(now), "due_at": due_at(now, 0)}
        self.store.transition(run, "proposed", Actor.PLANNER, stamp(now), data={"approval_id": approval_id},
                              approval=row, proposal_hash=phash[:16], steps=meter.steps,
                              inr=round(meter.spend_inr(), 4), items=[i.rule_id for i in draft.items])

    def _send(self, run: Run) -> None:
        approval_id = run.data["approval_id"]
        tctx = self._tool_ctx(run)
        res = execute(tctx, ToolCall("send_branch_message", {"approval_id": approval_id}), Actor.SYSTEM)
        if not res.ok:
            self.store.transition(run, "send_failed", Actor.SYSTEM, self._at(), data={"failure": str(res.content)},
                                  reason=str(res.content))
            return
        draft = drafts.SendBackDraft.model_validate_json(self.store.approval(approval_id)["final_json"])  # type: ignore[index]
        waiting = "; ".join(i.rule_id for i in draft.items)
        execute(tctx, ToolCall("update_tracker", {"file_id": run.file_id, "status": "sent back",
                                                  "waiting_on": waiting}), Actor.SYSTEM)
        self.faults.check("after_tracker_before_transition")
        now = self.clock.now()
        self.store.transition(run, "sent", Actor.SYSTEM, stamp(now),
                              data={"message_key": res.content["key"],
                                    "resubmission_due": stamp(add_working_days(now, self.budget.resubmission_days))},
                              key=res.content["key"], sent_now=res.content["sent_now"])

    def _start_push(self, run: Run) -> None:
        key = idempotency_key(run.file_id, run.branch)          # Day 11: file number and branch code, never bytes
        self.store.transition(run, "push_started", Actor.SYSTEM, self._at(), data={"core_key": key},
                              outbox=(key, "core", {"approved_by": run.data["approved_by"]}), key=key)

    def _push(self, run: Run) -> None:
        approval = Approval(analyst_id=run.data["approved_by"], approved_on=parse(run.data["approved_at"]).date())
        try:
            record = push_to_core(run.file_id, run.branch, Route(run.data["route"]), run.data["fields"], approval,
                                  self.sys.core, self.sys.pushlog)
        except (PermissionError, ValueError) as e:
            self.store.transition(run, "push_failed", Actor.SYSTEM, self._at(), data={"failure": str(e)}, reason=str(e))
            return
        self.faults.check("after_core_write_before_record")
        action = self.sys.pushlog.entries[-1]["action"]
        self.store.outbox_done(run.data["core_key"], self._at(), run.file_id, "core_written", record=record, action=action)
        self.store.transition(run, "pushed", Actor.SYSTEM, self._at(), data={"core_record": record},
                              record=record, action=action)

    # ---- people ------------------------------------------------------------------------------------
    def decide_send(self, approval_id: str, user: str, decision: str, *, edited_body: str | None = None,
                    note: str = "") -> Run:
        row = self.store.approval(approval_id)
        if row is None:
            raise ApprovalError(f"no approval {approval_id}")
        run = self.store.get(row["file_id"])
        assert run is not None
        at = self._at()

        def refuse(reason: str) -> ApprovalError:
            self.store.audit(at, run.file_id, Actor.HUMAN, "approval_refused", approval_id=approval_id, user=user,
                             reason=reason)
            return ApprovalError(reason)

        if row["status"] != "PENDING" or run.state != State.AWAITING_APPROVAL:
            raise refuse(f"{approval_id} is {row['status']} and the file is {run.state}; nothing to decide")
        who = authority_problems(user, run.branch, row["assigned_to"])
        if who:
            raise refuse("; ".join(who))
        if decision == "reject":
            return self.store.transition(
                run, "send_rejected", Actor.HUMAN, at,
                approval_update=(approval_id, {"status": "REJECTED", "decided_by": user, "decided_at": at,
                                               "decision_note": note}, {"decision": "reject", "by": user}),
                by=user, note=note)
        if decision != "approve":
            raise refuse(f"unknown decision {decision!r}")
        draft = drafts.SendBackDraft.model_validate_json(row["draft_json"])
        if edited_body is not None:
            draft = draft.model_copy(update={"body": edited_body})
            problems = drafts.problems(draft, file_id=run.file_id, branch_facing=branch_facing(run.data["findings"]),
                                       checklist_version=draft.checklist_version,
                                       citations_seen=set(draft.policy_citations))
            if problems:
                raise refuse("the edited text fails the same checks as the draft: " + "; ".join(problems))
        contact = self.sys.directory.get(run.branch)
        assert contact is not None
        final_hash = drafts.proposal_hash(draft, contact.mailbox)
        key = message_key(run.file_id, run.cycle, final_hash)
        return self.store.transition(
            run, "send_approved", Actor.HUMAN, at, outbox=(key, "message", {"approval_id": approval_id}),
            approval_update=(approval_id, {"status": "APPROVED", "decided_by": user, "decided_at": at,
                                           "decision_note": note, "final_hash": final_hash,
                                           "final_json": draft.model_dump_json()},
                             {"decision": "approve", "by": user, "edited": edited_body is not None,
                              "final_hash": final_hash[:16], "proposal_hash": row["proposal_hash"][:16]}),
            by=user, key=key)

    def approve_file(self, file_id: str, user: str, note: str = "") -> Run:
        run = self.store.get(file_id)
        assert run is not None
        at = self._at()
        problems = authority_problems(user, run.branch, ASSIGNED_ANALYST[run.branch])
        if run.state != State.NEEDS_REVIEW:
            problems.append(f"the file is {run.state}, not waiting for an analyst")
        if run.data.get("route") in (Route.SEND_BACK, Route.BLOCKED):
            problems.append("send-back or block findings are open; the branch must fix the file first")
        if problems:
            self.store.audit(at, file_id, Actor.HUMAN, "file_approval_refused", user=user, reason="; ".join(problems))
            raise ApprovalError("; ".join(problems))
        return self.store.transition(run, "file_approved", Actor.HUMAN, at,
                                     data={"approved_by": user, "approved_at": at}, by=user, note=note)

    # ---- time and recovery -------------------------------------------------------------------------
    def tick(self) -> list[str]:
        now = self.clock.now()
        moved = escalate_overdue(self.store, now)
        for run in self.store.runs(State.AWAITING_RESUBMISSION):
            due = run.data.get("resubmission_due")
            if due and parse(due) <= now:
                self.store.transition(run, "resubmission_overdue", Actor.SYSTEM, stamp(now), due=due,
                                      reason=f"no documents by {due}")
                moved.append(run.file_id)
        return moved

    def recover(self) -> list[tuple[str, str]]:
        """Resume every run that was not resting when the process died. A run in SENDING or PUSHING finds out
        from the outbox and the target system whether its side effect happened; it never simply repeats it."""
        resumed: list[tuple[str, str]] = []
        for run in self.store.runs():
            if run.state in RESTING:
                continue
            ob = None
            if run.state == State.SENDING:
                ob = self.store.outbox_row(self._msg_key(run))
            self.store.audit(self._at(), run.file_id, Actor.SYSTEM, "resumed", state=run.state,
                             outbox=ob["state"] if ob else None)
            resumed.append((run.file_id, str(run.state)))
            self.run_until_rest(run.file_id)
        return resumed

    def _msg_key(self, run: Run) -> str:
        row = self.store.approval(run.data["approval_id"])
        assert row is not None
        return message_key(run.file_id, row["cycle"], row["final_hash"])
