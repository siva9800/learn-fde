# 10 · Production Concerns: Cost, Latency, Scale, Security, Monitoring

> Day 17 · Section 10 of 16 · [Chapter overview](README.md) · Previous: [09 · Advanced and 2026 patterns](09-advanced-and-2026-patterns.md) · Next: [11 · Project: the send-back workflow](11-project-the-send-back-workflow.md)

---

## 10.1 Cost

Three costs, and only one of them is the model.

| Cost | Per send-back | A month at about 390 send-backs | Lever |
|---|---|---|---|
| model calls for drafting (if a model drafts) | Rs 1.82 measured on the large tier, five turns | about Rs 710 | template the body, let the model write only the issue sentences; a small tier; cache the stable prefix (Day 12) |
| analyst approval | about 2 minutes | about 13 hours, about Rs 5,960 at Rs 456 an hour | show the findings and the pages beside the draft (Day 18) so the check is fast |
| storage and audit | a few kilobytes of events | negligible | retention set with the compliance head (seven years, finding A6) |

The send-back volume (28 percent of about 1,400 paper and PDF files a month) is Day 9's hand count applied to Day 4's
intake volume, so these are planning numbers until the pilot measures them. The model cost is the smallest line and the
one most likely to surprise: per-turn cost rises with the history (0.25 to 0.65 rupees across five turns), so a planner
that takes ten steps instead of five costs well over twice as much. The step budget is a cost control.

## 10.2 Latency

The promise to branch managers is "a missing-document notice the day the file arrives" (Day 10). The workflow's own
latency is seconds; the latency that matters is the approval wait. In the synthetic week the simulated analysts decided about half
of the proposals within an hour, and five went to a team lead at the four-hour mark. Measure in the pilot: time from CHECKED to
SENDING, by analyst and by branch, p50 and p95. If p95 crosses the same day, the fix is staffing or the deadline, not
the model.

The 18:00 credit-check batch and the 17:30 to 20:00 write window (Day 6, step 17; finding A4) affect the core write,
not the email. Day 16's writer defers writes inside the window; the PUSHING state simply stays PUSHING until it may
write, which is one more reason in-flight states exist.

## 10.3 Scale

About 1,400 intake files a month is roughly 70 a working day: small for any database. The constraints are elsewhere.
**One writer per run**: the optimistic version check makes a second worker fail with `StaleRun`; with more workers add
a lease per run. **SQLite to Postgres** when the pilot moves to AWS Mumbai (cutover 4 January 2027), with the schema and
the single-transaction rule unchanged. **The targets' limits**: Day 16 found an undocumented core rate limit ("CL-E099
SERVICE BUSY"), so recovery after an outage drains in-flight runs through the same rate limiter as normal traffic.

## 10.4 Security

| Concern | Control in this design |
|---|---|
| the planner acting outside its job | read and propose tools only; a refused write stops the run |
| a person approving what she cannot see | `visible_to` with her AD groups at decision time (finding A1; Day 22 owns identity) |
| a customer receiving anything | no customer addresses in the directory; the recipient is never a model output |
| PII spreading | bodies only in the approval queue; the audit log holds them by hash; `pii_hits` finds nothing in it |
| tampering with the trail | hash chain plus a daily export of the last hash |
| the service account | no approval right, no branch groups; it acts only through tools |

The CISO's questionnaire (Day 23) will ask whether the system can act without a human. The honest answer, with
evidence, is `data/tool-inventory.md` and the state table: two irreversible actions, each reachable only through a human
transition.

## 10.5 Monitoring

What to put on the Day 19 dashboard from this chapter's events, each with a threshold and an owner:

| Signal | Source | Normal | Investigate when |
|---|---|---|---|
| refused write attempts by a planner | `tool_refused` with a write risk | 0 | any |
| planner failures by reason | `planner_failed` | a handful a week | a new reason, or a jump after a prompt or model change |
| approvals escalated | `approval_escalated` | a few a day | one analyst or branch dominates |
| approval edit rate | `approval_decided` with `edited` | some | near 0 (rubber-stamping?) or high (drafts are poor) |
| rejections by branch | `send_rejected` | low | one branch high: wrong recipient or wording |
| send-back cycles reaching the cap | `route_review` with the cycle reason | low | a document type that branches keep getting wrong |
| relay messages minus approvals | reconciliation | 0 | any |
| core records minus pushed runs | reconciliation | 0 | any (Day 16's nightly report) |
| audit chain | `verify_chain` nightly | intact | any break |

The last three are not dashboards but alarms. A duplicate email is a page to the FDE, the same night.

## 10.6 Operating it across two companies

In the pilot the Kaagaz FDE is called, with Godavari's application-support engineer (assigned by IT in week 2)
shadowing. Four runbook lines for Days 27 and 28: a FAILED run is read, fixed at the cause and worked by hand, never
"retry all failed"; runs stuck in SENDING or PUSHING get `recover()` and a reconciliation, never a hand-edited state;
an approval overdue at level 2 goes to the team lead, never approved on her behalf; a suspected duplicate is counted in
the target first, then traced by its key.
