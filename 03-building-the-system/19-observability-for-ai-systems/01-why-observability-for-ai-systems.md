# 01 · Why Observability for AI Systems: The Tuesday Morning Digest

> Day 19 · Section 1 of 15 · [Chapter overview](README.md) · Next: [02 · The five questions](02-the-five-questions.md)

---

## 1.1 Tuesday, 08:30

Pilot week two at Godavari Finance. The 02:00 SFTP batch ran, the queue opened at 08:00, and the six pilot analysts
in Hyderabad and Vijayawada are working through Monday's uploads. Nothing is down. Nobody has complained.

The morning digest arrives in your inbox:

```text
Tue 15 Dec  spike    Guntur median Rs 10.66 per file on Tue 15 Dec, 2.0 times its week-one median of Rs 5.42; median pages 95
Tue 15 Dec  ceiling  GF-61070 (Guntur) cost Rs 14.00 in model calls; the ceiling is Rs 12 for every file; 96 pages, 119 calls
```

That is real output from this chapter's project. Without the digest, you would have found out on Friday, when the COO
asked why the model bill for the week was higher than the plan you gave him in Day 12. With it, you open one trace,
see 96 classify calls and six extraction calls on pages that carry no field, and know the cause before the analysts have
finished their first files: Guntur's branch has started attaching customers' full sixty-page net-banking statements.
A page filter ships on Wednesday at 17:00, the last change before the freeze that starts on Thursday 17 December, and
Thursday's Guntur files cost a median of Rs 5.15 again.

This chapter teaches how to build that: a trace per loan file, rupees per unit of work, quality signals when there
is no answer key, feedback as data, a logging boundary that keeps customers' identifiers out, and three dashboards
for three readers.

## 1.2 What is different about an AI system

Observability fundamentals (metrics, logs, traces, Prometheus, Grafana, Loki, the OpenTelemetry Collector,
Alertmanager) are owned by the DevOps Masterclass module
[learn-observability](../../../DevOps/learn-observability/README.md). This chapter assumes them and does not re-teach
them. What it adds is what changes when one box in the diagram is a model:

| Ordinary service | AI system at a customer |
|---|---|
| a wrong answer is a bug, and usually an error | a wrong answer is a well-formed, confident value; nothing errors |
| cost per request is roughly fixed | cost per file depends on pages, retries, escalations and the prompt; one branch can double it overnight |
| a release is a code deploy | a "release" is also a prompt version, a model snapshot, a rule version and a band file |
| logs hold request metadata | the inputs are customers' documents; logging them is a data breach |
| users are customers of the service | the operators are the customer's staff, and their corrections are your best signal |
| the dashboard reader is an engineer | three readers: the FDE, the team leads, the COO, each with a different decision |

## 1.3 Why it matters for your career

The Part file puts it plainly: the customer's first production question is "why did this one cost that much" and the
second is "is it getting worse". An FDE who can answer both from data, the same morning, keeps the engagement's
credibility through the weeks when the pilot is fragile. One who cannot spends those weeks defending a bill and an
anecdote. Applied AI appears in 80 percent or more of the 1,000 FDE postings analysed in 2026 (CURRICULUM.md, the
2026 hiring-trends source), and evals, cost and feedback after launch are where applied AI meets the customer's
production: they decide whether a pilot is renewed or quietly switched off.

It also matters for the product. Every engagement's traces, in the same shape, are what Kaagaz's product team
learns from (Day 36): which page types cost most, which fields analysts correct, which prompts regress.

## 1.4 Where this sits

The chapters before this one already produce the signals; this one gives them a home.

| Day | Already produces | Day 19 turns it into |
|---|---|---|
| 11 | rule findings, routes, a sign-off fingerprint | rule fire rates per branch, the rules version on every trace |
| 12 | a ledger row per model attempt, the Rs 12 ceiling, latency budgets | a span per attempt, cost roll-ups, ceiling and latency alerts |
| 13 | prompt releases pinned per environment | the release on every trace; cost and quality grouped by it |
| 14 | the golden set's per-field error rates | the baseline that production corrections are compared with |
| 15 | permission-aware search with a stale-snapshot refusal | retrieval spans: results, refusals, snapshot age |
| 16 | the write journal, the reconciliation history | write health on the FDE page; a nightly proof the journal stays clean |
| 17 | the workflow's audit log, approvals and step budgets | approval waits, budget headroom |
| 18 | the screen log, corrections with reasons, rubber-stamp signals, spot checks | feedback events, correction rates, the team leads' page |

Day 27 takes the alerts here and turns them into SLOs and on-call across two companies. Day 37 measures the value the
COO's page only previews.

## 1.5 The hard parts, named now

Three things in this chapter feel harder than they look. That is normal.

1. **"Is it right?" has no answer key in production.** Everything you can measure is a proxy; the skill is knowing
   what each proxy can and cannot tell you (section 05).
2. **The most useful data is the most dangerous to log.** Page text, model answers and analysts' corrections are
   exactly what would explain a failure, and exactly what must not leave the screen (section 07).
3. **Three readers, three decisions.** A dashboard that serves everyone serves no one; most of the work is deciding
   what to leave off each page (section 08).

> **Analogy (Telugu audience).** Cricket. The scorecard is the dashboard; the ball-by-ball commentary is the trace.
> When the run rate drops you do not stare at the scorecard; you go to the ball-by-ball and find the over that did it.
> Guntur's Tuesday was one bad over, and the trace is where you found it.
