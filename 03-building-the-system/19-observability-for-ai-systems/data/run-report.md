# Day 19 run report

> The output of `python -X utf8 code/run_observability.py`, verbatim. Synthetic data, simulated analysts.

```text
== Day 19 · observability for Godavari's pilot: Kukatpally and Guntur, 7 to 18 December 2026 ==
spans written: 5830 in 180 traces; prompt release pinned for pilot: extraction@2.0.0+fake-large-2026-10
boundary: 0 attribute values dropped, 0 spans quarantined

-- 1. checks on the traces --
  SFTP arrivals 120; file traces 120; distinct file numbers 120
  traces missing a stage: 0; core.write spans 71 for 71 files written; core records created 71
  rupees: ledger Rs 676.5666, traces Rs 676.5666, difference Rs 0.000000
  models in the calls ['fake-large-2026-10', 'fake-small-2026-10']; the release pins ['fake-large-2026-10', 'fake-small-2026-10']: match
  week one's screen log against Day 18's data/pilot-week-1/action-log.jsonl: identical (840 events)

-- 2. cost per file (model calls, Rs), from the traces --
  pilot-week-1: 60 files, median 5.40, p95 7.73, max 9.46, total 320.40; at 1,400 files a month about Rs 7,476 (Day 12 measured about Rs 8,900)
  pilot-week-2: 60 files, median 5.47, p95 10.56, max 14.00, total 356.16; at 1,400 files a month about Rs 8,311 (Day 12 measured about Rs 8,900)
  by night and branch: files, median Rs, max Rs, median pages in the file / sent to the model
    Mon 07 Dec Guntur       6   4.35   7.22    25.5 /  25.5
    Mon 07 Dec Kukatpally   6   4.49   6.17    21.5 /  21.5
    Tue 08 Dec Guntur       6   5.15   6.99    23.0 /  23.0
    Tue 08 Dec Kukatpally   6   5.64   9.46    27.5 /  27.5
    Wed 09 Dec Guntur       6   5.42   7.80    19.5 /  19.5
    Wed 09 Dec Kukatpally   6   5.73   7.25    23.0 /  23.0
    Fri 11 Dec Guntur      12   5.58   8.59    30.0 /  30.0
    Fri 11 Dec Kukatpally  12   4.79   6.43    28.0 /  28.0
    Mon 14 Dec Guntur       6   6.05   7.19    31.5 /  31.5
    Mon 14 Dec Kukatpally   6   4.33   6.36    17.0 /  17.0
    Tue 15 Dec Guntur       6  10.66  14.00    95.0 /  95.0
    Tue 15 Dec Kukatpally   6   4.06   4.76    25.5 /  25.5
    Wed 16 Dec Guntur       6   8.74   9.94    83.5 /  83.5
    Wed 16 Dec Kukatpally   6   5.02   6.96    18.0 /  18.0
    Thu 17 Dec Guntur       6   5.15   8.65    81.5 /  22.5
    Thu 17 Dec Kukatpally   6   5.85   7.11    21.5 /  21.5
    Fri 18 Dec Guntur       6   3.99   5.55    75.5 /  16.5
    Fri 18 Dec Kukatpally   6   5.27   6.12    20.5 /  20.5
  by stage, pilot-week-1: classify 14.79, escalate 51.53, extract 254.08
  by stage, pilot-week-2: classify 20.50, escalate 65.93, extract 269.74
  by prompt release: extraction@2.0.0+fake-large-2026-10: 120 files, median 5.43
  by product: two-wheeler: 120 files
  alerts: 3
    Tue 15 Dec spike    Guntur median Rs 10.66 per file on Tue 15 Dec, 2.0 times its week-one median of Rs 5.42; median pages 95
    Tue 15 Dec ceiling  GF-61070 (Guntur) cost Rs 14.00 in model calls; the ceiling is Rs 12 for every file; 96 pages, 119 calls
    Wed 16 Dec spike    Guntur median Rs 8.74 per file on Wed 16 Dec, 1.6 times its week-one median of Rs 5.42; median pages 84

-- 3. Tuesday's most expensive file, from its trace --
  GF-61070 (Guntur, Tue 15 Dec): 96 pages, 59 of them statement continuation pages; 119 model calls costing Rs 14.00
  calls by stage: {'classify': 96, 'escalate': 10, 'extract': 13}; on continuation pages: {'classify': 59, 'escalate': 4, 'extract': 6}, Rs 5.99 of the total
  Guntur files with a long statement: before the filter 12 (median Rs 9.16, median 90 pages to the model); after it 12 (median Rs 4.36, median 19 pages to the model)
  the filter over Day 14's golden set: 200 files, 0 pages held back; the regression gate passes it without judging it

-- 4. latency by stage (p50 / p95) --
  pilot-week-1: classify stage 10.4 / 25.8 s (budget p95 20); extract stage 8.0 / 35.6 s (budget p95 90); ready by 09:00 100%; queue wait 10.7 h median, 10.5 h mean; review 168 min median; writes held for the evening window 3 of 34
  pilot-week-2: classify stage 9.8 / 19.9 s (budget p95 20); extract stage 8.1 / 36.4 s (budget p95 90); ready by 09:00 100%; queue wait 10.3 h median, 9.4 h mean; review 166 min median; writes held for the evening window 0 of 37

-- 5. the weekly quality job (week two; baselines: Day 14's golden set and week one) --
  correction rate per field (content changes per file reviewed) against the golden set's error rate:
    applicant_name      5 of 60    8.3% (3.6% to 18.1%)   golden  5.3% (2.7% to 10.2%)   in line
    date_of_birth       4 of 60    6.7% (2.6% to 15.9%)   golden  4.0% (1.8% to 8.5%)   in line
    pan                 5 of 60    8.3% (3.6% to 18.1%)   golden  6.0% (3.2% to 11.0%)   in line
    address             1 of 60    1.7% (0.3% to 8.9%)   golden  0.0% (0.0% to 2.5%)   in line
    mobile              1 of 60    1.7% (0.3% to 8.9%)   golden  0.0% (0.0% to 2.5%)   in line
    requested_amount    3 of 60    5.0% (1.7% to 13.7%)   golden  3.3% (1.4% to 7.6%)   in line
    tenure_months       1 of 60    1.7% (0.3% to 8.9%)   golden  0.0% (0.0% to 2.5%)   in line
    monthly_income      5 of 60    8.3% (3.6% to 18.1%)   golden  4.0% (1.6% to 9.8%)   in line
    application_date    1 of 60    1.7% (0.3% to 8.9%)   golden  1.3% (0.4% to 4.7%)   in line
    on_road_price       0 of 60    0.0% (0.0% to 6.0%)   golden  8.0% (4.1% to 15.0%)   in line
    dealer_code         0 of 60    0.0% (0.0% to 6.0%)   golden  2.0% (0.6% to 7.0%)   in line
    quotation_date      0 of 60    0.0% (0.0% to 6.0%)   golden  1.0% (0.2% to 5.4%)   in line
  pilot-week-1 Guntur    : files 30, review 40%, send back 33%, ENV-GROUND on 13%, content corrections 0.23 per file, unsure 0.20 and unclassified pages 11.73 per file
  pilot-week-1 Kukatpally: files 30, review 40%, send back 50%, ENV-GROUND on 10%, content corrections 0.23 per file, unsure 0.63 and unclassified pages 12.73 per file
  pilot-week-2 Guntur    : files 30, review 63%, send back 23%, ENV-GROUND on 10%, content corrections 0.40 per file, unsure 0.20 and unclassified pages 12.60 per file
  pilot-week-2 Kukatpally: files 30, review 37%, send back 40%, ENV-GROUND on 10%, content corrections 0.47 per file, unsure 0.60 and unclassified pages 8.30 per file
  rules and envelope checks that moved, week one to week two (share of files):
    ENV-CONFIDENCE   Guntur     16/30 -> 25/30
    TW-DOC-05        Guntur     5/30 -> 2/30
  review-band overrides, week two (expected wrong share 5.4%): H1 2/55 (p=0.42); H2 1/35 (p=0.43); H3 2/51 (p=0.47); V1 5/54 (p=0.92); V2 4/54 (p=0.82); V3 2/44 (p=0.57)
  rubber-stamp sessions flagged: week one 1, week two 0; fast-only sessions 2 and 4
  spot checks, week 1: 6 files drawn at random, 47 auto-accepted fields read again, 0 wrong; upper bound 7.6%
  spot checks, week 2: 6 files drawn at random, 44 auto-accepted fields read again, 0 wrong; upper bound 8.0%
  policy panel: 60 searches over both weeks, 0 with no result, 3 refused (group snapshot older than 36 hours)
  to Day 14's development split:
    - 24 files over 60 pages this week (the longest of the golden set's 200 files has 40): add five masked long-statement files to Day 14's development split, labelled and adjudicated as usual

-- 6. upstream records: counts in, identifiers out --
  Day 16 journal: 12 writes {'CONFIRMED': 9, 'EXISTS_NOT_OURS': 1, 'FAILED': 2}; reconciliation history 1 night(s), clean run 1 (last 2026-11-13); identifiers found: none
  Day 17 audit log: 824 events on 45 files; approvals asked 23, decided 23, escalated 5, refused 1; wait median 90.0 min, max 330.0 min; drafting runs 24, most tool calls 6 of a step budget of 8; identifiers found: none
  Day 18's correction events as written: 36, 15 carrying a value; identifier kinds in the file: ['pan']; through the boundary as raw attributes: 36 stored, 0 quarantined; dropped 396 values, e.g. analyst: not on the allowlist, analyst_value: not on the allowlist, at: not on the allowlist
    Day 12 night per file (CSV): none
    Day 15 view log: none
    Day 16 write journal (journal.sqlite): none
    Day 17 audit log: none
    Day 18 corrections (corrections.jsonl): pan
    Day 18 screen log (action-log.jsonl): mobile, pan
  the trace store itself: none

-- 7. alerts and where they went --
  page rules checked every night: the latest-finishing 02:00 job ended Fri 11 Dec 02:02:32; core records 71, write spans 71, files with two records 0; spans quarantined 0
  page: 0
  digest: 7; ceiling -> Kaagaz FDE; directory stale -> Godavari IT identity team; Kaagaz FDE copied; latency -> Kaagaz FDE; rule moved -> Kaagaz FDE; the compliance head if a regulatory rule; spike -> Kaagaz FDE
  weekly: 0

wrote data/traces.sqlite, data/sample-trace-GF-61070.jsonl, data/alerts.jsonl, data/run-report.md and 3 dashboards in data/dashboards/; 14.2 s
```
