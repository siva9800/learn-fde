# 06 · Deterministic Checks and LLM Judges: When a Judge Is Acceptable, and How It Earns Its Place

> Day 14 · Section 6 of 16 · [Chapter overview](README.md) · Previous: [05 · Numbers you can defend](05-numbers-you-can-defend.md) · Next: [07 · The regression gate](07-the-regression-gate.md)

---

## 6.1 Check with code first

An **LLM-as-judge** is a model asked to grade another model's output ("is this note good? pass or fail"). It is
the most over-used tool in evals in 2026, because it is easy to write and it always returns an answer. Before
reaching for one, ask the question Day 11 asked of every rule: **can code decide this?**

In Godavari's system almost everything can:

| Output | Who grades it | Why |
|---|---|---|
| a field value | code: the normaliser against the label | there is one right answer per field, typed by the analyst |
| a page type, a document present | code: against the label | the same |
| completeness, send-back | code: against the compliance head's labels | the same |
| "the note cites every rule that fired" | code: the rule ids are known, search the text | the findings are code's own output |
| "the note invents no document" | code: compare document names in the note with the findings | a list membership question |
| "the note contains no full PAN, Aadhaar or mobile" | code: regular expressions | a format question |
| "the note is plain enough for a branch clerk" | **a judge, calibrated against people** | a judgement; no regex knows what a clerk understands |

Out of seven questions, one needs a judge. That proportion is typical of extraction and workflow systems, and it is
the first lesson: **a judge is for the residue that code cannot check, not for the whole output.** Day 11's rule
applies to evals as much as to the product: put hard checks in code that runs the same way every time.

## 6.2 When a judge is acceptable

A judge earns a place when all four hold:

