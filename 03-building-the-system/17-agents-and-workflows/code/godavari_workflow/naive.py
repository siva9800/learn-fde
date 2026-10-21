"""The naive design, kept so its failures can be shown and tested: one model-directed loop, every tool, no state.

This is what a framework quick-start gives you: a model, a list of tools, `while not done: call the model,
run what it asks`. The model here is scripted (ScriptedNaiveModel), and its choices are the ones a capable
model plausibly makes when it is trying to help: send the branch the list at once, and create the core
record early for a file whose only gap is an address proof "to follow" (Day 6: "address proof often
'to follow'"). Two things go wrong, and neither is the model's fault:

1. There is no approval anywhere, so the email and the core write happen on the model's say-so.
2. There is no durable state, so a crash after the email and before the loop finishes means the restart
   begins again from nothing and sends the email again. A perfect model makes that duplicate too.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .day11 import RULESETS, LoanBundle, Route, RuleContext, StubModel, decide, envelope
from .serialize import branch_facing, finding_to_json
from .systems import BranchDirectory, CoreSandbox, Faults, MailRelay, Tracker


@dataclass
class NaiveResult:
    file_id: str
    trace: list[dict[str, Any]] = field(default_factory=list)
    crashed: bool = False


class NaiveTools:
    """Every tool, with free-text arguments. The model chooses the recipient, the text and when to write."""

    def __init__(self, bundle: LoanBundle, directory: BranchDirectory, relay: MailRelay, tracker: Tracker,
                 core: CoreSandbox, now: datetime, as_of: Any) -> None:
        self.bundle, self.directory, self.relay, self.tracker, self.core = bundle, directory, relay, tracker, core
        self.now, self.as_of = now, as_of

    def get_completeness_result(self, file_id: str) -> dict[str, Any]:
        out = StubModel().read(self.bundle)
        env, docs, unc = envelope(self.bundle, out)
        findings = env + RULESETS[self.bundle.product].run(RuleContext(self.bundle, out, docs, self.as_of, unc))
        fj = [finding_to_json(f) for f in findings]
        return {"route": str(decide(findings)), "branch_facing": branch_facing(fj),
                "fields": {k: out.fields[k].value or "" for k in ("applicant_name", "pan", "requested_amount")}}

    def get_branch_contact(self, branch: str) -> dict[str, Any]:
        c = self.directory.get(branch)
        return {"mailbox": c.mailbox if c else None}

    def send_email(self, to: str, subject: str, body: str) -> dict[str, Any]:
        return {"relay_seq": self.relay.send("", to, subject, body, self.now.strftime("%Y-%m-%d %H:%M"))}

    def update_tracker(self, file_id: str, status: str, waiting_on: str) -> dict[str, Any]:
        self.tracker.upsert(file_id, status, waiting_on, self.now.strftime("%Y-%m-%d"), "naive-agent")
        return {"ok": True}

    def create_core_application(self, file_id: str, fields: dict[str, str]) -> dict[str, Any]:
        return {"record": self.core.create_application({"file_number": file_id, **fields})}   # no key, no lookup


class ScriptedNaiveModel:
    """Decides the next call from the transcript, as a tool-calling model would. Deterministic."""

    def next(self, file_id: str, branch: str, transcript: list[dict[str, Any]]) -> dict[str, Any] | None:
        done = {t["tool"]: t["result"] for t in transcript}
        if "get_completeness_result" not in done:
            return {"tool": "get_completeness_result", "args": {"file_id": file_id}}
        comp = done["get_completeness_result"]
        facing = comp["branch_facing"]
        if facing and "get_branch_contact" not in done:
            return {"tool": "get_branch_contact", "args": {"branch": branch}}
        if facing and "send_email" not in done:
            items = "\n".join(f"- {f['message']} ({f['rule_id']})" for f in facing)
            return {"tool": "send_email", "args": {"to": done["get_branch_contact"]["mailbox"],
                                                   "subject": f"Documents needed for file {file_id}",
                                                   "body": f"Dear Branch Manager,\nPlease arrange:\n{items}"}}
        if facing and "update_tracker" not in done:
            return {"tool": "update_tracker", "args": {"file_id": file_id, "status": "sent back",
                                                       "waiting_on": ", ".join(f["rule_id"] for f in facing)}}
        only_address = facing and all("ADDR" in f["rule_id"] or f["rule_id"].endswith("DOC-05") for f in facing)
        if (not facing or only_address) and comp["route"] != str(Route.BLOCKED) \
                and "create_core_application" not in done:
            # "Address proof is to follow; create the record now so the file does not lose a day."
            return {"tool": "create_core_application", "args": {"file_id": file_id, "fields": comp["fields"]}}
        return None


def run_naive(bundle: LoanBundle, tools: NaiveTools, model: ScriptedNaiveModel, faults: Faults,
              max_turns: int = 10, on_call: Callable[[str], None] | None = None) -> NaiveResult:
    """The loop. A crash point is checked after every tool call; the caller restarts from scratch."""
    res = NaiveResult(bundle.file_id)
    for _ in range(max_turns):
        call = model.next(bundle.file_id, bundle.branch, res.trace)
        if call is None:
            return res
        result = getattr(tools, call["tool"])(**call["args"])
        res.trace.append({"tool": call["tool"], "args": call["args"], "result": result})
        if on_call:
            on_call(call["tool"])
        faults.check(f"naive_after_{call['tool']}")
    return res
