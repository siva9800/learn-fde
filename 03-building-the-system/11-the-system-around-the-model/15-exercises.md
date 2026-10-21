# 15 · Exercises

> Day 11 · Section 15 of 16 · [Chapter overview](README.md) · Previous: [14 · Interview questions](14-interview-questions.md) · Next: [16 · Further reading](16-further-reading.md)

---

Twelve exercises in three levels, including two "review this AI-written work and find what is wrong". Solutions
are folded under each one. The exercises marked **(tested)** were run against the chapter's code on Python
3.14.3 (October 2026) and their outputs are real. Learning mode: write the code and the answers yourself; use an
AI assistant as a tutor or a sceptical reviewer, not as the author. Try first, then open.

## Level 1: warm-up

**1.1 Sort the rules.** Put each into regulatory, policy or judgement, and say where it lives.

(a) The applicant's photograph must be in the file. (b) Tenure for a two-wheeler loan is 12 to 48 months.
(c) Is this stamped, half-legible page the dealer quotation? (d) No page may show an unmasked Aadhaar number.
(e) The analyst should check that the address proof "looks genuine". (f) A utility bill used as address proof
is at most 60 days old. (g) Which of two bank statements is the salary account? (h) Gold LTV within the tiered
cap. (i) A branch manager sees only his own branch's files. (j) The note to the branch should be polite and
say what to send first.

<details><summary>Solution</summary>

