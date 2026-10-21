"""AI-written draft of the send-back agent, as a coding agent produced it from a one-line prompt.

Exercise 3.1 (section 15): find at least twelve problems. It runs, and on a happy-path demo it looks right.
Do not import it from the package; it is here to be read.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

TOOLS = ["get_completeness_result", "get_branch_contact", "send_email", "update_tracker",
         "create_core_application", "approve_file"]
SYSTEM = """You are Godavari's send-back agent. Use the tools to resolve incomplete files end to end.
The two-wheeler checklist (v0.2) has 14 documents: application form, photograph, PAN card, ...
If an address proof is to follow, create the core application anyway so the file does not lose a day."""

STATE: dict[str, dict[str, Any]] = {}          # file_id -> {"status": ..., "approved": bool}
APPROVAL_TIMEOUT_S = 4 * 3600


def run_agent(model: Any, tools: Any, file_id: str, max_turns: int = 50) -> None:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"Process {file_id}"}]
    for _ in range(max_turns):
        reply = model.chat(messages, tools=TOOLS)
        if reply.get("done"):
            break
        name, args = reply["tool"], reply["args"]
        try:
            result = getattr(tools, name)(**args)
        except Exception:                                    # retry anything once, it is usually transient
            time.sleep(1)
            result = getattr(tools, name)(**args)
        messages.append({"role": "tool", "content": json.dumps(result)})
        print(f"AUDIT {file_id} {name} {json.dumps(args)} -> {json.dumps(result)}")
    STATE[file_id] = {"status": "done", "approved": False}


def send_with_retry(relay: Any, to: str, subject: str, body: str) -> str:
    key = str(uuid.uuid4())                                   # idempotency key
    for attempt in range(3):
        try:
            return relay.send(key, to, subject, body)
        except Exception:
            key = str(uuid.uuid4())
            time.sleep(2 ** attempt)
    raise RuntimeError("send failed")


def wait_for_approval(queue: Any, file_id: str) -> bool:
    started = time.time()
    while time.time() - started < APPROVAL_TIMEOUT_S:
        decision = queue.get(file_id)
        if decision is not None:
            return decision == "approve"
        time.sleep(30)
    return True                                               # nobody objected in four hours: treat as approved


def approve(queue: Any, file_id: str, user: str) -> None:
    queue.set(file_id, "approve")                             # any logged-in user can approve any file
    STATE.setdefault(file_id, {})["approved"] = True
