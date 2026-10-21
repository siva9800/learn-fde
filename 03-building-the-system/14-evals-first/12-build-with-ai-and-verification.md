# 12 · Build It With AI, and How You Know It's Right

> Day 14 · Section 12 of 16 · [Chapter overview](README.md) · Previous: [11 · Project: the golden set and the harness](11-project-the-golden-set-and-harness.md) · Next: [13 · Mistakes and debugging](13-mistakes-and-debugging.md)

---

A coding agent can write most of this chapter's harness in an afternoon: the dataclasses, the readers and writers,
the Wilson interval, the stratum tables. It will also, unless you stop it, write an eval that flatters the model,
because almost every eval it has seen in training does. This section is about getting the first without the second.

## 12.1 The context to give the agent

Give it the definitions, not your summary of them. Paste or attach:

1. **Day 9's section C, verbatim**: field-level accuracy ("equals what the eval owners would have typed; handwritten
   Telugu fields reported separately; on the held-out part of the golden set"), completeness recall and precision,
   the analysts' own keying error rate.
2. **The labelling guide**, especially 4.1 (full address), 4.2 (PAN only from the PAN card), 4.4 (never convert),
   4.6 (UNREADABLE) and section 8 (the adjudication rule).
3. **Day 11's interfaces and the rule "import, never copy"**: the path to `11-the-system-around-the-model/code`, the
   names it may use (`intake.pipeline.process`, `intake.routing.MANDATORY_FIELDS`, `intake.synth.build_file`, the
   rulesets), and that no rule may be re-implemented in the eval.
4. **The truth file's schema** (one record from `truth-adjudicated.jsonl`) and the manifest's columns.
5. **The strata** and why each exists (pilot branches, handwritten Telugu for R1).
6. **The constraints in writing**: standard library only for the harness; pinned test dependencies; no network; the
   real files never leave the building; Kaagaz's export masked; every random choice seeded.

## 12.2 A strong prompt for building it

> You are helping me build an evaluation harness for a loan-file extraction system. The system already exists in
> another package (path below) and must be imported, never copied or re-implemented. The labels were made by the
> customer's two analysts and adjudicated; the truth file is attached with its schema.
>
> Write a harness that, for each test-split file: verifies the file's page fingerprint against the manifest (refuse
> if it differs); runs `intake.pipeline.process()`; and classifies every mandatory field into exactly one of four
> outcomes: correct, correct-but-flagged, wrong-but-flagged, confidently wrong (wrong and no finding names the field).
> "Correct" uses a registered normaliser that forgives format (Rs and commas, slashes in dates, case, spaces) and
> never content; write its tests as two lists, forgiven and never forgiven, and include monthly-read-as-annual and a
> transliteration variant in the second. "Unsure" is never correct. A value for a field labelled "not in file" is
> wrong.
>
> Report: accuracy over ALL mandatory fields (not only answered ones), exact beside normalised, confidently-wrong
> rate, unflagged precision, completeness recall and precision against the compliance head's labels, each with its
> count and a 95 percent Wilson interval, plus a file-level bootstrap interval for the headline. Report every metric
> for every stratum listed. Write the confidently-wrong cases as a file-by-file table.
>
> Then write a regression gate that compares a candidate run with a stored baseline cell by cell on the same files:
> fail on the registered accuracy floor, any completeness miss, a one-directional paired regression in any stratum
> (exact binomial test on the changed cells), or a rise in confidently-wrong fields. It must refuse to compare runs on
> different files or truth-file versions. Thresholds come from a policy file, not constants.
>
> Do not: compute accuracy only on answered fields; use fuzzy matching on amounts or names; use the golden set's test
> split for anything except scoring; update the baseline to the best score seen; print PAN, Aadhaar, mobile numbers or
> names anywhere except the internal report; use unseeded randomness. Standard library only; type hints; pytest tests
> for every rule above, including a deliberately worse candidate the gate must fail.

## 12.3 A second prompt: attack my eval

Once it is built, use the agent as the sceptic, which is where it is most valuable:

> Here is my eval harness, its policy and one run's report. Do not rewrite anything. Find every way this eval could
> report a number better than the truth: inflated accuracy, hidden strata, leakage from the test split, a normaliser
> that forgives content, labels that came from the model, a gate that cannot fail, a gate that fails on noise, a
> judge that has not been calibrated. For each, say how to demonstrate it with a small change or a planted input, and
> what test would catch it. Cite the line.

The planted-input habit is the one to keep. "This normaliser might forgive content" is an opinion; "here is a pair
(32000, 384000) it calls equal" is a bug.

## 12.4 What the agent usually gets right

The data plumbing (dataclasses, JSON Lines, CSV, argument parsing, report tables); named formulas (Wilson, kappa, an
exact binomial tail), which you still pin to a textbook value; seeding once asked; masking functions once the list of
identifiers is given. Most of the code in `code/evals/` is the kind an agent writes correctly in one pass.

## 12.5 The mistakes it makes on this concept

These are the specific failures to look for, roughly in the order they appear. Exercise 3.1's AI-written harness
(`code/exercises/ai_draft_eval.py`) contains most of them.