(a) regulatory, code (TW-DOC-02). (b) policy, code with override (TW-TENURE). (c) judgement (perception), the
model proposes, grounding and the page title check it. (d) regulatory, code, a scan of every page. (e) judgement
that cannot be written as a rule; a review item with the model's evidence, not code pretending to know
"genuine". (f) regulatory as Godavari reads the KYC direction, code (TW-ADDR-AGE). (g) judgement, the model
proposes, code checks the salary credits (seam 1). (h) regulatory, code (GL-LTV). (i) regulatory (the CISO's),
code inside the query, never a prompt. (j) language, the model drafts; code checks it cites the rules (seam 2).
</details>

**1.2 Code or model, in another domain.** A Pune health insurer wants help with cashless pre-authorisation
requests. For each task, say code, model, or a seam (and which pattern): (a) check the policy is active on the
admission date; (b) read the treating doctor's handwritten notes; (c) compute the room-rent cap as 1 percent of
the sum insured per day; (d) decide whether the diagnosis matches a listed exclusion; (e) check the hospital is
in the network; (f) summarise the case for the medical officer; (g) decide to approve.

<details><summary>Solution</summary>

(a) code, a lookup and a date comparison. (b) model, with quotes and pages. (c) code, arithmetic. (d) a seam:
the model extracts the diagnosis and proposes a code (ICD), code matches it against the exclusion list, and a
medical officer reviews disagreements. (e) code, a reference lookup. (f) model, from code's findings. (g) a named
human; the system prepares a complete, checked case. The Day 42 capstone runs the full method on a hospital.
</details>

**1.3 Predict the output (tested).** A gold file has net weight 20.0 g, gross 22.0 g, 22 carat, appraised on
4 November 2026 (published rate Rs 11,404 a gram in the synthetic table), and asks for Rs 1,95,000. What does
GL-LTV return? Work it out by hand before running it.

<details><summary>Solution</summary>

Value = 20.0 x 11,404 x 22/22 = Rs 2,28,080. The amount is under Rs 2,50,000, so the cap is 85 percent:
Rs 1,93,868. Rs 1,95,000 is 85.5 percent, so GL-LTV returns a BLOCK: "requested Rs 195,000 is 85.5 percent of
collateral worth Rs 228,080 (net 20.0 g, 22 carat, Rs 11,404/g); the cap for this amount is 85 percent". The test
`test_amount_exactly_at_the_85_percent_cap_passes_and_one_rupee_over_blocks` uses the same file at Rs 1,93,868
(passes) and Rs 1,93,869 (blocks). Note what would have happened on gross weight: Rs 2,50,888 x 85 percent is
Rs 2,13,254, and the loan would have looked fine.
</details>

**1.4 Predict the route.** A file has these findings: ENV-CONFIDENCE (review) on the date of birth; TW-DOC-11
(send back) for the insurance proposal; TW-AMT-MARGIN (review). What is the route, and what does the branch
hear?

<details><summary>Solution</summary>

`send_back`: the most severe action decides. The branch hears only the branch-facing finding, the missing
insurance proposal with rule TW-DOC-11; the two review findings travel with the file for the analyst. The order
the findings were raised in does not matter (`test_the_most_severe_finding_decides`).
</details>

## Level 2: apply

**2.1 Break it, then fix it (tested).** In `pipeline.envelope`, make it return an empty tuple for the uncertain
pages, so `missing_document` never takes the review path. Run the batch. What changes, and who would notice
first at Godavari? Then restore it.

<details><summary>Solution</summary>

Run on the chapter's code: send-backs rise from 52 to 62 files, and 20 send-back findings in 13 files have no
real problem behind them, for example GF-25040 being asked for a proof of identity it already contains.
`test_no_send_back_or_block_without_a_real_problem` fails. The first person to notice is the branch manager
whose officer is told to resend a document that is in the file, then Srinivas when the manager phones him
(section 2.3). The fix is the seam rule in 6.4.
</details>

**2.2 Close a residual (tested).** GF-25140's date of birth was misread on the form and reached an analyst
unflagged. The PAN card also prints the date of birth. Add an envelope check `ENV-DOB-MATCH` that compares the
form's date of birth with the PAN card's, and run the batch. Write the tests first: one where they agree, one
where they differ, one where the PAN card is missing.

<details><summary>Solution</summary>

A version that reads the PAN card's "Date of Birth" line from the grounded PAN-card page and compares it with
the form's value, raising REVIEW with field `date_of_birth` on a mismatch, fires twice in the batch. GF-25140
moves from `ready_for_approval` to `review`, the date-of-birth miss disappears, and the only remaining miss is
GF-25106's PAN. There are still zero false send-backs (the check raises review, not send-back). Ready files go
from 23 to 22. That is a good trade: one more file for an analyst to look at, one fewer silent error.
</details>

**2.3 Change a signed rule (tested on your machine).** The compliance head decides that an electricity bill in
the spouse's name is acceptable when a marriage certificate is in the file. Implement it in `rules_kyc.py`,
with tests. Then run `run_batch.py`. What happens, and what is the correct next step?

<details><summary>Solution</summary>

The run refuses: "two-wheeler rules changed since the sign-off record; re-review before running" (and the same
for gold, which shares `rules_kyc.py`). That is correct. The next step is not to update the fingerprint yourself:
regenerate the sheets, show the compliance head the sheet diff (one new condition on the alternatives list) and
the new test names, and only after her review update the record's version and fingerprint. Bump the version to
0.4. Notice the change touched both products' fingerprints because the rule is shared; that is the right
behaviour and worth saying in the review.
</details>

**2.4 Effective dates.** Add `effective_from: date` to `RuleSet`, keep two versions of the gold rules (the old
uniform 75 percent cap until 31 March 2026, the tiers from 1 April 2026), and select by the file's application
date. Write a test with one file on each side of the date.

<details><summary>Solution</summary>

A registry of rulesets per product sorted by `effective_from`, and a `select(product, on: date)` that returns
the latest version whose `effective_from` is on or before the date, raising if none. Each version keeps its own
fingerprint and sign-off record. The test builds two hand-made gold files (section `helpers.make_ctx`) with
application dates 31 March and 1 April 2026 and an amount at 80 percent of the collateral under Rs 2.5 lakh: the
first is blocked by the old cap, the second passes the new one. Ask the compliance head which date governs (the
receipt date is the usual answer) and write her answer into the rule's text.
</details>

**2.5 Write the review.** The compliance head sends back the two-wheeler sheet with one comment: "TW-AMT-MARGIN
says 90 percent of the on-road price. Our product note says 85 percent for first-time borrowers." What do you
change, what do you ask, and what do you not do?

<details><summary>Solution</summary>

Ask: how is "first-time borrower" determined (a field on the form, a core-system lookup by PAN)? Is it policy
(overridable) like the 90 percent? From which date? Then add the field to the extraction contract if it is on
the form, or a reference lookup if it is in the core system, change the rule with tests at 85 and 90 percent for
both kinds of borrower, regenerate the sheet and send it back. Do not put "first-time borrowers get 85 percent"
into the prompt, and do not let the model decide who is a first-time borrower from the narrative.
</details>

## Level 3: challenging

**3.1 Review this AI-written code and find what is wrong.** Open
[`code/exercises/ai_draft_completeness.py`](code/exercises/ai_draft_completeness.py). An agent wrote it from the
prompt "write a completeness checker for two-wheeler and gold loan files using the ModelOutput dataclass; keep it
simple and fast", and reported "all edge cases handled". Find at least nine problems, and for each, write the test
that would have caught it.

<details><summary>Solution</summary>

1. `if output.prompt_only.complete: return []`: the model's verdict skips every rule. Test: a file whose
   `prompt_only.complete` is True with a missing PAN card must still produce a finding.
2. Presence is `confidence > 0.5` with no grounding: a hallucinated claim counts as present. Test: a claim whose
   quote is not on its page must not satisfy the checklist.
3. The required lists are incomplete (8 of 14 for two-wheeler, 5 of 9 for gold, no proof of identity for gold, no
   conditional co-applicant KYC) and not taken from the signed rules. Test: count against the signed checklist.
4. `re.match` without an end anchor accepts an 11-character PAN, and the holder letter is not checked. Test:
   "ABCPP1234KX" and "ABCFP1234K" must fail.
5. Any kind containing "bill" is accepted, and the holder is ignored: a gas bill in the father's name passes.
   Test: gas bill, father, must be sent back.
6. The Aadhaar check searches the identity page's evidence (its title line), not the page text, misses the spaced
   "1234 5678 9012" format, has no checksum, and never scans other pages. Test: an unmasked number on a photocopy
   reverse side must block.
7. `round(amount / price * 100) > 90` lets 90.4 percent through, in floating point. Test: 99,450 against
   1,10,000 (90.4 percent) must fire.
8. Dates parsed as `%m-%d-%Y` for dd-mm-yyyy forms; age as `days / 365`. With "02-11-2026" it silently reads
   11 February; with "15-03-1986" it raises. Test: the 21st-birthday boundary.
9. Gold uses gross weight, floats, purity over 24 with a 22-carat rate, a uniform 75 percent cap, and a
   hard-coded rate with no date. Test: net against gross; the tier edges; a date with no published rate.
10. `except Exception: return []` turns every crash (a None date, a missing field) into "no problems". Test: a
    file with no date of birth must produce a review finding, not an empty list.
11. The docstring says "an empty list means the file can go to the core system": no analyst approval anywhere.
12. A `None` amount skips the margin check silently (`if amount and price`). Test: unreadable amount means review.

The pattern across all twelve: each line is a reasonable-looking shortcut that moves a rule from "always" to
"usually", or a failure from loud to silent.
</details>

**3.2 Review this AI-written architecture.** Read
[`worksheet/ai-draft-architecture.md`](worksheet/ai-draft-architecture.md), written by an assistant for the COO.
Find at least twelve problems. For each, name the Godavari finding, constraint or decision it contradicts.

<details><summary>Solution</summary>

| # | Problem in the draft | What it contradicts |
|---|---|---|
| 1 | the agent "makes the completeness decision" | A7: rules as signed code |
| 2 | every rule in a prompt, editable from an admin screen; "policy changes are a prompt edit" | the compliance head's "I sign the change"; section 7.2 |
| 3 | files sent to an OCR service in Singapore | B1: no customer PII leaves India; the CISO's "no internet" for the prototype |
| 4 | "use your judgement on utility bills in a family member's name" | the compliance head's exact refusal; the signed list |
| 5 | gold LTV "75 percent", computed by the agent | the RBI's 2025 tiers; arithmetic left to the model |
| 6 | auto-approval above confidence 0.95 | D07 and A6: a named analyst decides every file |
| 7 | 97 percent from the vendor demo on salary slips | no golden set; fourteen document types, not one (Day 6, the COO) |
| 8 | "self-verification" instead of validation | a model checking itself is not a deterministic check; no grounding |
| 9 | access control as an instruction | A1: AD groups inside the query; an injection target (Day 41) |
| 10 | automatic writes, five retries, no key | A5: no idempotency; five retries can mean five applications |
| 11 | no "unsure" anywhere | A8 and the 2019 pilot |
| 12 | writes ignore the 17:30 to 20:00 window and the tracker | A4 and A2 |
| 13 | "files processed per day" as the only observability | Day 19: traces, cost, rule fire rates |
| 14 | all 300 branches in six weeks | the signed 90-day plan and the two-branch pilot (Day 8) |
| 15 | "accuracy improves automatically" | a model update can also regress; nothing measures it (Day 14) |
</details>

**3.3 Transfer.** Draw the eight boxes for Krishna District Hospital's insurance pre-authorisation (the Day 42
capstone). Put the line between code and model, place the humans, and list five rules you would refuse to put in
a prompt, with the bin for each.

