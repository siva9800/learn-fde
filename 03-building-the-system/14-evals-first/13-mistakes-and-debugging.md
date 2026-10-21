# 13 · Common Mistakes and Debugging

> Day 14 · Section 13 of 16 · [Chapter overview](README.md) · Previous: [12 · Build it with AI, and how you know it's right](12-build-with-ai-and-verification.md) · Next: [14 · Interview questions](14-interview-questions.md)

---

Each row is **symptom, likely cause, fix**, with the section that explains it.

## 13.1 Designing and labelling the set

| Symptom | Likely cause | Fix |
|---|---|---|
| The eval says 99 percent and the pilot's first week finds errors daily | the set was drawn from clean files, or from the files the system was developed on | redraw from the hard cases with quotas; new file numbers; development and test split (02.3, 02.5) |
| A branch or a language has a number with an interval from 80 to 100 percent | fewer than about 20 files in that stratum | add files to that stratum before deciding anything about it (02.4) |
| Two labellers agree on 80 percent of fields and you are worried | format differences counted as disagreement | normalise with the registered normaliser first; then look at what is left (03.6) |
| One field's agreement stays under 95 percent after normalising | the labelling guide does not define it | read the disagreements with the labellers; add a rule to the guide; re-label that field (03.2, 03.6) |
| The senior analyst says "those are not my answers" at the readout | the vendor labelled, or her labels were overwritten without a log | customer experts label; adjudication by a written rule with named people; the log (03.1, 03.7) |
| Adjudication takes weeks | no rule for who decides what; every disagreement is a meeting | fields to the two team leads, rules to the compliance head, in writing, before labelling starts (03.7) |
| The same "send-back reason" keeps being argued | it is a rule question disguised as a labelling question | the compliance head decides against the signed rules; a missing rule goes on the rule-gap list (03.7) |
| Labelling ran over and the pilot slipped | the experts' hours were not booked, or were booked at month end | the team leads book them in the analysts' week, never in the last three days of a month (Day 8; 02.2) |

## 13.2 Metrics and reports

| Symptom | Likely cause | Fix |
|---|---|---|
| A model that says "unsure" more often scores lower but the analysts like it more | accuracy computed with abstentions excluded, or confident wrongs not reported | accuracy over all fields; report confidently wrong and unflagged precision beside it (04.3) |
| Normalised accuracy rose after a change; exact did not | the normaliser started forgiving something new | review the normaliser change; it is a metric change, signed like one (04.2, 07.1) |
| Accuracy rose suddenly with no system change | a hard field stopped being scored, or the files changed | the "every mandatory field scored" test; the manifest fingerprint (10.5) |
| The overall number did not move and the Guntur analysts say it is worse | the average hides the stratum | read the per-branch and per-field rows; slice by everything that varies (05.4) |
| Completeness recall is "100 percent" and the compliance head is not reassured | 0 misses in 76 files is not proof of zero | show the interval (about 95 to 100 percent) and the monthly production measure (05.2) |
| Branch managers complain about send-backs the eval says are fine | completeness precision not shown, or document-level flags confused with file-level | report both levels; explain review-first flags (04.5) |
| The confidently-wrong list is long and the model looks bad | some of the "wrong" rows are label errors | read each row starting with the label; re-adjudicate; new truth-file version (03.8, 11.5) |
| The flag pointed at the wrong field (the price was wrong, the amount was flagged) | a rule fired on a relationship between two fields and named only one | envelope change: flag both fields; or flag a numeric quote containing letters (11.5) |

## 13.3 The gate

| Symptom | Likely cause | Fix |
|---|---|---|
| The gate blocks pull requests that changed nothing | thresholds inside the noise floor; too many strata at a loose threshold | measure the noise floor on development; tighten per-stratum tests; rerun `gate_false_alarms.py` (07.4, 07.6) |
| The gate has never failed anything | it checks only the average, or it cannot see the strata | keep a known-bad candidate in CI that must fail (07.6, 10.5) |
| Every honest run looks like a regression | the baseline ratchets to the best score seen | the baseline is main's last accepted run, refreshed only after merge (07.7) |
| A regression was merged and nobody saw it | the prompt and the normaliser changed in the same pull request | measurement changes travel alone (07.1) |
| The gate refuses with "same golden set" | the baseline was scored on another file set or truth-file version | re-baseline on main with the new version, then rerun the candidate (02.7, 07.2) |
| A change that is better overall is blocked on one field | the gate is doing its job | the eval owners decide the trade in writing with the field report; the gate makes it visible (07.7) |
| CI passes but the nightly real-model run fails | CI replays recorded responses; the prompt or model changed | prompt and model changes need a fresh real run before promotion (10.3) |

## 13.4 The code

| Symptom | Likely cause | Fix |
|---|---|---|
| Two runs give different numbers | unseeded randomness, or a dict or set order used to pick examples | seed every `random.Random`; sort before choosing (12.5) |
| `ImportError: Day 11's intake package is not at ...` | the chapter folders are not at their FOLDERS.md paths | clone the whole course; the harness imports Day 11 by path on purpose (11.3) |
| `LabelsChanged: GF-4xxxx: the pages differ` | the synthetic generator (Day 7 or Day 11) changed, or a real file was rescanned | find out why; if intended, a new golden-set version with re-labelling of the changed files (02.7) |
| `REFUSED: the golden set has leaked` | a prompt or example contains a test file's identifier | remove it; take the example from the development split (08.1) |
| `ModuleNotFoundError: No module named 'pytest'` | running the tests on the global Python | activate the chapter's venv and install the pinned requirements (11.3) |

## 13.5 A routine for "the number looks wrong"

When the headline surprises you, in either direction:

1. **Check the set.** Same manifest, same truth-file version, same normaliser as the run you are comparing with?
2. **Check the counts.** Fields and files scored equal the expected totals? Strata add up?
3. **Find the stratum.** Which branch, channel, language or field moved? A surprise is almost always concentrated.
4. **Open five files.** From that stratum, the pages, the truth record, the model's output. Count by hand.
5. **Check the label.** For every confidently-wrong row you open, read the page before blaming the model.
6. **Check what changed.** Prompt, model pin, envelope, rules, normaliser, data. One at a time, through the gate.
7. **Write it down.** The finding, the files, the fix, in the engagement folder, so the next surprise is faster.
