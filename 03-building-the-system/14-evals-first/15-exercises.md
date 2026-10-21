# 15 · Exercises

> Day 14 · Section 15 of 16 · [Chapter overview](README.md) · Previous: [14 · Interview questions](14-interview-questions.md) · Next: [16 · Further reading](16-further-reading.md)

---

Eleven exercises in three levels, including predict-the-output, break-it-then-fix-it, and "review this AI-written
eval harness and find what is wrong". Solutions are folded under each one. Exercises marked **(tested)** use the
chapter's code, run on Python 3.14.3 in October 2026, and the outputs shown are real. Learning mode: write the code and
do the thinking yourself, and use an AI assistant as a tutor or a sceptic (section 12.3's prompt), not as the author.

## Level 1: warm-up (no code needed)

**1.1 Which outcome?** For each case, give the field's outcome (correct, correct-flagged, wrong-flagged, confidently
wrong). The label is the adjudicated truth.

(a) PAN: model `ABCPP1234K`, label `ABCPP1234K`, confidence 0.97, no finding.
(b) Requested amount: model `1250000`, label `125000`, the amount-range rule fired on it.
(c) Monthly income: model `None` (unsure), label `32000`.
(d) PAN: model `MVPPM5456S` read from the form, label "not in file" (no PAN card), no finding on PAN.
(e) On-road price: model `37150`, label `137150`, confidence 0.93; the margin rule fired, on the requested amount.
(f) Date of birth: model `15/03/1986`, label `15-03-1986`, confidence 0.86, under its 0.90 threshold.
(g) Applicant name: model `GOPI CHAND TADIKONDA`, label `GOPI CHRND TADIKONDA`, no finding.

<details><summary>Solution</summary>

(a) correct. (b) wrong-flagged. (c) wrong-flagged: unsure is never correct, and it is honestly flagged. (d) confidently
wrong: the analyst would not have typed it (guide 4.2), and nothing flagged it. (e) confidently wrong at field level:
the finding names a different field, so the price is not highlighted (section 11.5). (f) correct-flagged: the
normaliser forgives the slashes; the threshold flagged it. (g) confidently wrong by the harness's arithmetic, and the
row to investigate first, because the label looks like the error ("CHRND"); re-adjudicate before blaming the model.

</details>

**1.2 Kappa by hand.** Fifty files. Lakshmi marks 40 complete and 10 incomplete. Of her 40 complete, the senior
analyst marks 36 complete and 4 incomplete; of her 10 incomplete, he marks 2 complete and 8 incomplete. Compute raw
agreement and Cohen's kappa, then say in one sentence what the difference means.

<details><summary>Solution</summary>

