# Review checklist for any agent or workflow pull request

> Day 17 · Use on every change to the workflow, the planner, the tools or the prompt, whether a person or a coding agent
> wrote it. Each line is a question with a yes or no answer and a place in the code to check.

## Shape

- [ ] The change keeps every state change inside `check_transition`; nothing assigns a state directly.
- [ ] A new state has an entry transition, an exit transition (or is terminal), and an actor for each.
- [ ] No transition into APPROVED or SENDING is fired by anything but a human.
- [ ] The diagram in `data/state-machine.md` was regenerated, not hand-edited.

## Tools

- [ ] Each new tool has a risk class, a side-effect sentence and the states it may run in.
- [ ] Write tools are not in `planner_specs()`.
- [ ] Arguments are typed and strict (`extra="forbid"`); the tool cannot act on another run's file.
- [ ] No tool lets the caller choose a recipient, a customer, or free text that is sent unreviewed.
- [ ] Tool results returned to the planner are small and contain no addresses.

## Side effects

- [ ] Every irreversible write has a key derived from business intent (not a timestamp, not a uuid per attempt).
- [ ] The intent is recorded before the call, and the outcome after it, in our store.
- [ ] A retry or a resume looks the effect up in the target system before repeating it.
- [ ] A crash test exists for the new side effect: kill between "done there" and "recorded here", resume, count.

## Approvals

- [ ] The approval is bound to a hash of exactly what will be done.
- [ ] Authority is checked at decision time: role, branch visibility, assignment.
- [ ] Timeouts escalate. Nothing approves by default.
- [ ] An edit passes the same checks as the draft.

## Budgets and loops

- [ ] Steps, rupees (from the ledger) and seconds are bounded per run; identical repeated calls stop the run.
- [ ] Hitting a budget ends in FAILED with the trace, visible to an analyst.
- [ ] Send-back cycles per file are capped.

## Evidence

- [ ] The trajectory eval ran on the golden set; every check that passed before still passes.
- [ ] Decisions against the experts did not get worse (precision and recall with intervals).
- [ ] The audit chain verifies after the test run; `pii_hits` finds nothing in the audit log.
- [ ] Pilot mode still refuses unsigned rules.
