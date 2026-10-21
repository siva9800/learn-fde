# 13 · Mistakes and Debugging: Symptom, Cause, Fix

> Day 17 · Section 13 of 16 · [Chapter overview](README.md) · Previous: [12 · Build it with AI, and how you know it is right](12-build-with-ai-and-verification.md) · Next: [14 · Interview questions](14-interview-questions.md)

---

## 13.1 Duplicates and missing effects

| Symptom | Likely cause | Fix |
|---|---|---|
| a branch manager received the same request twice | the send was retried after a crash or a lost reply without a lookup; or the key differs between attempts (uuid, timestamp) | content-derived key; outbox; lookup in the relay's trace before any send; the crash test |
| two applications in the core for one file | the create key included the bundle hash, so a resubmission looked new; or a retry without lookup | key on file number and branch code (Day 11); Day 16's lookup and quiet period |
| the email went but the tracker still says "with analyst" | crash after the send and before the tracker write, and the resumed run was never started | `recover()` on startup, always; the tracker upsert runs again on resume |
| a run stuck in SENDING for hours | the worker died and nothing called `recover()`; or the relay is down and every attempt fails | start-up recovery; an alarm on in-flight age; the send's error path |
| "sent" in our store, nothing in the relay | the outbox was closed before the relay confirmed; or the relay accepted then dropped | close the outbox only on the relay's id; reconcile daily by counting in the relay |

## 13.2 Approvals

| Symptom | Likely cause | Fix |
|---|---|---|
| a send-back went out that nobody approved | a default-approve on timeout; or a code path that calls the send tool outside SENDING | remove the default; the registry's state check; a test that the send is refused outside SENDING |
| the email differs from what the analyst saw | the draft was regenerated after approval; the approval was bound to the file | bind to the hash; recompute at send |
| a Hyderabad analyst approved a Guntur file | the authority check looked at role, not branch groups | `visible_to` at decision time, with groups resolved now, not at login |
| approvals pile up at one analyst | assignment from a stale tracker, or she is on leave | escalation works but slowly: shorten the deadline for that queue, or reassign at the team lead's request |
| analysts approve everything in two seconds | the drafts are always right, or nobody reads them | sample a few approved drafts a week against the pages; watch the edit rate (section 10.5) |

## 13.3 The planner

| Symptom | Likely cause | Fix |
|---|---|---|
| runs fail with "loop: get_branch_contact called 2 times" | the tool's result did not answer what the prompt asked for, so the model asks again | read the trace; fix the tool's result or the prompt; never raise the repeat limit to make it pass |
| runs fail on "step budget" after a model upgrade | the new model is more thorough and reads every tool | the trajectory eval shows the extra steps; decide whether they add anything; tighten the tool descriptions |
| drafts rejected for "items for rules that did not fire" | the prompt says "be thorough" or "to be safe", or examples include extra items | remove it; the rules decide what is required; the code check stays |
| drafts rejected for the checklist version | the version is in the prompt or a few-shot example | remove it; the planner must call the checklist tool; v2 in section 08 is this bug |
| cost per draft doubled | the history grew (a long tool result), or the tier changed | small tool results; Day 12's ledger by stage; the rupee meter catches the ceiling, the dashboard catches the trend |
| "refused: send_branch_message" in the trace | the prompt says "resolve the file end to end", or a few-shot example shows a send | the run stopped correctly; fix the prompt and rerun the trajectory eval |

## 13.4 A routine for "it did something twice"

1. **Count in the target.** How many emails with this file's subject in the relay? How many applications for this file
   number in the core? Your own logs come second.
2. **Find the keys.** For each copy, read its key (the relay's `X-Kaagaz-Key` header, the core's external reference).
   Same key twice means the lookup did not run or did not see the first; different keys means the key derivation is
   wrong.
3. **Read the outbox row** for the key: INTENDED or DONE, and when.
4. **Read the audit log for the file** in sequence: where is `resumed`? Which events are between the two copies?
5. **Reproduce it as a crash test** at the point you found, assert one effect, then fix.
6. **Reconcile the batch**, not just the file: if one file duplicated, the same window may have caught others.
