# 15 · Exercises: From Reading the Machine to Breaking It

> Day 17 · Section 15 of 16 · [Chapter overview](README.md) · Previous: [14 · Interview questions](14-interview-questions.md) · Next: [16 · Further reading](16-further-reading.md)

---

Learning mode: you write the code; use an AI assistant as a tutor ("why does this crash test pass?"), not as the
author. Each exercise names the file to change and how to tell you are done. Run everything in the chapter's virtual
environment from `code/`.

## Level 1 · Read the machine

**1.1 Draw it from memory.** Without looking, draw the twelve states and the transitions out of AWAITING_APPROVAL,
SENDING and AWAITING_RESUBMISSION, with the actor for each. Compare with `data/state-machine.md`. Every arrow you
missed is a question a reviewer will ask you.

**1.2 Predict the output.** Before running it, write down what this prints, then run it:

```python
import sys; sys.path.insert(0, "tests")
from conftest import make_engine, to_approval, NOW
from godavari_workflow.day14 import select
from godavari_workflow.states import Actor
from godavari_workflow.tools import ToolCall, execute
gf = next(g for g in select()[0] if g.file_id == "GF-40284")
eng = make_engine(); row = to_approval(eng, gf)
run = eng.store.get(row["file_id"])
print(run.state, row["assigned_to"], row["due_at"])
print(execute(eng._tool_ctx(run), ToolCall("get_branch_contact", {"branch": "Guntur"}), Actor.PLANNER))
```

*Answer:* `AWAITING_APPROVAL analyst.hyd.07 2026-11-26 14:00`, then
`ToolResult(ok=False, content="get_branch_contact may run only in ['DRAFTING'], not AWAITING_APPROVAL", refused=True)`. The state check comes before the branch
check. If you predicted "this run's file is from Dilsukhnagar", you read `_contact` and missed `execute`'s order.

**1.3 Classify five tools.** For a hypothetical analyst assistant, classify each as read, propose, write-reversible or
write-irreversible, with the side-effect sentence: (a) list today's files waiting on Guntur; (b) reassign a file to
another analyst in the tracker; (c) draft a reply to a branch manager's question; (d) mark a KYC status complete in
the core (Day 16's UpdateKYCStatus); (e) export the week's send-backs to a CSV on the shared drive.
*Answer sketch:* read; write-reversible (the team lead can reassign back, but it changes who works the file: approval
by the team lead); propose; write-irreversible (UpdateKYCStatus appends to the KYC history every time, Day 16);
write-reversible at best and a data-copy question for the CISO (Day 16's "data you may not copy").

## Level 2 · Change it

**2.1 A fifth meter.** Add "three error results in a row" to `budgets.Meter` as a stop reason, and a test with a
planner variant that keeps calling `get_completeness_result` with an invalid file id. Done when the run ends in FAILED
with your reason and the existing 51 tests still pass.

**2.2 The estimate-before-call budget.** Section 07.2 showed a 0.30-rupee ceiling stopping at 0.52. Change the meter
so the model planner's next call is refused when spent plus an estimate of the next call (from the request size and
Day 12's price card) would cross the ceiling. Done when the tight-budget run ends at or under 0.30 on the ledger.

## Level 3 · Break it, then fix it

**3.1 Review this AI-written code and find what is wrong.** `code/exercises/ai_draft_workflow.py` is what a coding
agent produced from "build an agent that resolves incomplete loan files, with retries and a four-hour approval
timeout". It runs. Find at least twelve problems; for each, name the section of this chapter that fixes it.

<details>
<summary>The problems (read after you have your list)</summary>

1. The tool list given to the model includes `send_email`, `create_core_application` and `approve_file`: the model can
   send, write and approve (section 04).
2. `send_email(to, ...)`: the model chooses the recipient; nothing stops a customer address (04.4).
3. The checklist version and its documents are in the system prompt: CHECKLIST_DRIFT, frozen in a string (04, 08).
4. The prompt tells the model to create the core application when the address proof is "to follow": an instruction
   to write an incomplete file (01, decision D07).
5. `max_turns=50` is the only bound: no rupee, time or repetition budget (07).
6. `except Exception: retry` around every tool call, including the send and the create: a lost reply becomes a second
   email or a second application (06).
7. `send_with_retry` makes a new uuid key for each attempt and even regenerates it on failure: the key deduplicates
   nothing (06.3).
8. No lookup before the retry (06.4).
9. `STATE` is a dict in memory, written only at the end: a crash anywhere loses everything, and a restart repeats
   everything (03.7, 06).
10. `wait_for_approval` returns `True` after four hours: approve on timeout (05.5).
11. The four hours are wall-clock, not working hours, and the wait blocks a process for four hours (05.5).
12. `approve(queue, file_id, user)`: any user can approve any file; no branch visibility, no assignment (05.3).
13. The approval is keyed by file id, not bound to the text; whatever the model drafts after approval is sent (05.4).
14. The audit line prints every tool's arguments and full result, including message bodies and anything the
    completeness result carries; and it is a `print`, not an append-only store (07.5).
15. The audit is printed after the call and only if the call returns; a crash between the call and the print leaves no
    record of an action that happened (03.3).
16. There is no state machine at all: nothing says which actions are allowed when (03).

</details>

**3.2 Break idempotency on purpose.** In `tools._send`, comment out the `find_by_key` lookup. Run
`pytest tests/test_idempotency_and_recovery.py`. Which tests fail, and with what counts? Restore it. Then change
`message_key` to include `datetime.now()` and run the same tests. Explain in two sentences why the second break fails
the same tests as the first.

**3.3 Break the approval.** In `approvals.authority_problems`, remove the `visible_to` check. Which test fails? Now
write the sentence you would say to the CISO about what that line protects.

**3.4 Find the bug in the Part plan's key.** Change `engine._start_push` to key the core write on file id plus the
current bundle sha. Write a test in which a file goes through one send-back and resubmission into the core, while the
first bundle's write is in PUSHING when the process crashes. Show that the sandbox ends with two records. Restore Day
11's key and show one.

## Level 4 · Design

**4.1 The correction email.** Design (states, transitions, actors, keys) and implement the correction flow of section
06.6: after a send, an analyst proposes a correction; it is approved and sent through the same states with its own
key; the original is never "unsent". Write the crash test.

**4.2 Day 16's writer behind PUSHING.** Read Day 16's `SafeCoreWriter`. Write the adapter that lets PUSHING call it
instead of Day 11's sandbox push, and a test of Day 16's "stall then commit" case through the state machine. What new
state, if any, does an ambiguous write need?
