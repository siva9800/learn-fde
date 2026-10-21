# 12 · Exercises

> Day 13 · Section 12 of 13 · [Chapter overview](README.md) · Previous: [11 · Interview questions](11-interview-questions.md) · Next: [13 · Further reading](13-further-reading.md)

---

Nine exercises in three levels, including one "review this AI-written prompt PR". Solutions are folded under each one.
Exercises marked **(tested)** were run against the chapter's code on Python 3.14.3 with Jinja2 3.1.6 and pytest 9.1.1
(October 2026), and the outputs shown are real. Learning mode: write the code and the reasoning yourself; use an AI
assistant as a tutor or a sceptical reviewer, not as the author. Try first, then open.

## Level 1: warm-up

**1.1 Pick the bump.** For each change to `extraction@2.0.0`, say major, minor or patch, and whether a new release
record is needed: (a) add `tenure_months` to the fields the pipeline expects back; (b) fix a typo in `_role.j2`;
(c) add a gold few-shot example; (d) keep the prompt, move to a newer model snapshot; (e) rename the variable
`page_type` to `doc_type`.

<details><summary>Solution</summary>

(a) Major: the output contract changes, and with it the merge, the scoring and Day 12's schema. (b) Patch, with a full
regression run anyway. (c) Minor: intended behaviour change. (d) No prompt bump, but a **new release**
(`extraction@2.0.0+<new snapshot>`) with its own eval, approval and compliance read. (e) Major: variables are the
interface the pipeline calls. All five get a new release record. (Sections 04.1, 04.3.)

</details>

**1.2 Prompt or code?** Where does each belong: the prompt, signed rule code (Day 11), or reference data? (a) "net
weight is after stones and dirt are deducted"; (b) "gold loans above 5 lakh: LTV at most 75 percent"; (c) "నెలసరి
ఆదాయం means monthly income"; (d) "a two-wheeler file needs the dealer quotation"; (e) today's 22-carat gold rate;
(f) "if you cannot read a digit, return null"; (g) "the annexure beats the form for the co-applicant".

<details><summary>Solution</summary>

Prompt: (a), (c), (f), all reading instructions. Signed code: (b) and (d), rules the compliance head owns. Reference
data: (e), owned by Godavari's treasury. (g) is code versioned with the prompt (`[merge]`): provenance, not policy,
and the model is never asked to choose. The lint fails (b) on "LTV" and "75 percent" but would not catch (d), which is
why a human reads too. (Section 02.3.)

</details>

**1.3 Predict the output.** In the fake, recall falls with distance from the nearest instruction block. If every
co-applicant annexure moved from page 38 to page 20, which way would the co-applicant score move for 1.0.0 (instructions
at the top), 1.1.0 (top and bottom) and 2.0.0 (per page)?

<details><summary>Solution</summary>

1.0.0 improves: page 20 is nearer the top. 1.1.0 gets worse: page 20 is now the furthest point from both blocks, the
bottom of the U. 2.0.0 does not change: each page is its own short call. Real models have different curves, but the
lesson holds: a layout that fixes one position can hurt another, and per-page calls take position out of the problem.
(Sections 06.3, 06.5.)

</details>

## Level 2: apply

**2.1 Break it, then fix it (tested).** In `loader.py`, delete `undefined=StrictUndefined, ` from the `Environment(...)`
call and run the tests. Which tests fail, and what does that tell you about the suite? Then restore it.

<details><summary>Solution</summary>

Real run:

```text
FAILED tests/test_loader.py::test_strict_undefined_catches_a_typo_inside_a_template
1 failed, 46 passed in 14.87s
```

Exactly one test fails, the one written for this purpose; the shipped templates have no typos, so nothing else
notices. StrictUndefined protects you from the *next* edit, and only a test that renders a deliberate typo proves it is
on. Without that test, an agent could remove the setting "to avoid crashes" (exercise 3.1) with every check green.
(Section 03.2.)

</details>

**2.2 Write 2.1.1.** Make a new version that keeps 2.1.0's removal of the few-shot example but restores the glossary
for pages with Telugu text. Gate it against 2.0.0 on the labelled set and on the lab set's Telugu files. Does the trim
still save tokens, and where?

<details><summary>Solution</summary>

Copy `2.1.0/` to `2.1.1/`, set the version, copy the glossary partial back from 2.0.0 and restore its
`{% if telugu %}` include. The lint warning disappears. On the labelled set nothing changes, because no page has Telugu
text. On the Telugu slice monthly income should return to 6 of 6, and the only saving left is the example's few hundred
tokens on Telugu income pages, about one page in forty. Whether that is worth a release is a judgement; the point is
that it is now measured where it applies.

</details>

**2.3 A slice-aware gate.** Make the gate refuse a candidate that regresses on any named slice as well as overall.
Which slices would you name for Godavari on day one?

<details><summary>Solution</summary>

