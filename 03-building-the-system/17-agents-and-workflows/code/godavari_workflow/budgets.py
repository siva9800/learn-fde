"""Budgets and loop detection for one drafting run, and the limits on the workflow around it.

A planner is a loop, and every loop needs a way to stop that does not depend on the model deciding to stop.
Four meters, checked before every call: steps, rupees (read from Day 12's ledger, the number finance sees),
seconds, and repetition (the same tool with the same arguments twice is a loop, not research). Two more
limits sit outside the planner: send-back cycles per file, and transitions per advance.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Budget:
    max_steps: int = 8                 # planner tool calls per drafting run (the stub needs 4 to 6)
    max_inr: float = 2.00              # model spend per drafting run; the file's 12-rupee ceiling is Day 12's
    max_seconds: float = 30.0          # wall time per drafting run
    max_repeats: int = 1               # identical calls allowed: one; the second identical call is a loop
    max_invalid_drafts: int = 2        # a draft code rejects is returned once with the reasons; twice stops it
    max_cycles: int = 2                # send-backs per file before an analyst takes the file over
    max_transitions: int = 25          # per advance-until-rest call: a guard against a workflow-level loop
    resubmission_days: int = 5         # working days the branch has before the file goes to an analyst


def signature(name: str, args: dict) -> str:
    return name + json.dumps(args, sort_keys=True, ensure_ascii=False)


@dataclass
class Meter:
    budget: Budget
    now_s: Callable[[], float]
    spend_inr: Callable[[], float]
    started_s: float = 0.0
    steps: int = 0
    invalid_drafts: int = 0
    seen: Counter[str] = field(default_factory=Counter)

    def __post_init__(self) -> None:
        self.started_s = self.now_s()

    def before_call(self) -> str | None:
        """The reason to stop now, or None. Checked before the planner is asked for its next call."""
        if self.steps >= self.budget.max_steps:
            return f"step budget: {self.steps} of {self.budget.max_steps} tool calls used without a valid proposal"
        spent = self.spend_inr()
        if spent > self.budget.max_inr:
            return f"cost budget: Rs {spent:.2f} spent, the ceiling is Rs {self.budget.max_inr:.2f}"
        elapsed = self.now_s() - self.started_s
        if elapsed > self.budget.max_seconds:
            return f"time budget: {elapsed:.1f} s, the ceiling is {self.budget.max_seconds:.0f} s"
        return None

    def record(self, name: str, args: dict) -> str | None:
        """Count the call; the reason to stop if it repeats an earlier call exactly."""
        self.steps += 1
        sig = signature(name, args)
        self.seen[sig] += 1
        if self.seen[sig] > self.budget.max_repeats:
            return f"loop: {name} called {self.seen[sig]} times with the same arguments"
        return None
