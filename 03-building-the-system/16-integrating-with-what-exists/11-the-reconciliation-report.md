# 11 · The Reconciliation Report the Core-System Owner Trusts

> Day 16 · Section 11 of 18 · [Chapter overview](README.md) · Previous: [10 · Contract tests and drift](10-contract-tests-and-drift.md) · Next: [12 · 2026 patterns and production concerns](12-2026-patterns-and-production-concerns.md)

---

## 11.1 "Bring the log"

The owner's condition for production writes: "I will say yes when I have seen your calls in the sandbox
for a month, every one logged, with no duplicates and nothing outside the batch window." The FDE's
promise in week 1: "Next week I bring the log and you tell me what is wrong with it." His answer: "Bring
the log." Risk R5 in the discovery document is "duplicates in the live core system", with the mitigation
"no live writes (M14) until a clean month". The reconciliation report is how a month becomes evidence.

A **reconciliation** compares two or more records of the same events and lists every difference. Banks
reconcile ledgers every night; integrations should too, because the failure an idempotent writer prevents
is the one nobody notices until month end.

## 11.2 What makes a report trustworthy

A report the owner trusts is not one that says "all good". It is one he can check:

| Property | How the job does it |
|---|---|
| it reads his system, not our memory | every journaled write is looked up live in the core; our call log is compared with the access log he exports |
| every count ties out | calls: ours 23, his 23; looked up 10, exactly one application each 10 |
| exceptions are file numbers with evidence | "GF-25147: tracker says keyed, the core says shell", never "98 percent consistent" |
| it is deterministic and idempotent | the same inputs give the same report; re-running for a date replaces that date's history line |
| it says what it could not check | a section for that, every night |
| it says how fresh each source was | "reporting copy refreshed 13 Nov 2026 05:00" |
| it carries versions | the job's version, the mapping's version and fingerprint, the SQL it ran |
| it writes nothing | except our own report and history file |

The senior analyst's test for the accuracy report applies here too: "the actual files, not a percentage"
(finding A8). And it is written for him: his terms (CL-E codes, APPL_STAT letters, his account name), not
Kaagaz's internal states.

## 11.3 The sections

`reconcile.py` builds eight sections; the real report for Friday 13 November is
`data/reconciliation-2026-11-13.md`.

1. **Our writes, checked against the core.** For every CONFIRMED or EXISTS_NOT_OURS write, a live lookup:
   exactly one application, carrying our key in `EXT_REF` if we made it. Duplicates are listed by file and
   application ID. UNKNOWN or DUPLICATE_IN_CORE in the journal makes the night not clean.
2. **Fields changed after our write.** The journal kept the business fields we sent; the job compares them
   with the core now. A branch user changing `LOAN_AMT` on the green screen is normal and listed, so
   nobody is surprised (the test does exactly that edit).
3. **Our call log against his access log.** By operation and outcome. The two writes we logged as "no
   reply" appear in his log as OK: that is what "ambiguous" means, and the report says so in a sentence.
   It also counts, from **his** log, files with more than one successful CreateApplication, and write
   calls inside the window. Those two numbers are the duplicate and window conditions measured by his own
   system.
4. **The 02:00 batch.** Per poll: listed, picked, re-scan, already picked, partial, late, missing, corrupt.
5. **The trackers against production.** The migration's numbers, the row for a person, the conflict, and
   the tracker-versus-core disagreements from the reporting copy.
6. **Codes the mapping does not know.** `APPLSTAT H`, for the owner's review.
7. **The month of logged calls.** Consecutive clean nights in the history file, against his condition.
8. **What the report could not check.** Production writes (none yet), the sandbox's credit checks (stale),
   applications carrying our key on files we never journaled (needs a query only he can run), the WhatsApp
   pages (they reach no system).

An appendix lists the SQL the job ran on the reporting copy, so he can run it himself.

## 11.4 Clean, and what "clean" is allowed to mean

The night is CLEAN when writes reconcile, the call logs agree, nothing wrote in the window and the batch
has nothing missing, corrupt or still partial. Tracker disagreements and unknown codes are findings for
the team leads and the owner, not failures of the integration, and the report says which is which. A
report that turned red for every tracker typo would be ignored in a week; one that stayed green while a
duplicate existed would be ignored forever.

## 11.5 Running it as its own job

The reconciliation runs at 06:00 as a separate job with its own read-only client, after the day's logs are
frozen. Built into the writer, it would share the writer's assumptions and its bugs; run with the
writer's call log still open, it would count its own lookups. The night run shows the second mistake was
made while this chapter was being written: the first version compared a live call log, found 42 calls
against the access log's 23, and reported NOT CLEAN. The fix, freezing both logs at the same moment and
reconciling with a separate client, is two lines; finding it took the report doing its job.

## 11.6 A month, a line at a time

`update_history()` keeps one line per date in `data/reconciliation-history.csv`. Thirty consecutive clean
lines from 9 November is the owner's month before live writes on Tuesday 8 December (M14). The history is
idempotent: run the job three times on one morning and there is still one line for that date, the last.
