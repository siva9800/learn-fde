# 01 · Why Production LLM Calls: The Demo Called the Model Once

> Day 12 · Section 1 of 14 · [Chapter overview](README.md) · Next: [02 · The call as a dependency](02-the-call-as-a-dependency.md)

---

## 1.1 One call versus forty thousand

In the week-one demo, a Kaagaz engineer drags a scanned Godavari application into a notebook, sends it
to a model with a long prompt, and prints a tidy JSON block on the screen. The COO nods. Everyone in the
room has now seen the model read a loan file.

Now count what production asks for. About 1,400 paper and PDF files a month arrive in the 02:00 SFTP
drop, each 8 to 40 pages. This chapter's pipeline classifies every page on a small model and extracts
fields from the pages that carry them on a large one. That is about 30 model calls per file and roughly
40,000 a month. At that volume, things that never happen in a demo happen every night:

- the provider answers 429 because forty calls arrived in the same second;
- one call in a hundred hangs for a minute and then times out, and the provider bills it anyway;
- the model returns valid JSON with the dealer's ex-showroom price in the "requested amount" field;
- the 02:00 job is restarted at 02:20 by the scheduler, and every page is sent again;
- the provider has a three-minute overload, and a naive client retries 1,500 calls straight into it;
- a vendor changes a price, a model or a parameter, and the code that called its SDK in forty places
  needs forty changes.

None of these is about prompting. They are about treating the model as what it is in production: a
paid, rate-limited, occasionally wrong network dependency, running in the customer's account on the
customer's budget.

## 1.2 Why it matters for your career

Applied AI appears in 80 percent or more of the 1,000 FDE postings analysed in 2026, and core
engineering in 95 percent or more (CURRICULUM.md, figures as published). This chapter sits exactly
where the two meet. Interviewers in the practical coding and system-design rounds (Day 43) ask the
questions in section 12 directly: what do you retry, how do you stop a retry creating a duplicate, what
does a file cost, what happens when the JSON is valid but wrong.

On the job, the reason is simpler. An FDE's code runs inside the customer, and the customer reads the
bill. Day 9 put about 26 lakh a year in Godavari's case for cloud in its own AWS Mumbai account, model
calls included, and gave this chapter the job of owning the per-file budget. The first question a COO
or a CFO asks about an AI system in production is "why did this one cost that much", and the second is
"why did that one take so long". You want both answered by a table you already have.

> **Analogy (Telugu audience).** UPI. Every bank agrees the field format before a rupee moves
> (structured outputs). A payment that fails half way never debits you twice, because every request
> carries a reference the bank remembers (idempotency keys and safe retries). And the app shows
> "processing" while the banks talk (streaming, for the person who is watching). UPI works at a few
> hundred million transactions a day because of those three agreements, not because any one bank is
> fast.

## 1.3 What this chapter adds to Day 11

[Day 11](../11-the-system-around-the-model/README.md) drew the system as eight boxes and sorted
Godavari's rules: regulatory and policy rules in code, reading and explaining with the model. It owns
that split and its model interface (`ExtractionModel`, with a deterministic `StubModel` and a one-call
real adapter). This chapter does not re-teach the split. It opens the model box and makes it
production-shaped:

| Day 11 left | Day 12 adds |
|---|---|
| one model call for a whole bundle, with only the SDK's default retries | per-page calls on two model tiers, retried with backoff and jitter inside a deadline |
| a schema written as plain dataclasses | the same vocabulary as a versioned Pydantic contract, sent to the provider and checked locally |
| "schema-valid is not the same as correct" | what to do about it at the API layer: content checks, one targeted re-ask, withhold, flag |
| a model-level seam, `read(bundle)`, with the vendor call inside it | a provider-level seam below it: tiers, typed errors, usage, one adapter per vendor |
| no cost or latency figures | rupees per file, p95 seconds per stage, budgets that can fail |

## 1.4 The hard parts, named up front

1. **Failures are normal.** At 40,000 calls a month, 429s and timeouts are routine traffic (section 06).
2. **Valid is not correct.** Once structured outputs make the shape reliable, wrong content parses,
   validates and flows downstream (section 03).
3. **The numbers are small and still matter.** Model calls cost a few rupees a file; the ledger is the
   baseline that lets you notice the night it doubles (section 07, Day 19).
4. **Vendor detail dates fast.** Names, prices and parameters here are as of October 2026; one adapter
   and a price card as data keep a change to one file.

By the end you will have a client that runs a simulated night of the SFTP drop offline in under a
second, shows every failure above, and prints the budget report you would show the COO before any demo.
