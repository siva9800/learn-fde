# 13 · Common Mistakes and Debugging

> Day 11 · Section 13 of 16 · [Chapter overview](README.md) · Previous: [12 · Build it with AI, and how you know it's right](12-build-with-ai-and-verification.md) · Next: [14 · Interview questions](14-interview-questions.md)

---

Each row is **symptom, cause, fix**, with the section that explains it. The first table is design; the second
is the running system; the third is the prototype's code.

## 13.1 In the design

| Symptom | Likely cause | Fix |
|---|---|---|
| The compliance head asks "which rule rejected this file?" and nobody can answer | the rules are in a prompt; the output has issues but no rule ids | rules as code with ids; every finding carries its rule id into the note and the log (04.4) |
| The architecture diagram has one big "AI" box in the middle | the system was drawn around the model, not around the workflow | eight boxes with the customer's names; the model is one (02.1) |
| Every rule review turns into an argument about edge cases nobody wrote down | the "rules" are unwritten policy being treated as judgement | the yellow box in 4.2: get it written and signed; most send-back judgement was a list (04.2) |
| A rule needs a value the model reads, and you cannot decide which side it goes | a seam treated as one piece of logic | split it: the model reads, code checks and decides; pick the seam pattern (06.1) |
| The design has a human "reviewing everything" as the safety net | review used as the control for errors it will not catch | review is for what code cannot settle; Bhavani's "I would not know" is the evidence (01.2, 02.4) |
| The demo is great and the auditor's first question is unanswerable | model-alone design (pipeline A) shipped as the product | pipeline B: the same demo, with rule ids and versions behind every decision (01.1) |

## 13.2 In the running system

| Symptom | Likely cause | Fix |
|---|---|---|
| Branch managers complain about send-backs for documents they sent | the model missed a page and the completeness rule trusted the label | missing plus unclassified pages goes to review, not to the branch (06.4) |
| A rule fires far more at one branch than the others | that branch is using an old checklist, or a new form layout | check `CHECKLIST_DRIFT` first; then the layout; never loosen the rule to quieten it (10.5) |
| Review queue grows week on week | thresholds are placeholders, or a new channel (phone photos) lowers confidence | measure per-field accuracy on the golden set; set thresholds per field (Days 14, 18) (05.5) |
| Analysts override the same policy rule every day | the rule is wrong for real cases | take the override log to the rule owner; change the rule with a signature, not the button (10.5) |
| A wrong value reaches the core system with high confidence | an OCR misread the model copied faithfully; no cross-check covers that field | add a cross-document check or a reference lookup for that field; list it as a known residual until then (11.6) |
| The run refuses with "rules changed since the sign-off record" after a harmless reformat | the fingerprint changed because the file changed | that is the control working; re-review the sheet diff (it will be empty of rule changes) and update the record; normalise line endings in CI (10.3) |
| The model's notes to the branch sometimes miss what the rules said | the note is free prose with no content check | code checks rule citations and appends missing ones; version the note prompt (06.3) |
| A gold file is blocked that the branch insists is within limits | the branch computed LTV on gross weight, or with the old uniform cap | show the rule sheet line and the arithmetic in the finding message; the message already prints net weight, purity and rate (07.2) |

## 13.3 In the prototype's code

| Symptom | Likely cause | Fix |
|---|---|---|
| `FileNotFoundError: Day 7's generator is not at ...` | the chapter was copied without Day 7's folder | keep the repository layout; the path is fixed by `curriculum/FOLDERS.md` |
| `SignoffError: two-wheeler rules changed since the sign-off record` | you edited a rules file, `validators.py` or `ruleset.py` | that is intended; for your own experiments, regenerate the record's fingerprint and note it is not a real signature |
| `UnicodeEncodeError` on Windows when printing | the console code page cannot print the middle dot or Telugu labels | run with `python -X utf8` |
| Tests pass alone but `test_the_sample_is_day7s_sample_not_a_copy` fails | Day 7's generator or CSV was changed | rerun Day 7's script to regenerate its CSV, or revert the change; the two chapters must share data |
| A new rule never fires in the batch | the rule reads a field name the model does not return | check the field name against `catalogue.py` and `MANDATORY_FIELDS`; a seam contract mismatch (06.6) |
| A new rule fires on every file | it treats `None` (unsure) as a failure of the rule instead of "cannot check" | return REVIEW with "cannot be checked", and only once per missing input (05.7) |
| Changing the stub's error rates changes many numbers in the text | the chapter's prose quotes the run | regenerate the output and update sections 03, 05, 07, 08 and 11 together; the numbers are a set |

## 13.4 A routine for "the system accepted something it should not have"

1. **Find the file's record.** Which ruleset version and fingerprint ran? Which findings were raised? What
   route? Who approved?
2. **Was the rule there?** If no rule covers the case, it is a missing rule: write it, test it, get it signed.
3. **Did the rule run on the right input?** Look at the field or document the rule read. If the model's
   reading was wrong and passed the envelope, the gap is in verification: which cross-check or lookup would
   have caught it?
4. **Did the rule fail open?** If the input was missing or unparseable and the rule passed, fix the rule to
   return REVIEW, and add the test.
5. **Did something bypass the rule?** An override (who, why), or a code path where a model verdict or
   confidence changed the route. The second is a design bug; fix it everywhere, not just here.
6. **Add the file to the golden set** with the correct label (Day 14), so the regression is tested forever.

## 13.5 Key takeaways

- Most design mistakes are rules in the wrong place or unwritten policy treated as judgement.
- Most running-system symptoms point at a seam: a rule trusting a label, a note not checked, a threshold not measured.
- When something gets through, ask in order: was there a rule, did it get the right input, did it fail open,
  did something bypass it.
