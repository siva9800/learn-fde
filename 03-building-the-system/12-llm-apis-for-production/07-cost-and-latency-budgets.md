# 07 · Cost and Latency Budgets: Rupees per Loan File, p95 Seconds per Stage

> Day 12 · Section 7 of 14 · [Chapter overview](README.md) · Previous: [06 · Retries, timeouts and rate limits](06-retries-timeouts-and-rate-limits.md) · Next: [08 · Caching, batch APIs and model choice](08-caching-batch-and-model-choice.md)

---

## 7.1 Budget per unit of work, not per month

A monthly bill tells you that something changed. A budget per loan file tells you which file, which
stage and which page. Godavari's unit of work is the loan file, so both budgets are per file: a rupee
ceiling for model calls, and a p95 processing time for a 36-to-40-page bundle, with a sub-budget for
each stage. Everything in the ledger rolls up to those two numbers.

## 7.2 What a page costs in tokens

| Token stream | Where it comes from | Size in this chapter's model |
|---|---|---|
| page image | Anthropic's PDF documentation estimates 1,500 to 3,000 text tokens per page, plus image tokens for each page rendered as an image | full page for extraction about 1,600 tokens; low-resolution thumbnail for classification about 450 |
| stable prefix | instructions plus the schema | about 1,380 tokens for extraction (cacheable); about 330 for classification (too small to cache) |
| variable text | "File X, page 7, classified as ..." | about 30 tokens |
| output | the JSON, evidence strings included | 150 to 600 tokens |
| reasoning | thinking tokens on the large tier, billed as output | about 220 per call in the fake |

These are the fake provider's numbers, chosen to be realistic. On a real engagement you measure them:
Anthropic offers a token-counting endpoint, and every response's usage block reports what was billed.

## 7.3 The price card, dated

Read on 21 October 2026 from the official pages (US dollars per million tokens):

| Model | Input | Cache read | 5-minute cache write | Output | Source |
|---|---|---|---|---|---|
| Claude Haiku 5.5 (prompts up to 100,000 tokens) | 0.10 | 0.01 | 0.125 | 0.50 | Anthropic pricing page |
| Claude Sonnet 5.5 | 2.00 | 0.10 | 2.50 | 10.00 | Anthropic pricing page |
| Claude Opus 5.5 | 4.00 | 0.20 | 5.00 | 20.00 | Anthropic pricing page |
| gpt-6-luna | 0.10 | 0.01 (cached input) | not listed | 0.50 | OpenAI pricing page |
| gpt-6.1-sol | 2.00 | 0.10 (cached input) | not listed | 10.00 | OpenAI pricing page |
| gpt-5.6-terra | 2.00 | 0.20 (cached input) | not listed | 12.00 | OpenAI pricing page |

Both pages list batch processing at half price, and both list a 10 percent premium for regional or
data-residency processing (Anthropic: `inference_geo: "us"` at 1.1 times, and regional endpoints on
Bedrock and Google Cloud at 10 percent over global; OpenAI: regional-processing endpoints at 10 percent
for models released on or after 5 March 2026).

The project's price card (`ledger.py`) has two tiers priced where the two vendors coincide: small at
0.10 / 0.50 and large at 2.00 / 10.00, with the cache prices above, a 1.10 residency uplift (Godavari will
need an in-country route; section 08), and **Rs 95 per US dollar, an assumption** near the RBI reference
rate of mid-2026 that you must replace with the rate on the day you present. Prices are data in one
dictionary, because they will change before this chapter is a year old.

## 7.4 One page, in rupees

An extraction page on the large tier: 1,700 fresh input tokens, 1,380 read from cache, 820 output
(JSON, evidence and thinking):

```text
input        1,700 x $2.00 / 1M = $0.00340
cache read   1,380 x $0.10 / 1M = $0.00014
output         820 x $10.00 / 1M = $0.00820
subtotal                          $0.01174
x 1.10 residency uplift           $0.01291   x Rs 95  =  about Rs 1.23
```

