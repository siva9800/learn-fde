# 12 · Build It With AI, and How You Know It Is Right

> Day 17 · Section 12 of 16 · [Chapter overview](README.md) · Previous: [11 · Project: the send-back workflow](11-project-the-send-back-workflow.md) · Next: [13 · Mistakes and debugging](13-mistakes-and-debugging.md)

---

## 12.1 Build it with AI

A coding agent writes most of this chapter's code well, fast: the SQLite store, the Pydantic argument models, the
transition table, the test scaffolding. It also writes, by default, the naive loop of section 01, because that is what
most agent tutorials on the internet are. The work is in the context you give it and in what you check afterwards.

**Context to give it** (paste or point at, in this order):

1. The state table from section 03 (or `data/state-machine.md`), with the rule "nothing assigns a state except
   `check_transition`".
2. The tool inventory with risk classes (`data/tool-inventory.md`) and the rule "the planner sees read and propose
   only; write tools run in one state each, against an approval".
3. The four never-rules from the design note: never approve a loan, never change a signed rule, never write to the
   core outside Day 11's `push_to_core`, never contact a customer.
4. The paths of the earlier chapters' packages and the instruction "import by path, never copy" (Days 11, 12, 14, 15).
5. The crash points you want tests for, named.
6. The target systems' real semantics: "the mail relay does not deduplicate and can be searched by header; the core's
   CreateApplication always creates".

**A strong prompt:**

> Build the send-back workflow for a lender's loan files as a Python package. It is a state machine, not an agent
> loop: here are the states, transitions and actors [paste]. Persist every run in SQLite; every state change and its
> audit event in one transaction; the audit table append-only and hash-chained. Inside the DRAFTING state only, a
> planner may call read and propose tools from this registry [paste]; it may not call write tools, and an attempt
> must stop the run. The send tool takes only an approval id; the recipient comes from a branch directory, never from
> the planner. Approvals are queue rows bound to a SHA-256 of the exact text and recipient, assigned to a named
> analyst, with a four-working-hour deadline that escalates to the team lead and never approves by default. Every
> irreversible side effect has a key derived from business intent (give me your derivation for each and why), an
> outbox row written before the call and closed after it, and a lookup in the target system before any repeat.
> Budgets per drafting run: 8 steps, 2 rupees read from this ledger [Day 12 path], 30 seconds, and a stop on an
> identical repeated call. Import Day 11's rules and core push by path from [path]; do not copy them. Write pytest
> tests that crash the process between the relay accepting an email and our record of it, and after the core create,
> and assert exactly one email and one record after resume. Do not add any tool I have not listed.

**What it typically gets right:** the SQLite schema and transactions; Pydantic models with `extra="forbid"`; the
transition table and a `check_transition` function; mocking the relay; the shape of a pytest suite; the hash chain
(it knows the pattern); Mermaid from a table.

**What it typically gets wrong for this concept, and how each shows:**

| Mistake | How it shows | Fix |
|---|---|---|
| **a uuid per attempt as the idempotency key** | `key = str(uuid.uuid4())` inside the retry loop (the exercise file does it) | derive from durable business facts; test that two processes compute the same key |
| **retry on any exception** | `except Exception: retry` around the send | classify: not sent, ambiguous, refused; an ambiguous send is looked up, never blindly retried |
| **state saved after the side effect** | the run row is updated once the email "succeeded" | intent before (outbox), outcome after; the crash test between them |
| **approval on timeout** | `return True  # nobody objected` | escalate, flag, never approve; a test with two ticks |
| **approval bound to the file, not the text** | `approve(file_id)`; the draft regenerated afterwards | bind to a hash of text and recipient; refuse at send if it differs |
| **any logged-in user can approve** | no authority check, or a role check without branch visibility | `visible_to` with her groups, plus assignment, at decision time |
| **the model picks the recipient** | `send_email(to, ...)` in the planner's tools | the send tool takes an approval id only |
| **the checklist in the prompt** | "the checklist (v0.2) has 14 documents..." | a tool that reads the signed code; the draft must carry its version string |
| **full message bodies and tool results in the audit log** | `print(f"AUDIT ... {json.dumps(result)}")` | record bodies by hash and length; run `pii_hits` over the log in a test |
| **tests that cannot fail** | the crash is simulated with `except Exception` that the code under test also catches | crash with a `BaseException` subclass and with `os._exit` in a subprocess |

The two to watch hardest are the first and the fourth. Both produce code that passes a happy-path demo and fails
exactly once in production, on the day it matters, and both are invisible in a code review that does not ask "what
happens if this runs twice?" and "what happens if nobody answers?".

**A second, review-mode prompt** (after the agent's first draft):

> You are reviewing this workflow code for a regulated lender. For each of these questions, quote the line that
> answers it or say it is not answered: (1) If the process dies one line after each external call, what happens on
> restart, call by call? (2) What exactly is an approval bound to, and where is that checked? (3) What happens when an
> approval is never decided? (4) Which tools can the model call, and which of them change anything outside our
> database? (5) What is each side effect's key, and could two attempts compute different keys? (6) What bounds the
> planner's loop, in steps, money and time? Do not suggest new features; find what is missing.

## 12.2 How do you know it's right?

Whether you wrote the workflow or an agent did, the checks are the same, and most are already tests.

1. **Count in the target, not in your logs.** Run the week (or a pilot day) and reconcile: emails in the relay equal
   approved send-backs; core records equal pushed runs; zero messages without a matching approval key; zero recipients
   outside the branch directory. If your own counters agree but the relay disagrees, the relay is right.
2. **Kill it for real.** A `SimulatedCrash` exception proves the logic; `os._exit` in a subprocess proves there is no
   `finally` block quietly saving you. Kill it at every point between "done there" and "recorded here", for every
   side effect.
3. **Read the state table as the compliance head would.** Who fires each transition into APPROVED and SENDING? If any
   answer is not "a human", stop.
4. **Print the planner's tool list.** It must be read and propose only. Then try each write tool as the planner and
   check it is refused and audited.
5. **Try to approve as the wrong person.** The service account, an analyst who cannot see the branch, a same-region
   analyst who is not assigned. All three must be refused, and the refusals must be in the audit log.
6. **Let the deadline pass.** Twice. The item must be with the team lead and then flagged, and still pending.
7. **Run the trajectory eval against the previous version.** Every check that passed must still pass on every file;
   decision precision must not fall. An outcome-only eval is not enough (section 08's v2).
8. **Search the audit log for identifiers.** `pii_hits` over the exported JSONL must return nothing.
9. **Verify the chain, then break it.** `verify_chain()` must be true after a run and false, at the right sequence
   number, after you edit one row.
10. **Check the never-list against the code, not the prompt.** For each of the four never-rules, find the line that
    makes it impossible. A sentence in a system prompt does not count.

**Review checklist:** use `worksheet/agent-review-checklist.md` on every pull request; it is the ten checks above
as yes-or-no questions, with the place in the code to look.
