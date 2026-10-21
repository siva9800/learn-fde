# Model-call budget · Godavari Finance: loan-file extraction

> For the engagement folder · Day 12 · Engagement week 2, before the week-3 skeleton demo · Version 1 · Measured on a simulated night of synthetic files; every figure has its command in `../code/run_nightly_batch.py`

## What this covers

Model calls for page classification and field extraction in the 02:00 SFTP drop, through
`code/godavari_llm/`. Not compute, storage or the VPC (Day 21), the review screen (Day 18) or the
core-system write (Day 17).

## The contract

`data/loan-file-extraction.schema.json`, version `godavari-extraction/1.0`: applicant name and PAN,
co-applicant, product, requested amount, income evidence and the documents present, every field with a
value or null, a confidence, a page and the exact line it was read from. The model reads pages; code
assembles the file, decides conflicts and writes the review reasons.

## The budgets

| Budget | Value | Where it comes from |
|---|---|---|
| model calls per file | **Rs 12, every file** | under a tenth of the Rs 130 per file implied by Day 9's 26 lakh cloud line for about 20,000 files |
| processing time, 36 to 40 page file | **p95 120 s** | the analyst who re-runs a file; the morning the 02:00 job must be re-run in an hour |
| classify stage / extract stage | p95 20 s / 90 s | the slowest page in each stage |
| the nightly drop | finished by 08:00 | the queue opens to analysts |

## Measured (simulated night: 60 files, 1,282 pages, an outage from 02:04 to 02:07)

| Measure | Result |
|---|---|
| cost per file | p50 Rs 6.34, p95 Rs 8.73, max Rs 9.57: **pass** |
| at 1,400 files a month | about Rs 8,900 a month, about 1.1 lakh a year |
| processing time, 36 to 40 pages | p95 27.2 s (5 files): **pass** |
| classify / extract stage p95 | 14.0 s / 38.0 s: **pass** |
| night finished | 02:10:07, with the outage absorbed by the breaker |
| re-run of the same night | 0 calls, Rs 0 |
| fields against the synthetic truth | 294 of 300 correct, 5 withheld for review, **1 wrong and accepted** (the ex-showroom price read as the requested amount) |
| files to the review queue | 11 of 60, each with a reason |
| twenty-file check (`--files 20`) | max Rs 9.51, 40-page p95 22.8 s, 1 wrong and accepted of 100 fields |

## What breaks it

Pages extracted per file (only the first page of each bank statement is extracted); output length and
effort (output is about 70 percent of a page's cost); the escalation threshold (65 escalations cost four
times all small-tier classification); and the route Day 24 allows, which may price differently and may
not offer batch. Prices assume list prices, a 10 percent residency uplift and Rs 95 per dollar.

## Open items

| # | Item | Owner | By |
|---|---|---|---|
| B1 | replace the synthetic night with 20 masked real files when the compliance head approves them | Kaagaz FDE with the compliance head | before the week-3 demo |
| B2 | the India-processing route and its real price, with the CISO | Kaagaz FDE with the CISO (Day 24) | week-6 checkpoint |
| B3 | per-field accuracy on the golden set, including the wrong-amount-line case | Kaagaz FDE with two senior analysts (Day 14) | before any threshold is changed |
| B4 | the cost-per-file and wrong-answer lines on the dashboard, with the Rs 12 alert | Kaagaz FDE (Day 19) | pilot start, week 7 |
| B5 | who pays for serving: Godavari's AWS bill or Kaagaz's subscription (open since Day 9) | Kaagaz engagement lead with the COO | the commercial page of the readout |

Prepared by the Kaagaz AI FDE · For: the COO, the ops leads · Copy: the CISO, the compliance head