Extend `regress.score(..., only=...)` to accept branch, product, channel and a Telugu flag, score candidate and baseline
per slice, and run `compare_evals` on each pair with the slice name in each problem. Day-one slices: each pilot branch,
each product, handwritten Telugu income, phone photos, files over 30 pages, files with a co-applicant. A slice with
fewer than about five files cannot say much: report it, do not gate on it, and ask Day 14 to fill it. (Section 05.3.)

</details>

**2.4 An alert for "the model stopped saying unsure" (tested).** Write a rule that fires when the unsure rate on an
amount field halves against the release record while correct does not rise. Check it against the drift check.

<details><summary>Solution</summary>

```python
def unsure_collapse(window: dict, record: dict, fields=("requested_amount", "monthly_income", "on_road_price")) -> list[str]:
    hits = []
    for f in fields:
        w, r = window["per_field"].get(f), record["per_field"].get(f)
        if not w or not r or r["unsure"] == 0:
            continue
        if w["unsure"] / w["n"] <= 0.5 * r["unsure"] / r["n"] and w["correct"] / w["n"] <= r["correct"] / r["n"]:
            hits.append(f"{f}: unsure {r['unsure']}/{r['n']} -> {w['unsure']}/{w['n']} with no gain in correct")
    return hits
```

Run against the two release records in `prompts/registry.json` (the pinned snapshot as the record, the new snapshot as
the window):

```text
['requested_amount: unsure 1/12 -> 0/12 with no gain in correct', 'on_road_price: unsure 1/5 -> 0/5 with no gain in correct']
```

It catches what an accuracy chart misses. On live traffic use a window of a day or more; on twelve files one value is
the whole signal. (Section 07.4.)

</details>

**2.5 The compliance head's question.** Reading 2.0.0, she asks: "The glossary says the annual figure must never be used
as monthly income. Isn't that a rule? You told me rules stay in code." Write your two-sentence answer.

<details><summary>Solution</summary>

"It is a reading instruction, not a lending rule: it tells the model which printed number is the monthly one, and
decides nothing about the loan. The eligibility rule that uses the income is the code your team signed, and it runs
after the model answers." (Sections 02.3, 02.4.)

</details>

## Level 3: challenging

**3.1 Review this AI-written prompt pull request.** `worksheet/ai-draft-prompt-pr.md` is the PR a coding agent opened
when asked to improve accuracy and cut tokens. Find at least ten problems, say which check (lint, verify, gate,
reviewer, compliance read) should catch each, and write your review comment.

<details><summary>Solution</summary>

1. **Wrong bump:** "2.0.1, backwards-compatible" adds an output field and changes behaviour: major.
2. **Released version edited in place:** the diff edits `2.0.0/`. `verify` fails; the rollback target is destroyed.
3. **A business rule in the gold variant:** "at most 75 percent ... above Rs 5,00,000" and an `eligible` flag. Lint.
4. **"Best estimate" instead of null:** against "cannot tell over a guess"; turns unsure into confident wrong. Reviewer,
   compliance read, and a gate that counts wrong separately.
5. **Few-shot example from the test split:** `GF-32003` is a labelled file; the example-source test fails and the 98.6
   percent is inflated by it.
6. **Accuracy only:** no wrong rate, no per-field table, no tokens. Not evidence.
7. **The data-not-instructions sentence removed:** the one structural defence Day 41 builds on. Reviewer.
8. **"Stop as soon as every field has a value":** re-creates page 38; the form's "none" fills the field first. Reviewer;
   the page-band table proves it.
9. **The classification prompt moved into an f-string** in `pipeline.py`: unversioned, unreviewed, `page.text` outside
   the wrapper.
10. **StrictUndefined removed:** exercise 2.1's test fails.
11. **Alias pins:** `fake-large-latest`; `add_release` refuses it.
12. **Self-approval:** `approved_by` equals `author`; `approve()` and `verify` refuse.
13. **"Approved on Slack":** not in the registry, and she reads prompts, she does not approve accuracy.
14. **Promoted to pilot in the same PR,** with no gate against the release pinned there.

Review comment, in short: "Please make this a new major version directory; remove the gold policy sentence (it is a
signed rule already); restore the null instruction, the data sentence and StrictUndefined; take the example from the
training split; keep the classification prompt in the package; pin snapshots; show per-field correct and wrong against
2.0.0 plus the Guntur replay. Promotion is a separate PR after a second engineer's approval and the compliance head's
read." (Sections 02 to 07, 09.7.)

</details>

**3.2 Chunked prompting, measured.** Add a `chunked` strategy as version 1.2.0: the 1.1.0 templates over windows of
eight pages, merged in code. Add its row to the page-band table and explain the co-applicant result.

<details><summary>Solution</summary>

Add `strategy = "chunked"` and a `_chunked` function that renders `extract_file` per window of eight pages and keeps
the first non-null answer per field by page number. Position losses shrink (no window is long) and a new failure
appears: the window holding page 1 answers "none", the window holding page 38 answers the name, and "first non-null"
picks "none". "Last non-null" breaks fields where the early page is authoritative. The only correct merge is by page
type, which needs the classifier, which is 2.0.0. Write that conclusion with your run's numbers. (Section 06.4.)

</details>