<details><summary>Solution sketch</summary>

Ingestion: discharge summaries and pre-auth forms from the hospital's system. Model: read clinical notes, extract
diagnosis, procedure and dates with quotes; draft the summary for the insurer's medical officer. Rules in code:
policy active on the admission date (lookup, regulatory in the contract sense); sum insured and sub-limits
(arithmetic); waiting-period exclusions from the policy start date (dates); network-hospital check (lookup);
mandatory documents for a pre-auth (completeness). Humans: the hospital's insurance desk (producer), the
insurer's medical officer (decides), the hospital's compliance officer (owns the document rules). The seam:
the model proposes a diagnosis code, code matches it to exclusions, and disagreements go to a person. Day 42
does it in full.
</details>

**3.4 Measure the stub against a real model (optional, needs an API key).** Run
`python -X utf8 code/run_batch.py --model anthropic --limit 20` on the synthetic files. Compare the table in
section 2 of the report with the stub's for the same twenty files. Which rows move, which do not, and why? Write
the paragraph you would put in the week-3 readout.

<details><summary>What to look for</summary>

The rule-breach rows should still show zero misses: the rules do not care which model read the pages, provided
the envelope's checks hold. The "model alone shipped" column and the field-error rows will move, in either
direction, because they measure the model. If a rule-breach row shows a miss, the cause is upstream of the rule
(a field the real model names differently, an attribute it does not return); that is a seam contract problem
(6.6), and the fix is in the adapter or the schema, never in the rule. Twenty synthetic files prove nothing about
accuracy on Godavari's real files; say so in the readout and point to Day 14.
</details>
