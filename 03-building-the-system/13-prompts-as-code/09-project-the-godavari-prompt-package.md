# 09 · Project: The Godavari Prompt Package

> Day 13 · Section 9 of 13 · [Chapter overview](README.md) · Previous: [08 · 2026 patterns and production concerns](08-2026-patterns-and-production-concerns.md) · Next: [10 · Mistakes and debugging](10-mistakes-and-debugging.md)

---

## 9.1 The brief

Week 3 of the engagement, 9 to 13 November 2026. Friday's milestone M07 sends ten real files from PDF to the core
system's test copy (Day 8). Before then, the extraction step needs a prompt package the team can operate:

1. **Versioned templates on disk**: partials, a variant per product (two-wheeler, gold, small-business, personal), a
   template per page type.
2. **A loader and renderer** with typed variables, strict undefined handling and immutable released versions.
3. **A registry file**: per release, the prompt version, model snapshots, eval score, author, approver and compliance
   read; dev, pilot and production pins with history.
4. **A classify-then-extract pipeline** over synthetic 40-page files, showing the single prompt failing on late pages
   and the per-page approach recovering.
5. **A regression check** on a handful of labelled files, gating promotion (Day 14 builds the real eval).
6. **A rollback demonstration** and a drift check.

## 9.2 Files and how to run

| Module in `code/godavari_prompts/` | What |
|---|---|
| `model_port.py` | Day 12's interface (tier, request, response, provider), copied minimally so the package runs alone |
| `synth.py` | 12 three-page samples, 50 lab bundles, 12 labelled Kukatpally files, 20 Guntur replay files |
| `fake_model.py` | the deterministic fake (06.3): two large snapshots and a moving alias |
| `loader.py`, `registry.py`, `gate.py` | typed render and hashes; releases, pins, gates, rollback, `verify`; the field gate |
| `pipeline.py`, `regress.py` | `resolve`, `check_models`, the two strategies, the merge; correct, unsure, wrong per field and by page band |
| `lint.py`, `explain.py`, `cli.py` | the CI lint; the compliance head's document; `versions`, `lint`, `verify`, `status`, `diff`, `explain`, `rollback` |

Everything was run on **Python 3.14.3** with **Jinja2 3.1.6** and **pytest 9.1.1** (October 2026), offline, in a fresh
virtual environment:

```bash
cd code
python -m venv .venv && . .venv/Scripts/activate      # or .venv/bin/activate on Linux and macOS
python -m pip install -r requirements.txt
python -X utf8 run_demo.py                            # about 7 seconds
python -X utf8 -m pytest -q                           # 47 passed, about 3 to 16 seconds
python -X utf8 -m godavari_prompts.cli lint
python -X utf8 -m godavari_prompts.cli explain --env pilot --product gold
```

## 9.3 Part A: the package, the loader and the renderer

The layout is in section 02.5 and the template mechanics in section 03. The pipeline's whole contact with a prompt is
three lines:

```python
rel, pv = resolve(registry, "pilot")                          # what pilot pins, hash-checked on load
system, user = pv.render("extract", product=f.product, page_type=page_type,
                         fields=pv.field_defs(names), telugu=telugu, examples=exs, page=view)
answer = _call(provider, rel, f, "extract", Tier.LARGE, system, user, page.number, result)
```

`render` checks every variable against `meta.toml`; `_call` builds Day 12's request with an idempotency key that
includes the `release_id`, and logs the call with it. The CLI's view of the versions:

```text
$ python -X utf8 -m godavari_prompts.cli versions
extraction@1.0.0   whole_file             fde.kaagaz       One prompt reads the whole file and returns every field. Tried against
extraction@1.1.0   whole_file             fde.kaagaz       Same contract as 1.0.0. Repeats the request after the document, so the
extraction@2.0.0   classify_then_extract  fde.kaagaz       Page classification on the small tier, then per-page extraction on the
extraction@2.1.0   classify_then_extract  platform.kaagaz  Same contract as 2.0.0. Removes the Telugu label glossary and the few-
```

## 9.4 Part B: the long-document experiment

The headline table is in section 06.5. Two more pieces of the same run show the failure close up:

```text
extraction@1.0.0 on the 40-page files, per field (n = files that have the field):
  field                  n  correct  unsure  wrong
  applicant_name        50       50       0      0
  applicant_pan         50       50       0      0
  business_name         10       10       0      0
  co_applicant_name     50       43       0      7
  employer_name         10       10       0      0
  monthly_income        50       39       7      4
  net_weight_g          10       10       0      0
  on_road_price         20       12       7      1
  requested_amount      50       46       3      1
  all fields                  90.0%           4.3%

One of them: GF-31006 (two-wheeler, Kukatpally). Page 38 names co-applicant PRASAD ALLURI.
  1.0.0 returned 'none' from page 1 with confidence 0.88: the form, not the annexure.
  2.0.0 returned 'PRASAD ALLURI' from page 38 (page 38 classified 'co_applicant_kyc').
```

