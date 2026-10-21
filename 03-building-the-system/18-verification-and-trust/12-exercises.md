# 12 · Exercises

> Day 18 · Section 12 of 13 · [Chapter overview](README.md) · Previous: [11 · Interview questions](11-interview-questions.md) · Next: [13 · Further reading](13-further-reading.md)

---

Nine exercises in three levels. Exercises marked **(tested)** use the chapter's code, run in the virtual environment on
Python 3.14.3 (October 2026) from the chapter folder; the outputs quoted are real. Learning mode: write the code and
the answers yourself, and use an AI assistant as a tutor or as a sceptical reviewer, not as the author. Try first,
then open the solution.

## Level 1: warm-up

**1.1 Which band?** Using the bands in `data/bands.json`, say where each field lands and why: (a) a printed
applicant name at 0.91 with no finding; (b) a printed PAN at 0.97 where the PAN card and the form disagree; (c) a
handwritten Telugu mobile number at 0.86 with no finding; (d) an on-road price at 0.95 with no finding; (e) a monthly
income the model marked "unsure".

<details><summary>Solution</summary>

(a) auto-accept: the printed name cell accepts at 0.87. (b) review: a deterministic finding (ENV-PAN-MATCH) always
means review, whatever the confidence. (c) review: the handwritten mobile cell is blocked until proved (0 wrong in 68,
upper bound 5.3 percent; proof needs 253). (d) review, and it is the file's forced look: the cell was withdrawn after 6
wrong of 96 on test, and it is on the standing list. (e) reject: key it from the page, or mark "not in the file".

</details>

**1.2 Predict the output (tested).** Without running it, what does `code/exercises/ai_draft_review_page.py` print
for its demo file (GF-40821, on-road price 37150 at confidence 0.93)? What should the screen have done instead?

<details><summary>Solution</summary>

```text
auto_approved
{"V2": 1.2}
```

Every field is "green" (0.93 is above 0.85), so the draft approves the file with nobody looking, and the price
is the misread one from Day 14's list (`Rs I,37,150`). The screen should have shown the source line beside the value,
put the on-road price in review as the forced look, and left the decision to a named analyst (D07). The second line
is the draft's "scorecard" for HR, which ranks the rubber-stamper as the fastest analyst.

</details>

**1.3 Bulk or not?** For each, say whether it may be a bulk action and why: claim 20 files; mark 20 files' branch
notices as printed; approve 20 files with no fields to check; confirm all highlighted names on a file; send back 20
files missing a photograph; export 20 rows to CSV.

<details><summary>Solution</summary>

Bulk: claim, mark notices printed, export (each reversible and decides nothing). Never bulk: approve (D07), confirm
fields (rubber-stamping with a button), send back (each one costs a customer days if wrong; Day 14 found false flags
that were really "check these pages first").

</details>

## Level 2: apply

**2.1 Break it, then fix it: the floor (tested).** In `bands.py`, replace the no-extrapolation line with
`accept_at = t`. Run the tests and the tuner. What fails, and what changes in the band report?

<details><summary>Solution</summary>

```text
FAILED code\tests\test_bands.py::test_no_threshold_extrapolates_below_what_development_showed_correct
  before any withdrawal: 1660 test fields auto-accepted, 10 wrong; pooled upper bound 1.11% against a limit of 1.5%
  WITHDRAWN            date_of_birth | handwritten_telugu: confirmation failed: 1 wrong of 65 auto-accepted test fields
```

