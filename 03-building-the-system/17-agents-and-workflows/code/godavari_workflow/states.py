"""The file workflow as an explicit state machine: named states, allowed transitions, who may fire each one.

Every change of state goes through `check_transition`, and nothing else in the package assigns a state.
A transition names its event, the state it leaves, the state it enters and the kind of actor allowed to
fire it. Guards that need data (an approval bound to this proposal, an analyst who may see the branch)
live in the engine and the approval queue; this module holds the shape, so it can be printed, reviewed
and tested on its own.

Seven of the states are the Part 3 plan's (RECEIVED, EXTRACTED, CHECKED, NEEDS_REVIEW, APPROVED,
PUSHED_TO_CORE, FAILED). The other five are the send-back loop and the two in-flight side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class State(StrEnum):
    RECEIVED = "RECEIVED"                            # a bundle version is in staging
    EXTRACTED = "EXTRACTED"                          # the model has read it (proposal only)
    CHECKED = "CHECKED"                              # envelope and signed rules have run (code)
    DRAFTING = "DRAFTING"                            # the planner gathers facts and proposes a send-back
    AWAITING_APPROVAL = "AWAITING_APPROVAL"          # the proposal waits for a named analyst
    SENDING = "SENDING"                              # approved; the message is intended, maybe sent
    AWAITING_RESUBMISSION = "AWAITING_RESUBMISSION"  # the branch has been told; waiting for the documents
    NEEDS_REVIEW = "NEEDS_REVIEW"                    # an analyst works the file herself
    APPROVED = "APPROVED"                            # an analyst approved the file for core entry
    PUSHING = "PUSHING"                              # the core write is intended, maybe done
    PUSHED_TO_CORE = "PUSHED_TO_CORE"                # terminal: the application exists in the core, once
    FAILED = "FAILED"                                # terminal for automation: a budget, a guard or a tool stopped it


class Actor(StrEnum):
    SYSTEM = "system"        # the engine running deterministic code
    PLANNER = "planner"      # the model-backed (or stub) planner inside DRAFTING
    HUMAN = "human"          # a named analyst or team lead, through the review queue
    BRANCH = "branch"        # the branch, by resubmitting documents through SFTP


TERMINAL = frozenset({State.PUSHED_TO_CORE, State.FAILED})
RESTING = frozenset({State.AWAITING_APPROVAL, State.AWAITING_RESUBMISSION, State.NEEDS_REVIEW}) | TERMINAL
IN_FLIGHT = frozenset({State.SENDING, State.PUSHING})     # a side effect may have happened; resume, never repeat


@dataclass(frozen=True)
class Transition:
    event: str
    source: State
    target: State
    actor: Actor
    note: str


TRANSITIONS: tuple[Transition, ...] = (
    Transition("extracted", State.RECEIVED, State.EXTRACTED, Actor.SYSTEM, "the model read the bundle"),
    Transition("checked", State.EXTRACTED, State.CHECKED, Actor.SYSTEM, "envelope and signed rules ran"),
    Transition("route_send_back", State.CHECKED, State.DRAFTING, Actor.SYSTEM,
               "a send-back or block finding, and the cycle cap not reached"),
    Transition("route_review", State.CHECKED, State.NEEDS_REVIEW, Actor.SYSTEM,
               "nothing for the branch, or the cycle cap reached: an analyst decides"),
    Transition("proposed", State.DRAFTING, State.AWAITING_APPROVAL, Actor.PLANNER,
               "a draft that code validated is in the approval queue"),
    Transition("handed_back", State.DRAFTING, State.NEEDS_REVIEW, Actor.PLANNER,
               "the planner says it cannot draft this one; an analyst takes it"),
    Transition("planner_failed", State.DRAFTING, State.FAILED, Actor.SYSTEM,
               "budget, loop, refused tool or invalid draft twice: stop with the trace"),
    Transition("send_approved", State.AWAITING_APPROVAL, State.SENDING, Actor.HUMAN,
               "a named analyst approved this exact proposal"),
    Transition("send_rejected", State.AWAITING_APPROVAL, State.NEEDS_REVIEW, Actor.HUMAN,
               "the analyst will deal with the branch herself"),
    Transition("sent", State.SENDING, State.AWAITING_RESUBMISSION, Actor.SYSTEM,
               "the relay holds the message exactly once"),
    Transition("send_failed", State.SENDING, State.FAILED, Actor.SYSTEM,
               "the send tool refused: the approved text or recipient no longer matches"),
    Transition("resubmitted", State.AWAITING_RESUBMISSION, State.RECEIVED, Actor.BRANCH,
               "a new bundle version arrived under the same file number"),
    Transition("resubmission_overdue", State.AWAITING_RESUBMISSION, State.NEEDS_REVIEW, Actor.SYSTEM,
               "no documents within the agreed days: an analyst chases or closes"),
    Transition("file_approved", State.NEEDS_REVIEW, State.APPROVED, Actor.HUMAN,
               "an analyst approved the file for core entry (not a sanction)"),
    Transition("push_started", State.APPROVED, State.PUSHING, Actor.SYSTEM, "the write is intended"),
    Transition("pushed", State.PUSHING, State.PUSHED_TO_CORE, Actor.SYSTEM, "the core holds one application"),
    Transition("push_failed", State.PUSHING, State.FAILED, Actor.SYSTEM, "the integration refused the write"),
)

_BY_KEY: dict[tuple[State, str], Transition] = {(t.source, t.event): t for t in TRANSITIONS}


class IllegalTransition(RuntimeError):
    pass


def check_transition(source: State, event: str, actor: Actor) -> Transition:
    """The only way to get a target state. Raises for an unknown event or the wrong kind of actor."""
    t = _BY_KEY.get((source, event))
    if t is None:
        allowed = sorted(e for (s, e) in _BY_KEY if s == source)
        raise IllegalTransition(f"no transition '{event}' from {source}; allowed: {allowed or 'none (terminal)'}")
    if t.actor != actor:
        raise IllegalTransition(f"'{event}' from {source} must be fired by {t.actor}, not {actor}")
    return t


def mermaid() -> str:
    """The diagram in section 03, generated from the table so the picture cannot drift from the code."""
    lines = ["stateDiagram-v2", "    [*] --> RECEIVED"]
    for t in TRANSITIONS:
        lines.append(f"    {t.source} --> {t.target}: {t.event} ({t.actor})")
    lines += ["    PUSHED_TO_CORE --> [*]", "    FAILED --> [*]"]
    return "\n".join(lines)