Fields on page 1 are perfect; fields from the middle and the back are not, and `co_applicant_name` has no "unsure" at
all: the failure is silent. The 43 of 50 looks respectable only because 34 files have no co-applicant and "none" is
right for them; on the 16 that have one it is 9. Always slice a field by the cases where it is hard.

## 9.5 Part C: release records and the regression check

Each version is scored on the twelve labelled Kukatpally files (part of the thirty that Lakshmi and the senior analyst
labelled in week 2, milestone M05), approved by a second engineer, and promoted to dev. 2.0.0 is rendered for the
compliance head, read, and promoted to pilot:

```text
== 3. Release records: each version scored on the 12 labelled Kukatpally files ==
release                               author          approved by       correct  wrong large tok
extraction@1.0.0+fake-large-2026-10   fde.kaagaz      platform.kaagaz     91.7%   4.2%     11800
extraction@1.1.0+fake-large-2026-10   fde.kaagaz      platform.kaagaz     95.8%   1.4%     11866
extraction@2.0.0+fake-large-2026-10   fde.kaagaz      platform.kaagaz     97.2%   0.0%      2212
pilot pins extraction@2.0.0+fake-large-2026-10; the compliance head read data/what-the-system-is-told-2.0.0-two-wheeler.md (2252 words)
```

The twelve files separate 1.0.0 from the rest and show 2.0.0's zero wrong rate. They cannot show the Telugu result
at all, because none has a Telugu declaration. That is the honest size of a week-2 labelled set, and why this is a
regression check while Day 14's golden set (150 files, sliced by branch, product and language) is the evaluation.

## 9.6 Part D: the pull request, the rollback and the drift check

Sections 05 and 07 walk through these outputs line by line (the diff, the gate, the replay, the rollback, the drift
check). The run ends with the registry:

```text
== 7. The registry file ==
wrote prompts/registry.json: 5 releases, 6 history events; verify: clean
  dev        extraction@2.0.0+fake-large-2026-10
  pilot      extraction@2.0.0+fake-large-2026-10
  production (nothing pinned until the January waves)
```

The fifth release is `extraction@2.0.0+fake-large-2026-11`, the same prompt on the new snapshot, recorded with its
failing score so the next person to try the migration sees why it was refused.

## 9.7 Build it with AI

A coding agent can write most of this package in an afternoon. It is good at the parts that look like other code,
and bad at the parts specific to prompts in a regulated customer.

**Context to give it:** Day 12's `provider.py` (the request and response shapes, tiers, the idempotency key); Day 11's
statement that rules live in signed code; one real-looking 40-page synthetic file with its answer key; the four products
and their traps; the rule that the compliance head reads every release; and this chapter's section 04.3 table as the
release record.

**A strong prompt:**

> Build a Python 3.14 package `godavari_prompts` that stores LLM prompts as versioned Jinja2 template directories
> (`prompts/<id>/<semver>/` with `meta.toml`, templates, partials, `products/<product>.j2` for two-wheeler, gold,
> small-business and personal). Requirements: (1) StrictUndefined and autoescape off; every call's variables declared
> with types in `meta.toml` and checked before render, rejecting missing, mistyped and undeclared variables. (2) A
> SHA-256 content hash per version directory with CRLF normalised; a load with an expected hash refuses edited files.
> (3) A JSON registry of releases keyed by prompt version plus model snapshot, with eval scores per field (correct,
> unsure, wrong), author, approver (never the author), compliance read; dev, pilot and production pins; promotion gates;
> rollback that walks history and refuses when the previous version's files are missing; refusal of model aliases.
> (4) A lint that fails on business-rule language (percentages, rupee thresholds, LTV, approve, reject, eligible,
> mandatory, at least) in any text shown to the model, including field descriptions, and on customer page text rendered
> outside `partials/_untrusted_page.j2`. (5) A pipeline with two strategies, whole-file and classify-then-extract, where
> the merge across pages is a precedence table in code. Use only the request shape in the attached `provider.py`. Write
> pytest tests for every refusal. Do not put any loan rule in a prompt, do not invent model names, and do not choose
> few-shot examples from any evaluation set.

**What the agent typically gets right:** the directory layout, a Jinja2 loader, the JSON registry, semver parsing, a
CLI with argparse, tests for the happy path, the unified diff.

**What it typically gets wrong for this concept (check each):**

