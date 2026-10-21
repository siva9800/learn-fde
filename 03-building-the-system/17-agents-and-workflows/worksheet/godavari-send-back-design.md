# Godavari send-back workflow · design note for sign-off

> Engagement folder · Day 17 · Draft 0.1, Thursday 26 November 2026 (engagement week 5) · Author: the Kaagaz AI FDE ·
> For: the compliance head (the rules and the audit trail), Srinivas and the Vijayawada team lead (approvals and
> deadlines), the CISO (what the workflow may touch), the core-system owner (writes). Prototype only: synthetic files,
> prototype mode, nothing on Godavari's network. Everything here is synthetic.

## 1. What it does, in one paragraph

When the signed rules find a file incomplete, the workflow drafts the send-back request that an analyst writes by
phone or email today (Day 6, steps 10 and 11), cites each rule that fired and the checklist version in force, and puts
the draft in the assigned analyst's queue. Nothing leaves until a named analyst approves it. Once approved, it is
emailed once to the branch manager's role mailbox, the tracker row is set to "sent back, waiting on ...", and the file
waits for the branch's re-scan under the same file number. When the documents arrive, the file is read and checked
again. A file with nothing for the branch goes to the analyst, who approves it for core entry; only then is it written
to the core, once, through Day 11's idempotent push.

## 2. What it never does

| Never | How that is enforced (not promised) |
|---|---|
| approve or reject a loan | no tool and no transition does it; APPROVED means "approved for core entry by a named analyst", and the sanction stays with the credit manager (Day 6, step 19) |
| change a signed rule | the rules are Day 11's code, imported; every run checks the sign-off fingerprint and refuses if the code changed; pilot mode refuses unsigned rules |
| write to the core without the idempotent integration | the only write is Day 11's `push_to_core` (approval check, route check, key from file number and branch code, lookup before create), from one state, after a file approval |
| contact a customer | the branch directory holds role mailboxes of branch managers only; the model never sees or chooses an address; the send tool takes an approval id and nothing else |
| send anything without approval | the send runs only in SENDING, which only a person's approval enters; the approval is bound to a hash of the exact text and recipient |
| ask for more than the rules require | code rejects a draft with an item for a rule that did not fire (the "to be safe" send-back, Day 6 SENDBACK_CAUTION) |
| quote an old checklist | the draft must carry the version string the checklist tool returned from the signed code (Day 6 CHECKLIST_DRIFT) |

## 3. The states

RECEIVED, EXTRACTED, CHECKED, DRAFTING, AWAITING_APPROVAL, SENDING, AWAITING_RESUBMISSION, NEEDS_REVIEW, APPROVED,
PUSHING, PUSHED_TO_CORE, FAILED. The diagram and the full transition table are generated from the code:
[`data/state-machine.md`](../data/state-machine.md). Every state change and its audit event are committed in one
transaction.

## 4. Approvals: who, by when, what if nobody

| Question | Proposed answer (for the team leads to confirm) |
|---|---|
| who approves a send-back | the analyst the file is assigned to in the tracker, or her region's team lead; she must hold the branch's AD group (Day 6, finding A1) |
| who may not | the workflow's service account; any planner; an analyst from the other region; a same-region analyst the file is not assigned to |
| deadline | 4 working hours from the proposal (working day assumed 09:30 to 17:30, Monday to Friday: **confirm**) |
| when the deadline passes | the item moves to the team lead with a 2-hour window; after that it is flagged overdue on the queue; **it is never approved by default** |
| edits | allowed; the edited text passes the same checks as a draft before it can be approved |
| rejection | the file goes to the analyst's own list; nothing is sent |
| branch does not resubmit | after 5 working days the file goes to the analyst, who chases or closes it (**confirm the number**) |
| repeated send-backs | at most 2 per file; a third gap goes to the analyst, who phones the branch |

## 5. What is recorded, for seven years (finding A6)

Every proposal (by hash), every tool call (arguments, with any message body recorded by length and hash, not text),
every approval, refusal, escalation and edit, every email sent (with its key), every core write, every crash recovery.
The log is append-only and hash-chained; `verify_chain()` finds the first edited or deleted event. The approved text
itself is kept in the approval queue, inside Godavari's boundary. No PAN, Aadhaar number or mobile number appears in
the audit log (tested).

## 6. Budgets

A drafting run may make at most 8 tool calls, spend at most Rs 2.00 on model calls (measured on Day 12's ledger) and
take at most 30 seconds; the same call with the same arguments twice is a loop. Any of these stops the run in FAILED
with its trace, on the analyst's list. The stub planner needs 4 to 6 calls and Rs 0.

## 7. Open questions for sign-off

| # | Question | Owner |
|---|---|---|
| SB1 | Is four working hours the right approval deadline, given "tell the branch the same day"? | Srinivas, the Vijayawada team lead |
| SB2 | Do credit-ops work Saturdays? The calendar in the code assumes not. | the team leads |
| SB3 | Is the branch manager's role mailbox the right recipient, or the branch operations desk? | the COO's office |
| SB4 | Does the compliance head want the send-back text itself reviewed as a template before the pilot? | the compliance head |
| SB5 | Which mail relay, and can it be searched by header (the message trace lookup-before-send needs)? | the CISO, corporate IT |
| SB6 | Retention of the approval queue's text: the same seven years as the decision trail? | the compliance head |
