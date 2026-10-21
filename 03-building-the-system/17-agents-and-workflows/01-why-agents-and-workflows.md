# 01 · Why Agents and Workflows: The Email That Went Twice

> Day 17 · Section 1 of 16 · [Chapter overview](README.md) · Next: [02 · Agents versus workflows](02-agents-versus-workflows.md)

---

## 1.1 Thursday, 10:00, the review queue

It is Thursday 26 November 2026, week 5 of the engagement. The prototype reads every new Godavari loan file the
morning after it arrives, checks it against the compliance head's rules (Day 11) and tells you, file by file, what is
missing. File GF-40284, a two-wheeler loan from Dilsukhnagar, has no proof of address. Today an analyst would phone
the branch manager from a personal phone list, list the missing document from memory, and write "waiting on address
proof since 26-11" in red in her tracker (Day 6, steps 10 and 11). The branch would chase the customer, and the
re-scan would arrive in a later 02:00 batch.

The obvious next step is to let the system do the chasing. Someone on the Kaagaz side builds it the way the 2026
framework quick-starts suggest: give a model the tools (read the completeness result, look up the branch contact,
send an email, update the tracker, create the application in the core) and let it work the file. On the demo it is
impressive. The model reads the result, finds the branch mailbox, writes a polite email, updates the tracker, and
then, because the address proof is "to follow", creates the core application so the file does not lose a day.

Now run it the way production runs it. The worker process dies one line after the email leaves, before the loop
records anything. A supervisor restarts it, and the restarted loop has no memory of the first one. This is the real
output of this chapter's naive loop on that file:

```text
naive loop: the process dies at naive_after_send_email; the restart has no memory and runs again
naive loop, second run: get_completeness_result -> get_branch_contact -> send_email -> update_tracker -> create_core_application
naive result: 2 emails to the branch for one send-back; 1 core application(s) for a file with its address proof missing; approvals asked for: 0
```

Two emails to a branch manager for one request, and a record in a 2009 core system that cannot delete it, for a file
the rules say is incomplete, approved by nobody. Notice what did not go wrong: the model. Every call it made was
sensible. A better model makes the duplicate too, because the duplicate comes from the loop having no durable state,
and the unapproved write comes from the tool list being the permission list (Day 12, section 4.2) and the list
containing a write.

This chapter builds the other design, on the same file:

```text
state machine, planner v1: proposal SB-GF-40284-c0 waits for analyst.hyd.07 (due 2026-11-26 14:00); emails so far: 0
approved; the worker dies at after_send_before_record: the relay has 1 email, our outbox says INTENDED
new worker, recover(): resumed [('GF-40284', 'SENDING')]; message_confirmed (found in the relay's trace; not sent again); emails in the relay: 1; state AWAITING_RESUBMISSION
```

Same crash, same point, one email, and nothing written to the core, because an analyst has not approved the file and
the rules still have a finding open.

## 1.2 Why it matters for your career

Applied AI appears in 80 percent or more of the 1,000 FDE postings analysed in 2026, and core engineering in 95 percent
or more (CURRICULUM.md). Agents are where the two meet, and where the system-design round probes hardest, because an
agent in a customer's production touches their systems of record, and trust rests on it never doing the same thing
twice or the wrong thing once (the Part 3 plan). At Godavari the core-system owner's number is "zero duplicate records"
(Day 10), the compliance head's is a human decision on every file (decision D07), and the RBI auditor reads the trail
seven years later (finding A6). None of them will ask which framework you used. All of them will ask what happens when
the process dies in the middle, and who approved this.

## 1.3 What this chapter owns, and what it does not

Day 12 owns tool use at the API level (the loop, schemas, errors as results); Day 11 owns the deterministic-versus-LLM
split; Day 16 owns the SOAP integration and lookup-before-create; Day 41 owns prompt injection and exfiltration through
tools. **This chapter owns agent design**: when a workflow, when an agent, and how to make either safe in a system of
record.

## 1.4 The engagement step

The send-back is the right first workflow because it is frequent, slow and measurable. Day 9's hand count found that
28 percent of files are sent back at least once, and that 6.4 of the median 9.1 days are files waiting in the queue
before an analyst opens them. Day 6 found two ways send-backs go wrong today: the checklist drifts (the compliance head:
"The analysts do not always get the new one") and juniors send back "to be safe" (Bhavani: "I send the file back if she
is busy, because sending back is safe. Maybe a third of mine."). The discovery document promised branch managers "a
missing-document notice the day the file arrives".

The workflow in this chapter does that: it drafts the send-back from the completeness result, looks up the branch
contact and the checklist in force with tools, cites the policy clause where it helps, and proposes the draft. A named
analyst approves before anything leaves. When the branch resubmits, the file is read and checked again and moves on.
It never approves a loan, never changes a signed rule, never writes to the core outside Day 11's idempotent push, and
never sends anything to a customer.

## 1.5 The hard parts, named up front

1. **The word "agent" invites you to give the model control of the sequence.** Most of the value here is a fixed
   sequence with a model inside one step. Section 02 shows how to tell, and the answer for Godavari is "workflow,
   with a small bounded planner in one state".
2. **Crashes happen between two lines of code.** The interesting failures are not "the call failed" but "the call
   succeeded and we never wrote that down". Section 06 is about exactly that gap, and it feels fiddly the first time.
   It is fiddly; it is also the whole job.
3. **Approval is not a pop-up.** A dialog box that says "send? yes / no" has no owner when the analyst is on leave, no
   deadline, no record of what exactly she approved. Section 05 makes approval a state with all four.
4. **Evaluating a path is different from evaluating an answer.** A planner can reach the right draft the wrong way
   (quoting the checklist from memory, then correcting itself). Section 08 shows the trajectory eval catching a change
   whose outcome eval was perfect.
