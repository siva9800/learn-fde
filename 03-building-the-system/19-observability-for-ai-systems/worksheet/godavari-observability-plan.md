# Observability plan · Godavari Finance: loan-file intake pilot

> For the engagement folder · Day 19 · Engagement week 8, Friday 18 December 2026 · Version 0.3 (draft for the
> Monday review) · For: Srinivas, the Vijayawada team lead, the compliance head, Godavari's application-support engineer
> · Copy: the CISO, the COO · Every figure comes from `../code/run_observability.py` on synthetic data; `../data/run-report.md` has the output

## 1. The five questions, and who answers each

| Question | Answered by | Read by | When |
|---|---|---|---|
| Is it up? | the 02:00 job finished, every SFTP arrival has a trace, the core writes match the journal | Kaagaz FDE | 07:30 every day, paged if not |
| Is it right? | corrections per field against the golden set, spot checks, rules that moved | eval owners, team leads, FDE | daily digest; weekly review |
| Is it affordable? | rupees per file against the Rs 12 ceiling, per branch per night, the month at 1,400 files | FDE; the COO weekly | daily digest; Friday page |
| Is anyone using it? | files opened in the tool, queue age, fields checked versus accepted, the Day 18 dwell signals | team leads | weekly |
| Is it safe? | values dropped and spans quarantined at the boundary; identifier scans of every record; group-sync refusals | FDE; the compliance head | daily; a quarantine is a page |

## 2. Alerts and routing

| Rule | Threshold | How | Who |
|---|---|---|---|
| queue not ready | 02:00 job not finished by 07:30 | page | Kaagaz FDE on call; application support informed |
| store quarantine | any span refused at the boundary | page | Kaagaz FDE on call; the compliance head the same day |
| core disagreement | core records not equal to write spans, or two records for one file | page | Kaagaz FDE with the application-support engineer |
| ceiling | any file over Rs 12 in model calls | digest 08:30 | Kaagaz FDE |
| spike | a branch's nightly median over 1.5 times its week-one median | digest | Kaagaz FDE |
| latency | classify stage p95 over 20 s on a night | digest | Kaagaz FDE |
| field drift | a field's correction rate outside the golden set's interval | digest | FDE and the eval owners |
| rule moved | a rule's fire share outside last week's interval, three files or more apart | digest | FDE; the compliance head for a regulatory rule |
| session or override | Day 18's rubber-stamp and override signals | digest or weekly | the analyst's own team lead only |
| directory stale | policy-panel searches refused for a group snapshot over 36 hours old | digest | Godavari IT identity team; FDE copied |

Nobody at Godavari is paged for anything the model does. The COO receives one page every Friday and no alerts.

## 3. What is never logged

PAN, Aadhaar numbers, mobile numbers, customers' names and addresses, page text, prompts and model answers, finding
messages (Day 11's quote the PAN and the names), the analyst's free-text notes, retrieval query text, and staff names.
The trace store accepts only allowlisted keys with validated values; a scanner quarantines anything that slips through.
Values live in the review screen's log and the file of record, inside Godavari's boundary, with their own access rules.

## 4. Questions for the compliance head (retention and the DPA)

| # | Question | Draft answer |
|---|---|---|
| C1 | Retention of the trace store | 13 months, so a year-on-year comparison and the RBI inspection from 1 February 2027 are both covered; to be agreed |
| C2 | Who may read it | the Kaagaz FDE and Godavari's application-support engineer; the team leads see their own dashboards only |
| C3 | Where it lives | the pilot machine in the Hyderabad building; after cutover, Godavari's AWS Mumbai account (Day 24 decides residency) |
| C4 | Does it leave Godavari | no; Kaagaz's product team receives aggregate counts only, through the masked export (Day 14) |
| C5 | Is it in the DPA | yes: telemetry is processing on Godavari's behalf; the schedule of fields goes into the DPA annex (Day 23 owns the DPA) |

## 5. Decisions and open items

| # | Item | Owner | By |
|---|---|---|---|
| O1 | the page filter (statement-continuation-v1) shipped 16 December 17:00; add five masked long-statement files to Day 14's development split | Kaagaz FDE with the eval owners | first week of January, after the freeze |
| O2 | ask Guntur's branch manager whether staff should attach the bank's summary or the full statement | Vijayawada team lead | Monday 21 December |
| O3 | ENV-CONFIDENCE fired on 25 of 30 Guntur files (16 of 30 in week one): the traces show fewer scanner uploads and more phone photos; confirm with the branch | Vijayawada team lead | Monday 21 December |
| O4 | the HR-to-AD export did not run on 17 December; the policy panel refused 3 searches that afternoon | Godavari IT identity team | before the Hyderabad wave, 6 January 2027 |
| O5 | retention and access (section 4) | the compliance head | before the cutover, 4 January 2027 |
| O6 | Day 27 turns section 3 into SLOs and an on-call rota across the two companies | Kaagaz FDE with application support | week 10 |

Prepared by the Kaagaz AI FDE. No threshold changes during the freeze, 17 to 31 December; withdrawals of a Day 18 band
cell are data changes and remain allowed.
