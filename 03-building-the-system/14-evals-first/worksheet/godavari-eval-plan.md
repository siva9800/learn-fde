# Eval plan · Godavari Finance: loan-file intake · version 1.0

> Engagement folder · Day 14 · Monday 30 November 2026 (week 6) · feeds the week-6 accuracy report at the
> go or no-go (M12, Friday 4 December 2026). Definitions are Day 9's, quoted, not reworded.
> Owners: Lakshmi and the senior analyst (eval owners), the compliance head (completeness labels), the
> Kaagaz FDE (the harness). Changes need the eval owners' agreement and a line in the change log.

## 1. The set

| Item | Value |
|---|---|
| Labelled files | 200: 150 test (the golden set) + 50 development |
| Products | two-wheeler (100 test) and gold (50 test); small-business and personal are out of these 90 days |
| Strata | product, branch (Kukatpally and Guntur over-sampled, 35 each), channel, language, pilot or not, field, handwritten Telugu or not |
| Labellers | Lakshmi and the senior analyst, every file, independently ([labelling guide](godavari-labelling-guide.md)) |
| Adjudication | fields: Srinivas and the Vijayawada team lead; documents, completeness, send-back: the compliance head |
| Truth file | `data/golden/truth-adjudicated.jsonl`, versioned; a reopened label is a new version |
| Where it lives | the machine in the Hyderabad building (D08); Kaagaz sees scores and masked rows only |
| Development split | the only source of few-shot examples and tuning; includes the thirty M05 files |

## 2. What is measured, and the bar

| Metric (Day 9 section C unless marked) | Definition | Bar |
|---|---|---|
| field-level accuracy | share of mandatory fields where the extracted value equals what the eval owners would have typed; handwritten Telugu fields reported separately | 90 to 95 percent or more, with uncertain fields routed to review (R2 below 90) |
| completeness recall | of files truly missing a mandatory document, the share the rules flag | no misses |
| completeness precision | of files the rules flag, the share truly missing something | agreed with the branch managers after the first run |
| confidently wrong (Day 14) | wrong value, no flag on that field | reported per file, every run; must not rise (gate) |
| send-back recall and precision (Day 14) | the analysts' "would send back" against a signed rule raising a problem | reported |
| page classification, documents found (Day 14) | per page and per document, against the labels | reported |
| analysts' own keying error rate | the same accuracy definition applied to the eval owners' labels | a baseline, not a target |
| note pass rate (Day 14) | branch notes passing the five-line rubric, by the calibrated rubric judge | reported; in the gate only while the judge stays calibrated |

Every number carries a 95 percent interval and its count. No stratum is reported without its n.

## 3. Cadence

| When | What | Who sees it |
|---|---|---|
| every pull request touching a prompt, model pin, chunking, retrieval or the envelope | the gate on the test split, stub or recorded responses, about a second | the FDE, the reviewer |
| nightly | the real model on the test split, inside the building | the FDE |
| weekly (Monday) | the report and the confidently-wrong list to the eval owners | Lakshmi, the senior analyst, both team leads |
| M12, Fri 4 Dec | the week-6 accuracy report with the per-file failure list (change C4) | the COO, the compliance head |
| pilot weeks 7 to 10 | analysts' corrections added to the development split weekly; 20 new test files a month from pilot branches | eval owners |
| a new model or model version | the full set, both models, same files; switch only on the gate | the FDE, the eval owners |

## 4. The gate (code/gate_policy.json)

Fails if: overall accuracy is under 90 percent; any incomplete file is not flagged; in any stratum, net
right-to-wrong fields reach 4 with p under 0.01 (paired, exact); or net new confidently-wrong fields exceed 2.
Thresholds sit above the noise floor of the unchanged model re-run on the development split. Measured false
alarms: 0 in 30 unchanged re-runs; the trimmed-prompt regression caught 10 times in 10.

## 5. Risks this plan answers

R1 (handwritten Telugu fields): reported as their own stratum at every run, decided at week 6. R2 (accuracy
below 90 percent): the registered bar is in the gate. C4 (the actual files, not a percentage): the
confidently-wrong report lists every file.

## Change log

| Version | Date | Change | Agreed |
|---|---|---|---|
| 1.0 | Mon 30 Nov 2026 | first issue | Lakshmi, the senior analyst, the Kaagaz FDE; section 2 completeness rows, the compliance head |