Raw agreement: (36 + 8) / 50 = 0.88. Chance agreement: Lakshmi says complete 0.80 of the time, the senior analyst
0.76 (38 of 50); chance = 0.80 x 0.76 + 0.20 x 0.24 = 0.608 + 0.048 = 0.656. Kappa = (0.88 - 0.656) / (1 - 0.656)
= 0.651 (the chapter's `cohen_kappa` returns 0.651). Meaning: 88 percent sounds high, but most of it would happen by
both saying "complete"; on the files that matter, the incomplete ones, they agree on 8 of the 14 either of them
flagged, which is a guide problem to fix before labelling more.

</details>

## Level 2: the code

**2.1 Predict the output (tested).** Without running anything, write down what each line prints. Then run it from the
chapter's `code/` folder with `python -X utf8 -c "..."`.

```python
from evals.stats import wilson, paired_worse_p
from evals.normalise import normalise, norm_equal
print([round(x, 3) for x in wilson(0, 30)], [round(x, 3) for x in wilson(30, 30)])
print(round(paired_worse_p(6, 1), 4), round(paired_worse_p(4, 0), 4))
print(normalise("requested_amount", "Rs 1,25,000.50"), normalise("date_of_birth", "5/3/1986"))
print(norm_equal("applicant_name", "P. Ravi", "P RAVI"), normalise("monthly_income", "Rs. 32,000/-"))
```

<details><summary>Solution</summary>

```text
[0.0, 0.114] [0.886, 1.0]
0.0625 0.0625
125000 05-03-1986
True Rs. 32,000/-
```

Zero failures in 30 still allows a failure rate up to about 11 percent. Six regressions against one fix and four
against none are equally unconvincing (p = 0.0625), which is why the gate needs a minimum net count and a strict p.
Paise are dropped and dates padded. The last one is a finding: "Rs. 32,000/-" is how many Indian forms write an amount,
and the normaliser does not recognise it, so it returns the text unchanged and the comparison with "32000" fails.
That is a **format** the normaliser should forgive. Exercise 2.5 fixes it.

</details>

**2.2 Break it and predict (tested).** Copy `data/golden/truth-adjudicated.jsonl` to a scratch folder. In the copy,
change GF-40030's `dealer_code` from `DLR-VJB-035` to `DLR-VJB-053`. Before running anything, predict exactly which
numbers in the baseline report change and by how much. Then point the harness at the copy (call `harness.run` with
`load_truth(your_copy)`), and compare.

<details><summary>Solution</summary>

Prediction: one cell moves from correct to wrong, in field `dealer_code`, and in every stratum that file belongs to:
product two-wheeler, branch Vijayawada-Benz Circle, channel sftp_scan, language mixed, pilot "other", and handwritten
Telugu "no" (the dealer quotation is printed). Overall 1755 to 1754 correct of 1800. No finding names `dealer_code`
on that file (the model's code is empanelled for the branch), so confidently wrong rises from 7 to 8. The run:

```text
before: DLR-VJB-035
overall correct 1755 -> 1754 ; cw 7 -> 8
  product=two-wheeler: 97.1% -> 97.0%
  branch=Vijayawada-Benz Circle: 96.7% -> 96.2%
  channel=sftp_scan: 97.7% -> 97.6%
  language=mixed: 97.4% -> 97.3%
  pilot=other: 97.3% -> 97.2%
  field=dealer_code: 98.0% -> 97.0%
  handwritten_telugu=no: 98.1% -> 98.0%
```

If anything else had moved (another field, another branch), the harness would be reading the wrong column: that is
the bug this mutation exists to find. Do it on a copy held in memory or in a scratch folder; never edit the real
truth file.

</details>

**2.3 The letter guard (tested).** Section 11.5 found six confidently-wrong on-road prices from "Rs I,37,150". Write a
model wrapper that, for numeric fields whose quoted figure contains a letter among its digits, returns "unsure"
instead of dropping the letter. Run it through the harness and the gate against main's baseline. What happens to
accuracy, to confidently wrong, and to the flag rate? Should it merge?

<details><summary>Solution</summary>

The core of one solution:

```python
class LetterGuard:
    """If the quoted figure has a letter among its digits ("Rs I,37,150"), say unsure instead of dropping it."""
    def read(self, bundle):
        out = self.inner.read(bundle)
        fields = dict(out.fields)
        for k in NUMERIC:
            v = fields.get(k)
            if v and v.value and ":" in v.evidence:
                figure = re.sub(r"^Rs\s*", "", v.evidence.split(":", 1)[1].strip())
                if re.search(r"\d", figure) and re.search(r"[A-Za-z]", figure):
                    fields[k] = replace(v, value=None)
        return replace(out, fields=fields)
```

Wrapped in `RunNoise(..., "candidate-1")` and compared with main's baseline, it printed:

```text
accuracy 97.5%; confident wrong 1; flagged 22.0%; on_road_price cw 0
72 checks, 0 failed
  ok   registered bar       all                    accuracy 97.5% against the floor 90%
  ok   completeness recall  all                    100.0% (0 incomplete files not flagged)
  ok   regressions          all                    8 right-to-wrong, 8 wrong-to-right of 1800 fields (+0.0 points lost), p=0.5982
  ok   confident wrong      all                    0 new, 6 resolved (net -6)
  ok   regressions          field=on_road_price    2 right-to-wrong, 1 wrong-to-right of 100 fields (+1.0 points lost), p=0.5000
  ok   confident wrong      field=on_road_price    0 new, 6 resolved (net -6)
```

Accuracy does not move: the six prices are still wrong, but now flagged (unsure), so confidently wrong falls from 7
to 1 (the remaining one is the label error). The flag rate rises by 0.2 points. The two right-to-wrong prices are run
noise, not the guard. Yes, it should merge, and it belongs in Day 11's envelope as a deterministic check rather than
in a model wrapper; the wrapper is how you measure it before asking Day 11's owner for the change.

</details>

**2.4 Re-adjudicate a label (tested in part).** GF-42025's requested amount is labelled 70060; the paper says 70000.
Write the procedure and the code change: who decides, what file changes, what happens to the gate, and what the
baseline must do.

<details><summary>Solution</summary>

Srinivas and the Vijayawada team lead read page 12 and record 70000 with the reason; the adjudication log gets a
row. A new truth file, version 1.1, is written beside 1.0 (never an edit), and the change log says which cell
changed and why. The next gate run refuses, because the stored baseline was scored against 1.0: "the baseline was
scored against a different version of the truth file; re-baseline first" (the refusal is real: the gate's
`truth_sha256` check, and `test_a_different_truth_file_version_cannot_be_compared`). Main is re-baselined against
1.1 in a pull request that changes nothing else; confidently wrong in the baseline falls from 7 to 6. Then candidate
runs resume. The point: a label correction is a measurement change and travels alone.

</details>

**2.5 Fix the normaliser (tested by you).** Make `normalise` forgive the Indian "/-" suffix on amounts ("Rs. 32,000/-"
equals "32000") without forgiving anything else. Add the case to the "forgiven" test list, and add a "never forgiven"
case that your change must not break.

<details><summary>Solution</summary>

In the amount branch, strip a trailing "/-" and an optional "Rs." with its dot before removing commas:
`text = re.sub(r"/-\s*$", "", text)` and change the prefix pattern to `r"(?i)^rs\.?\s*"` (it already allows the
dot). Forgiven: `("monthly_income", "Rs. 32,000/-", "32000")`. Never forgiven, and worth adding now:
`("monthly_income", "Rs. 32,000/-", "320000")`, so that stripping the suffix can never swallow a digit. This is a metric
change: it goes in its own pull request, the eval owners sign it, and the baseline is recomputed.

</details>

## Level 3: judgement and review

**3.1 Review this AI-written eval harness.** `code/exercises/ai_draft_eval.py` was written by an agent asked for "an
eval script that scores the extraction model on our labelled files and fails CI if accuracy drops". It runs and
prints a number. Find at least twelve problems. For each, say what number it would get wrong and how.

<details><summary>Solution</summary>

1. **One labeller's raw labels** (`labels-lakshmi.jsonl`), not the adjudicated truth file: her slips and habits are
   the truth.
2. **No split**: it scores every labelled file, development included.
3. **Few-shot examples from the scored files** (`rows[:FEWSHOT_COUNT]`): the test answers are in the prompt.
4. **Unseeded shuffle** before choosing them: different leaked examples each run, so the number changes run to run.
5. **Examples include file numbers and values**: a PII and leakage problem in every prompt.
6. **`same()` returns True when either side is None**: a model that returns nothing for a field present in the file
   scores as correct; so does a value for a field "not in file".
7. **Anything with digits is equal within 10 percent**: a stray zero is caught, but 32000 against 30000 passes,
   and dates are compared as numbers, so 15-03-1986 equals 16-03-1986.
8. **Names equal on the first six letters**: "RAVI TEJA PASUPULETI" equals "RAVI TEJA KONDAPALLI".
9. **Abstentions skipped** (`if value is None: continue`): accuracy on answered fields only; guessing is rewarded.
10. **Confidence above 0.9 counts as correct** (`or out["confidence"][name] > 0.9`): a confidently wrong value is
    scored right, the exact failure the metric exists to find.
11. **Fields the model did not return are not scored at all**: it loops over `out["fields"]`, not the mandatory list.
12. **No completeness, no confidently-wrong rate, no strata, no intervals**: one number, rounded to four decimals.
13. **PANs printed to the CI log** for every file, model value and label.
14. **A self-judge**: the same model grades its own notes with "good? yes or no", uncalibrated; `"yes" in reply`
    also matches "yes, but it omits the PAN card".
15. **A ratcheting baseline**: any better run overwrites `baseline.json`; a lucky run becomes the bar.
16. **An average-only gate with a 5-point tolerance**: would pass the trimmed prompt (0.5 points) and much worse.
17. **"Whatever is configured today"** as the model: the run does not record which model or prompt it scored.
18. **No fingerprint check**: rescanned or edited files are scored against old labels.

</details>

**3.2 Write the M12 paragraph.** In at most six sentences, for the COO, report this chapter's baseline run as if it
were the real-model run, including R1, R2 and C4. No jargon he would need explained.

<details><summary>Solution</summary>

"On the 150 files Lakshmi and the senior analyst labelled, the system read 97.5 percent of the required fields
correctly (between 96.7 and 98.2 percent allowing for the sample), above the 95 percent level the business case needs.
It did not miss a single missing document in 76 incomplete files. On handwritten Telugu forms it was 96 percent right,
but it asked an analyst to check almost half of those fields, so the time saving in Guntur will be smaller at first.
Seven values were wrong without being flagged; six are one problem with how a printed '1' is read on dealer
quotations, which is fixed this week, and one turned out to be a labelling slip. The list of all seven files is
attached, as the senior analyst asked. We recommend starting the two-branch pilot on Monday."

</details>

**3.3 "We need 100 percent accuracy."** In the client simulation (Day 34 drills it), the COO says: "I cannot put a
system in front of the RBI that is 97.5 percent accurate. It has to be 100." Answer in under a minute.

<details><summary>Solution</summary>

"Agreed that nothing wrong should reach a decision unchecked, and that is how it is designed. Today two of your best
analysts, working carefully, type about 99 percent of fields the same way the truth file does, so 100 percent is not
what the current process achieves either. What we can promise is three things you can audit: every file is decided by
a named analyst; every rule the compliance head signed is applied to every file, and on the golden set it missed no
missing document; and the system says when it is unsure instead of guessing, so the 2.5 percent it gets wrong is
mostly highlighted for the analyst. The number to watch is the seven it got wrong without highlighting, and we report
those to you by file every week."

</details>

**3.4 The capstone's eval plan.** Using `worksheet/golden-set-plan-template.md`, write the first version of the
golden-set plan for Krishna District Hospital's discharge summaries and pre-authorisation forms. Fill every section;
for section 6, say which criteria code can check and which need a judge, and how that judge will be calibrated.

<details><summary>Solution</summary>

There is no single answer; check yours against these questions. Is "correct" defined by named clinical and insurance
experts, two per output, with adjudicators named for clinical and for rule questions? Are the strata the ones that vary or decide something (department, insurer or scheme, language of the notes, typed or handwritten source, length of stay),
each with at least about 20? Are exact outputs (patient identifiers, diagnosis codes, medication names and doses,
insurer, amounts) checked by code against labels, and only free-text qualities (completeness of the clinical course,
patient-readable advice) left to a judge with a binary rubric, calibrated on a development split and reported on a
held-out split? Is the confidently-wrong analogue defined (a wrong dose or diagnosis code with nothing flagged)? Does
nothing identifiable leave the hospital, and is the export masked? Is there a gate, a noise floor, and a known-bad
candidate? Day 42 starts from this plan.

</details>