Most thresholds fall to 0.70, the bottom of the grid, so values development never saw correct are accepted. One
more wrong value gets through (GF-40155's date of birth at 0.71), and the handwritten date cell is now "withdrawn"
instead of "blocked until proven". The final bands look cheaper (41.1 hours a month instead of 42.6) only because the
test split happened not to contain more such values. Restore the line.

</details>

**2.2 Break it, then fix it: escaping (tested).** In `render.py`, set `autoescape=False`. Which tests fail, and why
does the second one fail?

<details><summary>Solution</summary>

`test_every_value_from_a_document_is_escaped` (the hostile `<script>` is now markup) and
`test_the_pages_load_nothing_from_anywhere`. The second fails because it checks for the CSP in its escaped form
inside the attribute (`default-src &#39;none&#39;`), so it notices that escaping stopped everywhere, not only in values.
Then try the subtler break: keep autoescape on but name the template `file.html.j2` and switch to
`select_autoescape(["html"])`. `test_select_autoescape_does_not_cover_a_dot_j2_template` shows why the escaping would
silently stop.

</details>

**2.3 The flag on the wrong field.** Day 14 found that when the on-road price is misread, the margin rule fires on
the requested amount and the screen highlights the wrong field. Write a function that, for a finding from
`TW-AMT-MARGIN`, returns both fields the rule reads, and make `build_item` put both in review. Write the test first.

<details><summary>Solution sketch</summary>

A table `RULE_READS = {"TW-AMT-MARGIN": ("requested_amount", "on_road_price"), "TW-AMT-RANGE": ("requested_amount",)}`
reviewed with Day 11's owner (it describes Day 11's rules, so it belongs beside them eventually), used when building
`by_field` in `queue.py`. The test builds an item from a pilot file whose margin rule fired and asserts that both
fields carry the finding in `reasons`. Measure on the golden set that no confidently-wrong price remains outside
review even if the standing list is emptied.

</details>

**2.4 Quote the row, not the table.** Clause 4.2 of GFL/CO/2025/027 is a table. Change `citations.clause_text` so
that for a table clause it returns the header and the row for the applicant's type (salaried or self-employed, from
the form's "Occupation" line), using Day 15's `Table.rows`. What should happen if the type cannot be read?

<details><summary>Solution sketch</summary>

Pass the applicant type into `cite()`; find the row whose first cell matches; return `header: row` joined. If the type
is unreadable, show the whole table and say so; never guess a row, for the same reason the screen never guesses a
value.

</details>

## Level 3: challenging

**3.1 Review this AI-written work.** `code/exercises/ai_draft_review_page.py` was written by an agent from the prompt
"build a review screen and auto-approval for the loan files". List at least fourteen problems, in the code and in
what it decides on Godavari's behalf, and say which test or rule in this chapter catches each.

<details><summary>Solution</summary>

1. The threshold is "tuned for best accuracy on all 200 labelled files": the test split is used for tuning (03.2).
2. `tune()` picks the threshold by pooled accuracy, hiding the on-road price (03.3).
3. One global threshold for every field and stratum (03.2).
4. The handwritten Telugu condition is ignored (03.3).
5. Values are put into HTML with f-strings: no escaping (05.6).
6. The page loads Bootstrap, a Google font and an `htmx` script from the internet (05.6).
7. The band is a background colour only (WCAG 1.4.1; 05.4).
8. Confidence is shown as a percentage and is the only thing shown; no source, no rule, no clause (02).
9. The applicant's full name is put in the page heading for anyone who opens the page, with no view log (07.3).
10. "Approve all green files": a bulk approval (05.3; D07).
11. `route()` auto-approves files whose fields are all green (D07; the auditor's condition).
12. `correct()` overwrites the value with no original, no reason and no analyst (06.1).
13. The queue is sorted by lowest confidence only: old, confident files starve, and nothing explains the order (05.2).
14. `analyst_scorecard()` ranks people by speed and sends it to HR (04.4, 04.5).
15. `citation_for()` picks the "most similar circular" by word overlap: it will cite a superseded one (02.4).
16. No spot checks of accepted values, no forced look, no sign-off check, no Telugu labels, no tests.

</details>

**3.2 The M12 paragraph.** Write the paragraph for the COO's go or no-go pack on Friday 4 December: what the analysts
will see on Monday, what it costs in analyst hours, what risk it removes, and what is not yet proved. Use only numbers
from `data/band-report.md` and `data/pilot-week-1/pilot-week-report.md`. At most 150 words.

<details><summary>A model answer</summary>

"On Monday the analysts see every extracted field beside the line of the document it came from. About half of all fields
(three in four on printed pages) need no action; the rest are highlighted for a check, and on every file the on-road price must
be looked at first, because it was misread six times in our 150-file test. On the test files this leaves no wrong
value unhighlighted, against seven with the old settings, for about 12 more analyst hours a month (roughly 5,500
rupees). Handwritten Telugu fields stay fully checked until they prove themselves on 253 fields. Not yet proved: the
real minutes per field (the screen's timer measures them in week one) and the error rate of accepted fields, which
spot checks will bound over about six weeks."

</details>