Two things to see. **Output is 70 percent of the cost of a page**, so the length of evidence strings and
the reasoning effort matter more than the size of the prompt. And **the cached prefix costs a twentieth
of fresh input** on this tier (0.05 times, the multiplier Anthropic lists for Sonnet 5.5 and Opus 5.5;
0.1 times on most other models). The test `test_one_extraction_page_in_rupees` holds this arithmetic.

## 7.5 One file, measured

From the simulated night of 60 files and 1,282 pages:

```text
cost per file, model calls (Rs): p50 6.34, p95 8.73, max 9.57 (WGL-26-00054, 39 pages); 36-40 page files max 9.57
  budget Rs 12.00 per file: PASS; night total Rs 381.89; per 1,400 files a month about Rs 8,911
  by stage (Rs): classify 12.25, escalate 51.87, extract 314.16, repair 10.05
```

About Rs 8,900 a month, roughly 1.1 lakh a year at 1,400 files a month: a few percent of the 26 lakh
cloud line in Day 9's case. Model calls are not where Godavari's money goes. That is worth saying to the
CFO early, and it is not a reason to skip the budget: the budget is what tells you, the morning after,
that a new branch's sixty-page bank statements doubled the cost per file (Day 19's incident).

## 7.6 Setting the cost budget

The ceiling is **Rs 12 per file for model calls**, and every file must be under it, not the average.
Where it comes from:

- Day 9's sizing: 26 lakh a year for about 20,000 files is about Rs 130 per file for everything in
  Godavari's AWS account (compute, storage, logs, the VPC and model calls).
- Model calls get under a tenth of that, leaving the rest for infrastructure that does not shrink.
- Rs 12 is about 1.25 times the worst file in the measured night: room for a heavier night, not for a
  regression. A prompt change that pushes any file over it fails the run.

A budget that is never allowed to fail is a forecast. This one is a check in the run, and it goes to
Day 19's dashboard as an alert. It does fail: across forty simulated nights (40 seeds, 2,400 files), the
most expensive file cost Rs 12.04, four paise over, after a run of retries and re-asks. One file in
2,400 is the alert working, not the budget being wrong; ten a night would be a regression to find.

## 7.7 The latency budget per stage

| Stage | Budget (p95) | Measured p95 | What drives it |
|---|---|---|---|
| queue wait in the 02:00 drop | until 08:00 | the night ended at 02:10:07 | concurrency pool size, outages |
| classify all pages (small tier, thumbnails) | 20 s | 14.0 s | waiting for a slot in the shared pool, escalations to the large tier |
| extract the field-bearing pages (large tier) | 90 s | 38.0 s | output length, reasoning, the slow tail, retries |
| parse, check, merge (code) | under 1 s | negligible | |
| **whole file, 36 to 40 pages** | **120 s** | **27.2 s (n=5)** | the slowest page in the extract stage |

The p95 of two minutes per bundle is for the cases where someone is waiting: Lakshmi re-running a file
from the review screen, or a morning when the 02:00 job failed and sixty files must be processed in the
hour before the queue opens. For the nightly run itself, the budget that matters is the batch deadline,
and it has almost six hours of slack, which is exactly why section 08 asks whether that slack can be sold
for a discount.

A p95 from five files is a weak number; Day 14's golden set and Day 19's traces give you hundreds.

## 7.8 Model tiering

Classification goes to the small tier on a thumbnail; extraction to the large tier on the full page;
a classification under 0.60 confidence escalates to the large tier. The ledger shows the price of that
last rule: 65 escalations cost Rs 51.87, more than four times all 1,282 small-tier classifications
(Rs 12.25). The escalation threshold is a cost lever with an accuracy price, and the only way to move it
is to measure both on Day 14's golden set. Before building a cascade at all, measure the simpler
alternative: one capable model at low effort for both stages. Anthropic's own cost guidance makes the
same recommendation, since one model also means one prompt cache.

## 7.9 Twenty files before anyone sees a demo

The Part's rule for this Day: set the budget, then measure twenty files against it before any demo.
`run_nightly_batch.py --files 20` does it: worst file Rs 9.51, 40-page p95 22.8 s, and one wrong value
accepted in 100 fields. Put that last number on the week-three demo's first slide (Day 20) beside the
cost. A budget report that shows only rupees and seconds hides the number the compliance head will ask
about.
