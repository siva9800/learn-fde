# 05 · Human Approval as a State: What Needs It, Who Gives It, and What Happens When Nobody Does

> Day 17 · Section 5 of 16 · [Chapter overview](README.md) · Previous: [04 · Tool design](04-tool-design.md) · Next: [06 · Idempotency, retries and durable state](06-idempotency-retries-and-durable-state.md)

---

## 5.1 A pop-up is not an approval

The usual first "human in the loop" is a dialog: "Send this email? Yes / No". At Godavari it fails four questions the
compliance head will ask. **Who was allowed to click?** Whoever is at the screen, including a Hyderabad analyst who
cannot see Guntur files (finding A1). **What exactly did she approve?** The text on screen at that moment; nothing ties
it to what is sent if the draft is regenerated. **What if nobody clicks?** The process waits in memory until it is
restarted, and then the question is gone. **Where is the record?** In the agent's log, if it logged.

Making approval a **state of the file** answers all four. The file sits in AWAITING_APPROVAL on disk; the queue row holds
the assignee, a hash of exactly what was proposed, a deadline and an escalation level; the decision is a transition only
a human may fire, checked against her authority when she makes it, and committed with its audit event.

## 5.2 What needs approval

Approval is expensive: it is analyst time, and Day 9 priced analyst time at 456 rupees an hour. So approve what is
irreversible or shared, and nothing else.

| Action | Risk class | Approval | Why |
|---|---|---|---|
| reading the findings, the checklist, the contact, the policy | read | none | nothing changes |
| proposing a draft | propose | none (it creates the approval item) | nothing leaves our store |
| emailing the branch manager | write-irreversible | **the assigned analyst or her team lead** | cannot be unsent; it is the branch's first impression of the system |
| updating the tracker row after the send | write-reversible | none of its own; it follows the approved send | the team lead can change it back, and it reflects a fact (the email went) |
| creating the application in the core | write-irreversible | **an analyst's file approval**, after every send-back finding is resolved | decision D07: a human decision on every file; the core cannot delete |
| sanctioning the loan | not in this system | the credit manager (Day 6, step 19) | never automated |

The test for "needs approval" is not "is it risky in general" but **"if this is wrong, can we undo it before anyone
outside our store sees it?"** The tracker row passes (Srinivas can recolour it). The email does not.

## 5.3 Who approves, checked at decision time

`approvals.authority_problems(user, branch, assigned_to)` returns every reason a person may not decide, and an empty
list when she may. Real output from part D of `run_demo.py`, for a Guntur file assigned to Lakshmi:

```text
   proposal SB-GF-40167-c0 assigned to lakshmi, due 2026-11-26 14:00
   svc-kaagaz-workflow: refused: svc-kaagaz-workflow is a service account; only a named analyst or team lead decides; svc-kaagaz-workflow has no group for Guntur; she cannot see the file, so she cannot approve it; the item is assigned to lakshmi; svc-kaagaz-workflow is neither the assignee nor the team lead (vjw.team.lead)
   analyst.hyd.07: refused: analyst.hyd.07 has no group for Guntur; she cannot see the file, so she cannot approve it; the item is assigned to lakshmi; analyst.hyd.07 is neither the assignee nor the team lead (vjw.team.lead)
   bhavani: refused: the item is assigned to lakshmi; bhavani is neither the assignee nor the team lead (vjw.team.lead)
```

Three rules, in that order of importance:

- **Only a person.** The workflow's service account and any planner have no approval right, and no tool takes a
  decision as an argument. There is no code path by which the system approves itself.
- **Only someone who can see the file.** Day 11's `visible_to` with the person's AD groups; the same rule Day 15 uses
  for retrieval. Approving what you cannot see is rubber-stamping.
- **Only the owner, or her lead.** The tracker assigns files (Day 6, step 5); the queue respects it. Bhavani is in the
  right region and still may not approve Lakshmi's item, because two people working one file is how a branch gets two
  different emails.

