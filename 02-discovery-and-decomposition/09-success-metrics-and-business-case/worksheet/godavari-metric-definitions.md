# Pre-registered metric definitions · Godavari Finance: loan-file intake

> Engagement folder · Day 9 · Signed in discovery week 4, before the pilot touches a production file · Version 1
> Changes after signature need the same signatures and a line in the change log. Day 37 measures against these definitions; Day 19's dashboard computes them.

## A. Headline metrics (business rung)

| Metric | Definition | Population and exclusions | Baseline (method: baseline pack v1) | Target | A change is claimed when | Guardrail |
|---|---|---|---|---|---|---|
| median turnaround | calendar days from the customer's signature on the application form to the decision (sanction, rejection or withdrawal recorded) | every new file from the named pilot branches; resubmissions keep the original signing date; no exclusions | 9.1 days (8.7 to 9.7) | 3 to 4 days in the pilot branches by day 90 | the pilot's 95 percent interval lies entirely below 8.5 days | files decided with a mandatory document missing |
| decided with a mandatory document missing | share of decided files where PAN, address proof, income proof or photo is absent from the file of record at decision, by the compliance head's "present" rule | all new files from the pilot branches | 4.1% (0.9 to 7.2); a census of the baseline frame is to follow | below the baseline, every month | the compliance head's monthly re-draw agrees | none: this is the guardrail |
| customers who withdraw | share of new files closed as withdrawn by the customer | all new files from the pilot branches | 10.1% (5.2 to 14.9) | measured, not targeted; the case breaks even at about 3 in 10 of would-be-sanctioned walk-aways kept | the pilot's rate is below the baseline's interval | none |

## B. Operational metrics (managed weekly)

| Metric | Definition | Baseline | Target |
|---|---|---|---|
| addressable hours per file | re-keying + completeness check + chasing the branch, per new file; measured by the timing log before launch and the review screen's timer plus the timing log for a fortnight after | 1.59 h (1.52 to 1.66) | 0.5 to 0.9 h |
| queue age | hours from SFTP arrival to first opened (core record-creation time before launch; review screen after; both run for a fortnight at the switch-over) | 6.4 days (mean) | under 2 days |
| send-back rate | share of new files with at least one request to the branch for a missing or defective document, by any channel that can be dated | 28% (21 to 35) | not targeted in the first 90 days; the delay is the lever |
| send-back notice delay | days from SFTP arrival to the branch being told what is missing | after the queue: about 6 to 7 days | same day |

## C. System metrics (engineered; never the headline)

| Metric | Definition | Measured on | Threshold the case needs |
|---|---|---|---|
| field-level accuracy | share of mandatory fields where the extracted value equals what the eval owners (Lakshmi, the senior analyst) would have typed; handwritten Telugu fields reported separately | the held-out part of the golden set (Day 14) | 90 to 95 percent or more, with uncertain fields routed to review |
| completeness recall | of files truly missing a mandatory document, the share the rules flag | the golden set, completeness labels signed by the compliance head | no misses on mandatory documents |
| completeness precision | of files the rules flag, the share truly missing something | the golden set | agreed with the branch managers after the first run |
| ready time | share of files with fields and completeness ready by 9 am the morning after SFTP arrival | production logs | 95 percent |
| analysts' own keying error rate | the same accuracy definition applied to 30 double-keyed golden-set files | the golden set | a baseline, not a target |

## D. Leading indicators, with expected direction by pilot week 10

Pilot files opened in the tool above 90 percent · files flagged on the day of arrival above 80 percent of
eventual send-backs · review-queue age at 10 am under 2 days · fields corrected per file falling, below
3 of 23 · distinct file numbers through the tool equal to SFTP arrivals.

## E. Rules that apply to every metric

1. The baseline sample's seed and file list are fixed; nobody re-draws.
2. Months with the RBI inspection, a quarter-end freeze or a festival week are flagged in every
   comparison, not dropped.
3. A metric that cannot be computed from logs is computed by the same hand method as the baseline.
4. The FDE does not compute the headline alone: Bhavani recomputes it monthly, and the compliance head
   re-draws one month in three.

## Signatures

| Role | For | Signed |
|---|---|---|
| the COO | section A, the targets | week 4 |
| the compliance head | section A (missing-document metric, "present" rule), section C (completeness) | week 4 |
| Srinivas, credit-ops team lead, Hyderabad | section B | week 4 |
| the credit-ops team lead, Vijayawada | section B | week 4 |
| the Kaagaz AI FDE | all, as author | week 4 |

## Change log

| Version | What changed | Who signed |
|---|---|---|
| 1 | first issue | as above |