1. **The output is open-ended**: a note, a summary, an explanation, an answer to a question. (Godavari's branch
   notes now; the capstone's discharge summaries on Day 42.)
2. **The criterion is a judgement code cannot make**: plain language, tone, whether an explanation would satisfy a
   branch manager, whether a summary omits something clinically important.
3. **People cannot read everything**: at 1,400 files a month, nobody reads every note; a judge can, and people read
   a sample.
4. **It has been calibrated against people on held-out examples and passes a written bar**, and is re-calibrated
   whenever the judge model, its prompt or the rubric changes.

The fourth is the one teams skip. A judge that has not been calibrated is a second unverified model, and you are now
evaluating one guess with another.

## 6.3 The rubric: binary, written, with critiques

The note Day 11's model writes to the branch explains what code has already decided. The rubric for it is five
lines, written with Lakshmi and the senior analyst (`RUBRIC` in `code/evals/judge.py`):

```text
A note to the branch passes only if all five hold:
  1. covers every problem code found (nothing dropped);
  2. invents nothing (no document or problem the findings do not contain);
  3. cites the rule for every item, as "(rule TW-DOC-05)";
  4. contains no full PAN, Aadhaar or mobile number;
  5. is plain enough for a branch clerk (no bare codes like "TW-DOC-05: FAIL").
```

Three design choices follow published practice (Hamel Husain's guide, section 16):

- **Pass or fail, not 1 to 10.** Nobody can say what separates a 6 from a 7, and a score invites averaging, which
  hides the failures. A failed note is a failed note.
- **One principal expert's standard.** The rubric is the eval owners', not the FDE's.
- **A one-line critique with every human judgement**, so that disagreements can be read and the critiques can later
  become the judge's few-shot examples (from the development split only).

Lakshmi and the senior analyst rated 300 notes this way: for every golden file with a branch-facing finding, the
note from Day 11's `stub-model-v1`, plus two from a second, chattier writer (`note-writer-b`) that sometimes drops a
finding, invents a document, pastes a PAN, writes a bare rule code or forgets a citation. Disagreements went to the
Vijayawada team lead. The 75 notes from development files are the **calibration set**; the 225 from test files are
**held out**.

## 6.4 Judge v1: holistic, and wrong in the ways the literature predicts

The first judge does what most teams write first: "Rate this note to the branch from 1 to 10." It is a toy, a
deterministic simulation, but it carries the three biases Zheng and colleagues measured in the MT-Bench study
(section 16): it likes longer answers (**verbosity bias**), it likes writing in its own style (**self-enhancement
bias**, here because it is from the same model family as `stub-model-v1`), and it misses specific defects it was not
asked to look for. Its pass threshold was chosen on the calibration notes to maximise agreement with people (score
of 6.0 or more).

The real output (`code/run_judge.py`):

```text
judge                  split    n   agree  kappa  catches fails  passes passes  probe own  probe other  judge right
judge-v1 (holistic)      dev   75   89.3%   0.71          66.7%          98.1%       100%          50%            0
judge-v1 (holistic)     test  225   79.1%   0.38          34.9%          96.3%       100%          75%            0
```

Read it the way you would read it to the eval owners.

- **79 percent agreement sounds acceptable. It is not.** On the held-out notes the judge passes 96 percent of the
  notes people passed, which is easy because most notes are fine, and **catches only 35 percent of the notes people
  failed**. Agreement is dominated by the easy majority. That is why the report shows the two rates separately
  ("catches fails" is the true positive rate on failures; "passes passes" the true negative rate), as Hamel's guide
  recommends for exactly this reason.
- **It looked better on the data it was tuned on.** Kappa 0.71 on the 75 calibration notes, 0.38 on the 225 held-out
  notes. A threshold picked to fit a small set fits that set's accidents. Only the held-out number counts.
- **It prefers its own family.** The probe compares notes with the same single defect (a missing citation) from the
  two writers: the judge passes 100 percent of its own family's and 75 percent of the other writer's. Same defect,
  different verdict. Run it on its own model's output and it will tell you the model is better than it is.

The script prints two of the 41 held-out notes people failed and v1 passed. One:

```text
  GF-40109-v1 (stub-model-v1; really: no_citation)
    | GF-40109: 4 point(s) before this file can move.
    | 1. Recent photograph of the applicant: not in the file (rule TW-DOC-02).
    | 2. Income proof: salary slip, ITR or income declaration: not in the file (rule TW-DOC-06).
    | 3. Utility bill is 120 days old on the application date; the limit is 60 (rule TW-ADDR-AGE).
    | 4. An unmasked Aadhaar number is visible on page(s) 4; the copy must be masked to the last four digits before the file is held.
    judge v2: rule 3: TW-KYC-MASK not cited
```

It reads well. Item 4 has no rule citation. A branch manager who disputes the masking requirement has nothing to
point to, and the compliance head's rule "every send-back cites its rule" is broken. A holistic judge reading for
overall quality does not see it. Code does, instantly.

## 6.5 Judge v2: the rubric split in two

The second judge is not a better prompt. It is a different design: **code checks rules 1 to 4, and the judge model
is asked only rule 5**, "is this plain enough for a branch clerk?", the one question code cannot answer.

```python
def judge_v2(note: Note) -> tuple[bool, list[str]]:
    """Rubric judge: code checks rules 1 to 4; the judge model answers only rule 5 (plain language)."""
    reasons: list[str] = []
    for rule_id, msg in note.findings:
        if rule_id not in text and _cap(msg)[:30] not in text:
            reasons.append(f"rule 1: {rule_id} not covered")
        elif f"(rule {rule_id})" not in text:
            reasons.append(f"rule 3: {rule_id} not cited")
    ... rule 2: documents named in the note that no finding mentions
    ... rule 4: PAN, Aadhaar, mobile patterns
    ... rule 5: the judge model (simulated here) reads for bare codes
    return not reasons, reasons
```

```text
judge-v2 (rubric)        dev   75  100.0%   1.00         100.0%         100.0%         0%           0%            0
judge-v2 (rubric)       test  225   96.9%   0.93         100.0%          95.7%         0%           0%            0

judge-v1 (holistic): advisory only, not in the gate (needs held-out kappa >= 0.80 and catches >= 90 percent of the notes people failed)
judge-v2 (rubric): TRUSTED in the gate (needs held-out kappa >= 0.80 and catches >= 90 percent of the notes people failed)
```

It catches every note people failed. It passes 95.7 percent of the notes people passed; the other 4.3 percent are
its clarity judgement flagging a note that was fine, a false alarm that costs a reviewer a glance. Its probes are
zero, because neither the code nor the narrowed question cares who wrote the note.

**Why it can score above the people's own agreement.** Lakshmi and the senior analyst agree with each other at a
kappa of 0.89 on the held-out notes, and judge v2 agrees with the reference at 0.93. That is not a judge beating
people. The reference is the adjudicated label, which is better than either single labeller (it corrects each
person's misses), and most of v2's checks are exact. Compare a judge against the adjudicated label, and use the
people's agreement with each other as a guide to how good a purely judgement-based check can get.

**Why "judge right" is zero.** The last column counts disagreements where the hidden defects say the judge was
right and the people wrong. In this simulation people missed nothing after adjudication; on real data, read every
judge-human disagreement, because some will be the people's miss, and those become better labels.

## 6.6 The calibration procedure, step by step

This is the procedure, whatever the judge:

1. **Write the rubric with the experts**, binary, a handful of criteria, each one checkable on a single note.
2. **Move every criterion code can check into code.** What remains is the judge's job.
3. **Label a calibration set and a held-out set** with the experts, with critiques, adjudicated. Both come from the
   golden set's splits: calibrate on development, report on test.
4. **Tune the judge (prompt, threshold, few-shot critiques) on the calibration set only.**
5. **Report on the held-out set**: agreement, kappa, the rate of failures caught, the rate of passes passed, and any
   bias probe that matters (own family against other writers; long against short; first position against second if
   the judge compares two outputs).
6. **Write the bar down before you look**: here, held-out kappa of at least 0.80 and at least 90 percent of
   failures caught. A judge that misses the bar is advisory: its verdicts are shown, never gated on.
7. **Re-calibrate on any change** to the judge model, its prompt, the rubric, or the writer being judged. A provider's
   silent model update is a change (Day 13's drift).
8. **Expect the criteria to move.** Shankar and colleagues call it **criteria drift**: "users need criteria to grade
   outputs, but grading outputs helps users define criteria." The first hundred notes the eval owners read will
   change the rubric. Version it like the labelling guide.

## 6.7 Never judge a model with itself, unchecked

Anthropic's evaluation guide puts the default plainly: "Generally best practice to use a different model to evaluate
than the model used to generate the evaluated output." Judge v1's probe shows why: same defect, 100 percent passed
for its own family's notes against 75 percent for the other writer's.

A different model is necessary and not sufficient. Different models share training data and habits, and a
different model can have its own bias toward long, polite notes. The protection is the calibration in 6.6, not the
brand on the judge. If the only judge the customer's environment allows is the same model that writes the notes
(an on-prem deployment with one licensed model, Day 21 and Day 40), you can still use it, as long as its held-out
numbers against people pass the bar and the narrowed question is one where its bias has room to do little harm.

## 6.8 Cost and cadence of a judge

A judge is a model call per item: at Godavari's volume, about 1,400 notes a month if every file gets one. Judge v2
asks one short question per note, which is cheap; the holistic judge reads the whole note and the findings and
reasons about everything, which is not. Two practical patterns: run the code checks on every note in production (they
cost nothing) and the model question on a daily sample; and run the full calibrated judge in the golden-set run on
every change to the note prompt, because that is when it can catch a regression before branches see it.

## 6.9 Key takeaways

- Ask "can code decide this?" first; in extraction systems, most quality questions can be decided by code.
- A judge is acceptable for open-ended outputs, on criteria code cannot check, calibrated against people on held-out
  examples, with a written bar.
- Binary rubrics, one principal expert's standard, critiques with every human judgement.
- Report failures caught and passes passed separately; agreement alone is dominated by the easy majority.
- Tune on the calibration split, report on the held-out split, probe for bias, and re-calibrate on every change.
- Never judge a model with itself unchecked; a different model helps, calibration is what makes it safe.
