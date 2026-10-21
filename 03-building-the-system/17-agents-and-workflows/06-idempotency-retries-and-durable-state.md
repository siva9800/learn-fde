# 06 · Idempotency, Retries and Durable State: Resume, Never Repeat

> Day 17 · Section 6 of 16 · [Chapter overview](README.md) · Previous: [05 · Human approval as a state](05-human-approval-as-a-state.md) · Next: [07 · Budgets, loops and the audit trail](07-budgets-loops-and-the-audit-trail.md)

---

## 6.1 In plain words

An action is **idempotent** if doing it twice has the same effect as doing it once. Setting the tracker row to "sent
back" is idempotent: set it ten times, there is one row saying "sent back". Sending an email is not: send it twice,
the branch manager has two emails. Creating an application in Godavari's 2009 core is not: Day 6 found that
CreateApplication always creates, and a retry in the test copy made a duplicate (finding A5).

Every multi-step system retries. Networks drop replies, processes are restarted by supervisors, the 02:00 job runs
twice, SFTP delivers the same file twice. So every side effect must be made safe to repeat, and the state of "what has
been done" must survive the process that did it. That is the whole of this section, and it is the reason the Part 3
plan's Short says "Idempotency key: the reason a retry never creates two loans."

> **Analogy (Telugu audience).** UPI (Day 12's picture, continued). When a payment shows "processing" and you press
> pay again, the bank does not debit you twice, because the second request carries the same transaction reference and
> the bank looks it up before acting. At a wedding, it is the serving staff remembering who has eaten (the Part 3
> plan): the same guest at the same table does not get a second plate just because he sat down again.

## 6.2 The idempotency key pattern

Stripe's API reference describes the pattern most engineers learn first (read on 21 October 2026). The client sends
an `Idempotency-Key` header with a create or update request; Stripe "saves the status code and body of the first
request made with a given idempotency key", and "retries with the same key return the saved response, including
`500` errors". Keys "are up to 255 characters long", may be removed "after they're at least 24 hours old", and the
idempotency layer "compares incoming parameters to those of the original request and errors if they're not the same".
It also says to avoid "sensitive data (for example, email addresses or personal identifiers) as idempotency keys".

Four ideas to take from it, all of which apply when the server is not Stripe:

1. **The key identifies the intent, not the attempt.** Every retry of the same intent carries the same key.
2. **The server remembers outcomes by key** for long enough to cover every retry you will make.
3. **Same key, different parameters is an error**, not a silent second action.
4. **Keys are not personal data.**

Godavari's core and mail relay remember nothing by key. So the memory moves to our side, and the lookup moves to the
target's own records: the core's GetApplicationByFileNumber (Day 16) and the relay's message trace by header.

## 6.3 Deriving the key: business intent, not bytes, not a uuid

The key must be computable again, from durable facts, by a process that has forgotten everything else. That rules out
two common choices:

- **A uuid generated per attempt.** Every retry has a new key, so nothing is ever deduplicated. The exercise file
  `ai_draft_workflow.py` does exactly this, and even regenerates the key inside the retry loop.
- **A timestamp or a counter.** A restarted process cannot reproduce it.

And it must identify the **business intent**, which is subtler. The Part 3 plan sketched the core key as "the loan ID
and the bundle hash". That is right for the extraction step: Day 12 keys model calls on the page bytes, so a re-scanned
page is a new unit of work. It is wrong for the create. A resubmitted file has a new bundle hash and is still the same
loan; a key that includes the hash would make the resubmission's create look like a new application, and the core
would hold two. Day 11 and Day 16 key the create on **file number and branch code**, and this chapter keeps that. The
test `test_a_duplicate_upload_is_ignored_and_a_resubmission_is_a_new_cycle` asserts both halves: the new bundle has a
new hash, and the core key is unchanged.

| Side effect | Key | Why that and not something else |
|---|---|---|
| model call (Day 12) | file, page, page sha256, stage, prompt version, schema version, model | the unit of work is "this page, read this way" |
| bundle staging | file id and bundle sha256 | a duplicate SFTP upload of the same bytes is the same arrival |
| send-back email | file id, send-back cycle, hash of the approved text | one email per approved request per cycle; a second cycle is a new request |
| tracker row | file id (an upsert) | the row is a fact about the file, not an event |
| core create | file number and branch code (Day 11) | one application per loan file, whatever bytes arrived |

## 6.4 Intent before, outcome after: the outbox

A key alone is not enough. The process has to know, after a crash, whether it had started the side effect. The pattern
is an **outbox** row written before the call and closed after it:

1. When the analyst approves, one transaction moves the file to SENDING **and** inserts an outbox row (key K,
   INTENDED) **and** marks the approval APPROVED with its final hash **and** appends the audit events. Either all of
   that is on disk or none of it is.
2. The SENDING handler looks K up in the relay's trace. If found, the email went before a crash: close the outbox row
   as DONE ("found in the relay's trace; not sent again") and move on. If not found, send with header K, then close
   the outbox row.
3. Then the tracker upsert, then the transition to AWAITING_RESUBMISSION.

Every crash point has a defined recovery:

| The process dies... | On disk | On resume |
|---|---|---|
| before the approval transaction commits | file in AWAITING_APPROVAL, no outbox row | nothing happened; the analyst's click is lost and she clicks again (the UI shows the item still pending) |
| after the commit, before the send | SENDING, outbox INTENDED, relay has nothing | lookup finds nothing; send |
| after the relay accepted, before the outbox closes | SENDING, outbox INTENDED, relay has the email | lookup finds it; close; **no second email** |
| after the outbox closes, before the tracker write | SENDING, outbox DONE | the send tool finds it again; the tracker upsert runs |
| after the tracker write, before the transition | SENDING, outbox DONE, tracker set | as above; the upsert writes the same row again |

The third row is the one the naive loop gets wrong, and it is the one the demo kills a real process on. Three separate
Python processes, the second dying through `os._exit(17)` the moment after the relay accepts the email, with no
`finally` and no cleanup:

```text
   process 'prepare': exit code 0; prepare: GF-40284 approved by analyst.hyd.07; state SENDING
   process 'send': exit code 17; send: worker starting the send; it will die after the relay accepts the email
   process 'recover': exit code 0; recover: resumed [('GF-40284', 'SENDING')]; state AWAITING_RESUBMISSION; emails in the relay for GF-40284: 1; audit chain intact: True
```

## 6.5 The core write, the same way

APPROVED to PUSHING writes an outbox row with Day 11's key. The PUSHING handler calls Day 11's `push_to_core`, which
looks the file up in the core before creating. A crash after the create and before the outbox closes leaves PUSHING on
disk; the resumed handler calls `push_to_core` again, the lookup finds the record, and the push log says `exists`
(`test_a_crash_after_the_core_create_does_not_create_twice`). From the synthetic week:

```text
Thu 26 Nov 11:30  CRASH at after_core_write_before_record; a new worker opens the same store and recovers
Thu 26 Nov 11:30    resumed 23 unfinished run(s); mid-step: GF-25003 from PUSHING, GF-25079 from SENDING; the other 21 had not started their step
```

The week ended with 43 runs in PUSHED_TO_CORE and 43 records in the sandbox: zero duplicates, counted in the sandbox
itself.

There is one case Day 11's lookup cannot settle and Day 16's writer does: the core **commits after the caller gave up
waiting** (Day 16's "stall then commit"). A lookup that runs immediately finds nothing and a create follows; then the
late commit lands too. Day 16's `SafeCoreWriter` handles it by never retrying an ambiguous write until a quiet period
longer than the core's own transaction timeout has passed. The sandbox here never stalls, so this chapter does not
reproduce it; [Day 16](../16-integrating-with-what-exists/README.md) does, and Day 20 puts its writer behind the
PUSHING state.

## 6.6 Retries with compensation

Retries make an action happen at least once; keys and lookups make it happen at most once; together they give
"effectively once". Some failures are not retryable at all, and then the question is how to undo. That is
**compensation**: a new action that reverses the business effect of an earlier one.

| Side effect | If it turns out to be wrong | Compensation | Who may trigger it |
|---|---|---|---|
| tracker row | the email bounced, or was rejected later | set the row back ("with analyst") | the engine, audited |
| email to the branch | it asked for the wrong document | a **correction** email, drafted, approved and sent through the same states | a person, as a new proposal |
| core application | created for a file that should not have been | nothing we may do; the core-system owner reverses it on his screen | the core-system owner, by his own process |

Two rules follow. **Compensation for an irreversible action is itself an irreversible action**, so it goes through
approval like the original; nothing "unsends" automatically. And **the existence of compensation does not lower the bar
for the original**: an email that needs a correction has already cost the branch manager's trust.

## 6.7 Duplicate detection: count in the target, not in your own logs

The last line of defence is a reconciliation that counts in the systems you wrote to, not in your own counters. The
week's reconciliation, from `simulate.reconcile`:

```text
     approved_send_backs                21
     messages                           21
     duplicate_messages                 0
     messages_to_non_branch_addresses   0
     messages_without_an_approval       0
     core_records                       43
     pushed_runs                        43
     duplicate_core_records             0
```

"Messages" is counted in the relay; "core records" in the sandbox; "messages without an approval" by matching every
relay header to an approved queue item's key. A process can be wrong about what it did. The relay cannot. Day 16's
nightly reconciliation report for the core-system owner is the production version of this table.
