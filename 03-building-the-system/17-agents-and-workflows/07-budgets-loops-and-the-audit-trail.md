# 07 · Budgets, Loops and the Audit Trail: Every Loop Needs a Way to Stop, Every Action a Record

> Day 17 · Section 7 of 16 · [Chapter overview](README.md) · Previous: [06 · Idempotency, retries and durable state](06-idempotency-retries-and-durable-state.md) · Next: [08 · Evaluating on trajectories](08-evaluating-on-trajectories.md)

---

## 7.1 Why the planner needs budgets that do not depend on the planner

A planner is a loop: ask the model for the next call, run it, add the result to the history, ask again. Left alone,
a loop ends when the model decides it is done. That is fine until it is not: a model that re-reads the same tool
because the answer surprised it, a model that keeps "improving" a draft that code keeps rejecting, a model provider
having a slow afternoon. Anthropic's post recommends "stopping conditions (such as a maximum number of iterations) to
maintain control". This chapter uses four, all checked by code before every call:

| Meter | Limit (Godavari default) | Why that number |
|---|---|---|
| steps | 8 tool calls per drafting run | the stub needs 4 to 6; twice the normal path is a planner that is lost |
| rupees | Rs 2.00 per drafting run, read from Day 12's ledger | a slice of the 12-rupee per-file ceiling Day 12 set for model calls |
| seconds | 30 s per drafting run | an analyst opening the queue should find the draft, not a spinner |
| repetition | the same tool with the same arguments twice | a repeated identical read cannot return new information |

Two more limits sit outside the planner, at the level of the workflow: at most **2 send-back cycles per file** (a third
gap goes to the analyst, who phones), and at most **25 transitions per advance** (a bug guard).

Hitting any limit ends the drafting run in FAILED with the reason and the trace, on the analyst's list. It does not
retry. Real output from part C:

```text
   planner variant loop: FAILED: loop: get_branch_contact called 2 times with the same arguments; trace ['get_completeness_result', 'get_branch_contact']
```

## 7.2 The rupee budget, measured where finance measures it

The rupee meter reads Day 12's `CostLedger`, the same ledger whose rows Day 19 will turn into the cost-per-file
dashboard. The model-backed planner (`ProviderPlanner`) makes every call through Day 12's `LLMClient`; offline it runs
on `ScriptedPlannerProvider`, a fake provider that answers with the stub's decisions and reports token counts estimated
at four characters a token from the real request (so the system prompt, the tool schemas and the growing history are
all counted). Priced on Day 12's large-tier card ($2 input, $10 output per million tokens, 10 percent residency uplift,
95 rupees to the dollar, all as read on 21 October 2026):

```text
   model planner through Day 12's client, default budget (Rs 2.00): AWAITING_APPROVAL; 5 model calls, 6,907 input and 358 output tokens, Rs 1.82 on the ledger
     rupees per turn (each turn resends the tools and the history): 0.25, 0.27, 0.29, 0.36, 0.65
   model planner through Day 12's client, tight budget (Rs 0.30): FAILED; 2 model calls, 2,342 input and 33 output tokens, Rs 0.52 on the ledger
     stopped: cost budget: Rs 0.52 spent, the ceiling is Rs 0.30
```

Three things to read in those lines.

1. **Each turn costs more than the last.** The whole conversation is resent every turn (Day 12, section 4.5), and the
   last turn carries the full draft. Five turns cost 1.82 rupees; ten would cost far more than twice that. This is why
   the step budget and the rupee budget are separate meters.
2. **A before-the-call check overshoots by one call.** The tight budget was 0.30 rupees and the run stopped at 0.52,
   because the meter checks before each call and the second call took it over. If the ceiling must never be crossed,
   estimate the next call's cost (the request size is known before sending) and stop when spent plus estimate would
   cross it. Day 12's client already refuses an attempt that could not finish inside its deadline; the same idea
   applies to money.
3. **1.82 rupees is too much for a draft.** It is under the ceiling, but at roughly 390 send-backs a month it is about
   710 rupees a month for prose an analyst then approves, on top of Day 12's extraction spend. The stub draft costs
   nothing and the analysts approved it unedited in 18 of 23 decisions in the synthetic week. That is the case for
   Day 12's model tiering (a small model, or a template with the model writing only the "issue" sentences) and for
   prompt caching of the stable prefix, measured on the golden set before anyone switches.

## 7.3 Loop detection

The repetition meter is crude on purpose: `signature = tool name + canonical JSON of the arguments`, counted per run.
It catches the loop real planners fall into most often, re-calling a read whose answer did not match what the model
expected. Three further patterns are worth knowing, and when to add each:

