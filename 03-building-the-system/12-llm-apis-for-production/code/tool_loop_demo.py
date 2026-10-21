"""A bounded, provider-neutral tool loop, with a scripted model so it runs offline.

    python -X utf8 code/tool_loop_demo.py

The use: an analyst asks the operator assistant "where is file KKP-26-00002?". The answer lives in two
legacy places, the Excel tracker and the core system's lookup operation (Day 16 builds the real
wrappers). Tools are read-only here. Writes go through Day 17's state machine and an approval gate, never
through a tool the model can call on its own.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class FileNumber(BaseModel):
    model_config = ConfigDict(extra="forbid")
    file_number: str = Field(pattern=r"^[A-Z]{3}-26-\d{5}$", description="Godavari file number, e.g. KKP-26-00002")


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    args: type[BaseModel]
    run: Callable[[BaseModel], dict]

    def spec(self) -> dict:
        """The definition sent to the model: a name, one sentence on when to use it, a small schema."""
        return {"name": self.name, "description": self.description, "input_schema": self.args.model_json_schema()}


TRACKER = {"KKP-26-00002": {"status": "sent back", "reason": "address proof older than 3 months", "updated": "2026-11-12"}}
CORE = {"KKP-26-00002": {"core_status": "SHELL", "branch": "KKP", "created": "2026-11-10"}}

TOOLS = {t.name: t for t in [
    Tool("get_tracker_status", "Read the credit-ops tracker row for one file: status, reason, last update.",
         FileNumber, lambda a: TRACKER.get(a.file_number, {"status": "not in tracker"})),
    Tool("lookup_core_application", "Read the core lending system's record for one file (read-only lookup).",
         FileNumber, lambda a: CORE.get(a.file_number, {"core_status": "NOT_FOUND"})),
]}


@dataclass
class LoopResult:
    outcome: str
    answer: str | None
    trace: list[str] = field(default_factory=list)


def run_tool_loop(model: Callable[[list[dict], list[dict]], dict], question: str, *, max_turns: int = 4,
                  max_tool_calls: int = 6) -> LoopResult:
    """The whole pattern: ask, run the tools it asks for, send back every result in one message, repeat;
    stop on an answer, on the turn budget, or on the tool-call budget. Errors go back to the model as
    results, marked as errors, so it can recover; they never crash the loop."""
    messages: list[dict] = [{"role": "user", "content": question}]
    specs = [t.spec() for t in TOOLS.values()]
    result = LoopResult("running", None)
    calls = 0
    for turn in range(1, max_turns + 1):
        reply = model(messages, specs)
        if "text" in reply:
            result.outcome, result.answer = "answered", reply["text"]
            result.trace.append(f"turn {turn}: answer")
            return result
        outputs = []
        for call in reply["tool_calls"]:              # parallel calls: run all, return all together
            calls += 1
            if calls > max_tool_calls:
                result.outcome = "stopped: tool-call budget"
                result.trace.append(f"turn {turn}: budget of {max_tool_calls} tool calls reached")
                return result
            tool = TOOLS.get(call["name"])
            if tool is None:
                out = {"is_error": True, "content": f"no tool named {call['name']}; available: {sorted(TOOLS)}"}
            else:
                try:
                    out = {"is_error": False, "content": tool.run(tool.args.model_validate(call["arguments"]))}
                except ValidationError as e:
                    out = {"is_error": True, "content": f"invalid arguments: {e.errors()[0]['msg']}"}
            outputs.append({"tool_call_id": call["id"], **out})
            result.trace.append(f"turn {turn}: {call['name']}({json.dumps(call['arguments'])}) -> "
                                f"{'ERROR ' if out['is_error'] else ''}{json.dumps(out['content'])[:70]}")
        messages += [{"role": "assistant", "tool_calls": reply["tool_calls"]}, {"role": "tool", "results": outputs}]
    result.outcome = "stopped: turn budget"
    result.trace.append(f"stopped after {max_turns} turns without an answer")
    return result


def scripted(turns: list[dict]) -> Callable[[list[dict], list[dict]], dict]:
    """A stand-in model that replays fixed replies. A real adapter maps these shapes to a vendor's."""
    queue = list(turns)
    return lambda messages, specs: queue.pop(0)


SCENARIOS = {
    "normal: two parallel reads, then an answer": [
        {"tool_calls": [{"id": "c1", "name": "get_tracker_status", "arguments": {"file_number": "KKP-26-00002"}},
                        {"id": "c2", "name": "lookup_core_application", "arguments": {"file_number": "KKP-26-00002"}}]},
        {"text": "KKP-26-00002 was sent back on 12 November: the address proof is older than three months. "
                 "The core system holds only the shell record created on 10 November."}],
    "the model reaches for a write it was never given": [
        {"tool_calls": [{"id": "c1", "name": "update_kyc_status", "arguments": {"file_number": "KKP-26-00002", "status": "OK"}}]},
        {"tool_calls": [{"id": "c2", "name": "get_tracker_status", "arguments": {"file_number": "KKP-2600002"}}]},
        {"tool_calls": [{"id": "c3", "name": "get_tracker_status", "arguments": {"file_number": "KKP-26-00002"}}]},
        {"text": "I cannot change KYC status. The tracker shows the file was sent back for an old address proof."}],
    "the model loops on the same read": [
        {"tool_calls": [{"id": f"c{i}{j}", "name": "get_tracker_status", "arguments": {"file_number": "KKP-26-00002"}}
                        for j in range(2)]} for i in range(4)],
}


def main() -> None:
    for title, turns in SCENARIOS.items():
        res = run_tool_loop(scripted(turns), "Where is file KKP-26-00002?")
        print(f"== {title}: {res.outcome}")
        for line in res.trace:
            print("   " + line)
        if res.answer:
            print("   answer: " + res.answer)


if __name__ == "__main__":
    main()