Refusals are audited (`approval_refused`), because "someone tried to approve a file she could not see" is exactly what
the CISO wants to find in a review.

## 5.4 What she approved: the hash

The queue row stores `proposal_hash`, a SHA-256 over the draft and the recipient. When the analyst approves, the
engine computes `final_hash` over the final text (the draft, or her edit) and stores it with the decision, in the same
transaction that moves the file to SENDING. The send tool recomputes the hash from what it is about to send and
refuses if they differ. The test `test_an_approval_is_bound_to_the_text_it_approved` edits the approved text directly
in the database after the approval; the send refuses, the file goes to FAILED, and nothing reaches the relay.

**Edits are allowed and are checked like drafts.** An analyst who knows the branch manager adds a line. That is what
the human is for. But the edited text goes through `drafts.problems` again before it can be approved, because an
analyst in a hurry can paste a customer's mobile number as easily as a model can. From the synthetic week:

```text
Thu 26 Nov 10:00  lakshmi's edit of SB-GF-25074-c0 refused: the body carries an email address or phone number; recipients and contacts come from the directory
```

She removed the number and approved; the week's counts show one refused edit and three accepted ones.

## 5.5 By when, and what happens when nobody decides

Each item gets a deadline in **working hours**: four, because "tell the branch the same day" is the promise. A
proposal at 16:30 is due at 12:30 the next working day, not at 20:30 the same evening (`clock.add_working_hours`; the
calendar, 09:30 to 17:30 Monday to Friday, is an assumption the team leads must confirm, question SB2 in the design
note). When the deadline passes, `escalate_overdue` moves the item to the region's team lead with a two-hour window,
and after that flags it overdue on the queue. It never approves.

```text
   14:30, nobody decided: tick() moved ['SB-GF-40167-c0']; status PENDING, now assigned to vjw.team.lead (level 1), due 2026-11-26 16:30
   next morning, still undecided: status PENDING, level 2 (flagged overdue; no default approval)
   vjw.team.lead approves: AWAITING_RESUBMISSION; one email: 1
```

"Approve on timeout" is the most common shortcut in approval systems and the most dangerous: it converts every absent
analyst into a yes. The exercise file `code/exercises/ai_draft_workflow.py` has it (`return True  # nobody objected in
four hours`); a coding agent asked for "an approval step with a four-hour timeout" writes it more often than not.

```mermaid
sequenceDiagram
    participant P as Planner (DRAFTING)
    participant Q as Approval queue (disk)
    participant A as Assigned analyst
    participant L as Team lead
    participant E as Engine (SENDING)
    P->>Q: proposal, hash H, due in 4 working hours
    Note over Q: file is AWAITING_APPROVAL
    alt analyst decides in time
        A->>Q: approve (or edit, re-checked; or reject)
    else deadline passes
        Q->>L: escalate: level 1, 2 more hours
        L->>Q: approve or reject
        Note over Q: still nobody: level 2, flagged overdue, never approved by default
    end
    Q->>E: approved, final hash H2, outbox key K
    E->>E: send once (section 06)
```

## 5.6 Rejection, and the analyst's own list

Rejecting is a first-class decision: the file moves to NEEDS_REVIEW and nothing is sent. In the synthetic week Lakshmi
rejected two proposals with the note "branch manager on leave; I will phone the deputy". The workflow does not argue,
retry or redraft. A rejection is information: if one branch's proposals are rejected often, the draft wording or the
recipient is wrong for that branch, and the team lead hears about it from the Day 19 dashboard, not from an escalation.

## 5.7 Approval cost, honestly

About 390 send-backs a month (28 percent of about 1,400 paper and PDF files) at two minutes each is about 13 analyst
hours, about 5,960 rupees at Day 9's 456 rupees an hour, replacing a phone call and a tracker edit each. That is why
every email keeps its approval. If the pilot shows 99 percent approved unedited, that is a conversation for the
compliance head after the RBI inspection, with the data in hand, not a default.