| Mistake | How it shows | Fix |
|---|---|---|
| **default `Undefined`** | `Environment(loader=...)` with no `undefined=`; a typo renders as an empty string and every test still passes | `StrictUndefined`, and a test that renders a deliberate typo and expects an error |
| **rules written into the prompt** | the two-wheeler variant says "the amount must not exceed 90 percent of the on-road price"; the gold variant lists the LTV caps "to help the model" | the lint; and a reviewer who knows the rules live in Day 11's signed files |
| **released versions edited in place** | "bumped the version in meta.toml" with the same directory edited, or a shared `partials/` folder across versions | immutable directories, per-version partials, the hash check |
| **the model pinned to an alias** | `model = "...-latest"` or a bare family name in the release record; or the model chosen inside the prompt file | dated snapshots in the release only; `check_models()` at batch start |
| **few-shot examples from the test split** | it picks "a good example" from the labelled set it was given to evaluate against, and the score jumps | examples from the training split only, with a test on the source file ids |
| **page text interpolated anywhere** | `f"Page: {page.text}"` in a template, or `env.from_string(page_text)` | one wrapper partial; the lint |
| **a gate on the overall average** | "accuracy did not drop by more than 2 percent" | per field, wrong counted separately (the drift case) |
| **rollback as `git revert` plus redeploy** | the prompt is loaded at import time | resolve per batch; old files stay on disk |
| **whole-file prompting for long documents** | one big prompt plus "read every page carefully" | classify first; prove it with the page-band table |
| **it agrees with your prompt change** | asked to review 2.1.0, it praises the token saving | ask which files exercise each removed line, and whether the gate's tokens moved |

The two that matter most are the second and the fifth: rules in a prompt look like helpfulness, and examples from the
test split look like a better score.

## 9.8 How do you know it's right?

Whether you or an agent wrote it, check these in order:

1. **The tests pass, and they test refusals.** Real run:

   ```text
   $ python -X utf8 -m pytest -q
   ...............................................                          [100%]
   47 passed in 10.86s
   ```

   Read the names, not just the count (`test_rollback_needs_the_old_files_on_disk`,
   `test_a_rule_hidden_in_a_field_description_is_caught`): a registry's whole job is refusing, so test the refusals.
2. **Break it on purpose.** Edit one sentence in a released partial and run `cli verify`: it must fail. Add "at least
   Rs 15,000" to a product variant and run `cli lint`: it must fail. Delete 2.0.0's directory in a scratch copy and try
   a rollback: it must refuse.
3. **Render and read** every call for one product (`cli explain`). If you would not show it to the compliance head,
   it is not ready.
4. **Check the experiment is fair.** Same files, same fake, only the prompt changes; the fake's randomness is a hash
   of file, field, page and model family, so a prompt change cannot "get lucky".
5. **Slice before you believe, and count wrong separately from unsure.** Averages hid both failures in this chapter;
   a drop in "unsure" with no gain in "correct" is the model guessing.
6. **Reconcile the numbers in the text** with `data/run-report.md` after any change to the generator or the fake.

**Review checklist:**

- [ ] templates use StrictUndefined, typed variables, per-version partials and a variant per product
- [ ] no business rule in any template or field description; the lint passes with zero errors
- [ ] every page reaches the model through the untrusted-page partial
- [ ] released directories are unchanged (`cli verify` is clean); old versions are on disk
- [ ] every release pins dated snapshots, has a per-field eval, an approver who is not the author, and a compliance read for pilot
- [ ] the runtime resolves the release per batch and stops when the adapter's model differs
- [ ] the idempotency key and every call log carry the release id
- [ ] the long-document result is shown by page band and by hard slice, not only as an average
- [ ] few-shot examples come from the training split and are masked
- [ ] the rollback has been rehearsed and timed, and the alert that triggers it is written down

## 9.9 What goes into the engagement folder

- `prompts/registry.json` and the four version directories, as the record of what ran and why;
- `data/what-the-system-is-told-2.0.0-two-wheeler.md`, with the compliance head's read recorded in the registry;
- `worksheet/incident-note-2026-11-12-extraction-2.1.0.md`, the drill, and the new golden-set slice it asks Day 14 for;
- `worksheet/prompt-change-review-checklist.md`, adopted for every prompt pull request from now on;
- one line for Friday's M07 readout: "Extraction runs `extraction@2.0.0` on a pinned model; every field is read from the
  page it belongs to; a bad prompt change was caught and rolled back in a rehearsal with one command."

## 9.10 Extend it

- Exercises 2.2 (version 2.1.1), 2.3 (a slice-aware gate) and 3.2 (chunked prompting) extend the package directly.
- Add a canary: pilot runs 2.1.0 on one branch's files and 2.0.0 on the other's for a day, and the registry records both.
- Point `model_port` at Day 12's real adapter and run the package against a live model on the masked set, inside the
  boundary the CISO approved. Expect the page-band shape to differ from the fake's; that difference is the finding.