| Mistake | What it looks like | Why it matters | Catch it with |
|---|---|---|---|
| **accuracy on answered fields only** | `if value is None: continue` | rewards guessing; a model that never says unsure scores higher | a model that returns None for every field must score 0, not undefined |
| **loose matching** | amounts "within 10 percent", names that "start the same" | calls the twelve-times income or the RAAVI variant correct | the never-forgiven list |
| **confidence as correctness** | `correct if same(...) or confidence > 0.9` | a confident wrong value counts as right: the exact failure the metric exists to find | a hand-made confidently-wrong case must score wrong |
| **few-shot from the golden set** | `build_prompt(rows[:5])` on the scored rows | the test answers are in the prompt | the leakage scan; a planted PAN |
| **unseeded shuffle** | `random.shuffle(rows)` before choosing examples | the leaked examples change every run, and the number with them | run twice, compare |
| **an average-only gate** | `if baseline - result > 0.05: FAIL` | let the trimmed prompt through ten times in ten | the known-bad candidate in CI |
| **a ratcheting baseline** | "keep the best score as the new baseline" | a lucky run becomes the bar; honest runs fail | baseline only from main, after merge |
| **a self-judge, 1 to 10 or yes/no, uncalibrated** | `model.complete("Is this note good?")` with the same model | self-preference and missed defects; no held-out numbers | the calibration procedure; the bias probe |
| **one labeller, or the vendor's labels** | `LABELS = labels-lakshmi.jsonl`; or labels "pre-filled from the model" | one person's slips are truth; or the model grades itself | two labellers, adjudication, the agreement report |
| **re-implementing the rules** | a `check_completeness()` inside the eval | the eval measures its own copy, not the system | import by path; a test that no rules file exists in the eval |
| **PII in logs** | `print(f"{file_id} pan={...}")` | every CI log is a data leak | the PII scan on the export; review prints |
| **rounding as rigour** | `round(correct / total, 4)` on 12 fields | four decimals on a number whose interval is ten points wide | intervals and counts printed beside every share |
| **fields treated as independent** | Wilson on 1,800 cells as the headline | overstates certainty when errors cluster by file | the file-level bootstrap beside it |
| **measurement and system changed together** | one PR edits the prompt and the normaliser | a regression hidden by a kinder metric | the gate's same-set check; measurement changes travel alone |

## 12.6 How do you know it's right?

Whether you wrote the harness or an agent did, these checks tell you whether to trust its numbers. Each one is run
in this chapter, and most are tests.

1. **A known-bad change must fail.** The trimmed-prompt candidate fails the gate on every run
   (`test_the_trimmed_prompt_is_blocked_on_its_field`). If your gate has never failed anything, you do not know that it can.
2. **An unchanged rerun must pass.** Three reruns pass in the tests; 30 of 30 in `gate_false_alarms.py`.
3. **The baseline against itself passes**, and a different file set or truth version is refused.
4. **Hand-made cases for the four outcomes**: seven pairs of value, label and flag with known answers
   (`test_the_four_outcomes`), including "unsure" and "a value for something not in the file".
5. **Mutation of one label.** Change one label in the truth file to something wrong; accuracy must drop by exactly
   one cell (1/1,800) in the right field and stratum, and nowhere else. If it moves elsewhere, something is reading
   the wrong column. (Exercise 2.2.)
6. **Strata add up.** For every stratum family, the counts and the correct cells sum to the overall
   (`test_strata_add_up`). A field silently dropped from scoring breaks this.
7. **The normaliser's two lists.** Every format pair forgiven, every content pair refused.
8. **A planted leak is found**, and a shared name is only a weak match.
9. **Hand-count five files.** Take five test files, open the pages and the truth record, and count the four outcomes
   yourself. Compare with the harness's per-file rows. This is how the "Rs I,37,150" pattern was understood: not from
   the table, from page 10.
10. **Read the confidently-wrong list one row at a time, label first.** One of the seven baseline rows is a label
    error. An eval you have never read row by row will be wrong in ways no test anticipates.
11. **Exact beside normalised.** If normalised accuracy rises after a change and exact does not, the normaliser
    changed what it forgives.
12. **The judge's held-out numbers**, not its calibration-set numbers, and the bias probe.

### Review checklist

Before an eval harness, a golden-set change or a gate policy is merged:

- [ ] Accuracy is over all mandatory fields; "unsure" is not correct; a value for "not in file" is wrong.
- [ ] The normaliser is registered, tested with forgiven and never-forgiven lists, and exact accuracy is reported beside it.
- [ ] Every metric has a count and an interval; the headline has a file-level interval.
- [ ] Every stratum that varies or decides something is reported, each with at least about 20 files.
- [ ] The confidently-wrong cases are listed file by file, and someone has read them, label first.
- [ ] Completeness recall and precision are against the compliance head's labels.
- [ ] Labels come from two of the customer's experts, adjudicated by a written rule; agreement is reported.
- [ ] The test split is used only for scoring; few-shot examples, thresholds and noise floors come from development.
- [ ] The leakage scan ran and found nothing; names are weak matches.
- [ ] The gate compares cell by cell against main's baseline, refuses different sets or truth versions, and fails a
      known-bad candidate; its thresholds sit above a measured noise floor.
- [ ] Any judge in the gate has held-out kappa and failure-catch rates above the written bar, and was not judging its
      own model unchecked.
- [ ] No PII in logs or exports; the export was scanned.
- [ ] Day 11's code is imported, not copied; no rule is re-implemented in the eval.
- [ ] Every random choice is seeded; two runs give the same numbers.