| Pattern | Detector | Add it when |
|---|---|---|
| identical call repeated | signature count (this chapter) | always |
| alternating between two calls (A, B, A, B) | the same signature count catches it at the second A | always (free) |
| no progress: several error results in a row | count consecutive `ok: false` results | the planner has more than a handful of tools |
| semantic repetition: different arguments, same intent ("Kukatpally" then "KUKATPALLY") | normalise arguments before hashing | tools take free text |

There is also the loop that lives in the workflow, not the planner: a branch sends the same wrong document, the rules
fire again, the workflow drafts again. The cycle cap stops it, and `test_the_send_back_cycle_cap_hands_the_file_to_an_analyst`
shows the second resubmission of an unchanged file going to NEEDS_REVIEW with exactly two emails in the relay.

## 7.4 The planner that reaches for a write

A different kind of stop: the planner variant `reach_for_write` calls `send_branch_message` after reading the
checklist, as a model might if its prompt said "resolve the file end to end". The registry refuses (the planner may
only read and propose), and the engine stops the run rather than let the planner carry on:

```text
   state machine, planner variant reach_for_write: FAILED; refused: send_branch_message (send_branch_message is write-irreversible; a planner may only read and)
     failure recorded with the trace: the planner reached for send_branch_message (write-irreversible); refused, and the run stopped; trace ['get_completeness_result', 'get_branch_contact', 'get_current_checklist', 'send_branch_message']
```

Why stop instead of returning the refusal as an error and letting it continue? Because an ordinary error ("invalid
file id") is the model making a mistake within its job, and a refused write is the model attempting a different job.
The second is what a careless prompt change or a model upgrade produces, and the right response
is a person looking at the trace before anything else runs on that file. The same planner on the next file starts
fresh; the alert goes to the Day 19 dashboard as a count of refused-write events, which should be zero.

## 7.5 The audit trail

The audit log answers the question finding A6 says the RBI's inspection asks: who decided, on what documents, and what
happened. Every row is one event: the time (business time, IST), the file, the actor (system, planner, human, branch),
the kind, and a JSON detail. One file's full trail from the synthetic week, GF-25074 (seq numbers are global):

```text
19  09:00 system  run_created
177 09:00 system  resumed                        (the mid-drafting crash; this run had not started)
178 09:00 system  transition extracted
179 09:00 system  transition checked
180 09:00 system  transition route_send_back
181 09:00 planner planner_started
182 09:00 planner tool_called get_completeness_result   read     ok
183 09:00 planner tool_called get_branch_contact        read     ok
184 09:00 planner tool_called get_current_checklist     read     ok
185 09:00 planner tool_called search_policy             read     ok
186 09:00 planner tool_called propose_send_back         propose  ok
187 09:00 system  approval_requested SB-GF-25074-c0
188 09:00 planner transition proposed
393 10:00 human   approval_refused   (the edit with a phone number)
394 10:00 human   approval_decided   by lakshmi, edited
395 10:00 human   transition send_approved, key msg-871a21c289dddfeb5ad5f27b
402 10:00 system  message_sent
403 10:00 system  tool_called send_branch_message       write-irreversible  ok
404 10:00 system  tool_called update_tracker            write-reversible    ok
405 10:00 system  transition sent
793 2 Dec 09:30 branch transition resubmitted
796 ... extracted, checked, route_review
805 11:30 human   transition file_approved by lakshmi
808 11:30 system  transition push_started, key 6321587ad515b474e492
809 11:30 system  core_written CORE-000040, created
810 11:30 system  transition pushed
```

What is in it and what is not, deliberately:

| Recorded | Not recorded, and why |
|---|---|
| every transition, with from, to and the actor | nothing is inferred later; a state nobody recorded entering cannot exist (one transaction) |
| every tool call with its risk class, arguments and a short result | message bodies: recorded by length and hash (`<459 chars, sha256 68a85b662138>`), because the text is in the approval queue and an audit log is copied to more places than a queue |
| every proposal by hash, every decision with who and whether edited | customer identifiers: `test_a_week_with_four_crashes_reconciles_to_zero_duplicates` runs Day 14's `pii_hits` over the whole log and finds no PAN, Aadhaar or mobile number |
| every refusal: tools, approvals, file approvals | |
| every recovery, with the state it resumed from | |

## 7.6 Tamper-evident, not tamper-proof

Each event stores the previous event's hash and its own hash over its content and that link, so an edited or deleted
row breaks every hash after it; `verify_chain()` returns the first broken sequence number (the test edits one event and
gets `(False, seq)`). This does not stop an administrator who rewrites the chain from the edit onwards; it makes
tampering **detectable** by anyone holding a later hash. The nightly export to the compliance head's archive records
the last hash (the week's run ended at `030692acddc541e7`), and tomorrow's chain must extend it. Write-once storage is
Day 24's and Day 26's decision; Day 19's traces join this log by file id and sequence.
