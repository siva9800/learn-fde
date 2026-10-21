"""A worker process, so a crash can be a real one: `os._exit` in the middle of a send, no cleanup, no finally.

    python -m godavari_workflow.worker prepare STATE_DIR GF-40104   # receive, propose, analyst approves
    python -m godavari_workflow.worker send    STATE_DIR GF-40104   # dies right after the relay accepted the email
    python -m godavari_workflow.worker recover STATE_DIR GF-40104   # a new process: resume, then count

run_demo.py runs the three in sequence as separate processes (part B). Everything is on disk in STATE_DIR.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from .clock import BusinessClock
from .day14 import select
from .engine import Engine, Systems
from .planner import StubPlanner
from .store import Store
from .systems import Faults

NOW = datetime(2026, 11, 26, 10, 0)


def main(argv: list[str]) -> int:
    step, folder, file_id = argv[0], Path(argv[1]), argv[2]
    faults = Faults({"after_send_before_record": 1}, hard_exit=True) if step == "send" else Faults()
    eng = Engine(Store(folder / "workflow.sqlite"), Systems.open(folder), BusinessClock(NOW), StubPlanner(),
                 faults=faults)
    if step == "prepare":
        bundle = next(g for g in select()[0] if g.file_id == file_id).build()[0]
        eng.receive(bundle)
        eng.run_until_rest(file_id)
        run = eng.store.get(file_id)
        assert run is not None and run.data.get("approval_id"), f"{file_id} produced no proposal"
        row = eng.store.approval(run.data["approval_id"])
        assert row is not None
        eng.decide_send(row["id"], row["assigned_to"], "approve")
        print(f"prepare: {file_id} approved by {row['assigned_to']}; state {eng.store.get(file_id).state}")  # type: ignore[union-attr]
    elif step == "send":
        print("send: worker starting the send; it will die after the relay accepts the email", flush=True)
        eng.run_until_rest(file_id)
        print("send: this line is never printed")
    elif step == "recover":
        resumed = eng.recover()
        run = eng.store.get(file_id)
        assert run is not None
        print(f"recover: resumed {resumed}; state {run.state}; emails in the relay for {file_id}: "
              f"{eng.sys.relay.count_for(file_id)}; audit chain intact: {eng.store.verify_chain()[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
