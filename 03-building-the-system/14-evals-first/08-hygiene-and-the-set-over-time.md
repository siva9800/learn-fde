# 08 · Hygiene and the Set Over Time: No Leaks, No PII Out, Reused as Models Change

> Day 14 · Section 8 of 16 · [Chapter overview](README.md) · Previous: [07 · The regression gate](07-the-regression-gate.md) · Next: [09 · Advanced and 2026 patterns](09-advanced-and-2026-patterns.md)

---

## 8.1 Leakage: when the test is in the textbook

**Leakage** is any path by which the golden set's test files, or their answers, reach the system being measured. A
leaked file scores itself: the model has seen the answer, the number goes up, and it means nothing. Leakage is
rarely deliberate. It happens like this:

| How it leaks | What it looks like | Prevention |
|---|---|---|
| few-shot examples copied from the golden set | the extraction prompt's three examples are the three hardest Guntur files | examples come from the development split only, and the check below scans every prompt |
| a failing file turned into a fixture | "let me add GF-41934 to the prompt's edge cases so it stops failing" | failing test files are reported, never pasted; their kind of failure gets a development-split example |
| tuning while watching test failures | ten prompt edits, each checked against the same 150 files, until the number is good | tune on development; run the test split when the change is ready; count how often you looked (8.2) |
| corrections used for training | pilot corrections include files that are also golden; a fine-tuned model learns them | golden file numbers are excluded from every training or retrieval corpus by a check, not by memory |
| the vendor trains on customer data | the provider's own training includes your prompts and files | the no-training term in the contract (Day 23), and the model gateway (Day 25) |

The harness checks the first four mechanically before it scores anything. `code/evals/hygiene.py` collects the
test split's **strong identifiers** (file numbers, PANs, mobile numbers), scans every prompt template and example
file it can find (Day 12's and Day 13's prompt folders, Day 11's model and adapter code, this chapter's few-shot
file), and refuses to run if any appears. It also checks that no test file is in the development split or in Day
7's 200-file development sample. On every run, the first line of the report is:

```text
hygiene: 46 prompt and example files scanned, 0 test-split values found in them; 0 name or address matches for a person to look at; test files also in dev: 0; also in Day 7's development sample: 0
```

A test plants a golden file's PAN in a fake prompt file and checks it is found
(`test_a_golden_file_planted_in_a_prompt_is_found`).

**Strong and weak identifiers.** The first version of this check also searched for applicant names and addresses,
and it failed on its first run: a development file and a test file belong to two different synthetic customers who
share a name. Real customers share names too (there are many RAVI TEJAs in Guntur). A name match is now a **weak
match**, printed for a person to look at, and only identifiers prove a leak. A check that cries wolf on common
names gets disabled; a check that ignores names misses a pasted example. Two tiers solve both.

## 8.2 Looking is a slow leak

The subtlest leakage is you. Every time you run the test split, read the failing files and change the prompt
because of what you saw, the test split becomes a little more like a development split. Do it fifty times and the
prompt is fitted to those 150 files.

Three habits keep it honest:

- **Develop on the development split.** Run the test split when a change is ready for review, not after every edit.
- **Count the looks.** The gate's report history is a count of how often the test split has informed a change. When
  it passes about 20 releases, retire part of the test split into development and label fresh files from
  production to replace it.
- **Keep a sealed slice.** Twenty to thirty test files that nobody on the Kaagaz side ever reads, scored only at
  milestones (the week-6 go or no-go, the day-90 review). If the sealed slice and the rest disagree, the rest has
  been fitted.

## 8.3 Personal data in real examples

The real golden set is 150 Godavari customers' loan files: names, PANs, masked Aadhaar numbers, addresses, incomes,
bank statements. Everything about handling it follows from three facts already decided:

- **Processing stays in the building** until each written gate in section 8 of the discovery document (decision D08).
  The files, the labels and the harness run on the machine in the Hyderabad building; nothing is copied to a laptop.
- **"Who viewed this file" is logged for seven years** (the CISO's requirement, Day 10). Labelling and adjudication
  are viewing; the labelling tool logs them like the review screen will.
- **No customer PII leaves India, and Kaagaz receives scores, not values** (the labelling guide, section 9).

What leaves the building is the **masked export**: the metrics, and every confidently-wrong row with its strata,
outcome and confidence, but the values masked at the boundary (`hygiene.mask`):

| Field | Inside the building | In the export |
|---|---|---|
| PAN | `ABCPP1234K` | `AB*******K` |
| mobile | `9876543210` | `******3210` |
| applicant name | `RAVI TEJA PASUPULETI` | `R. T. P.` |
| address | `12-4, KPHB Colony, Kukatpally, Hyderabad 500072` | `[address, PIN 500072]` |
| date of birth | `15-03-1986` | `**-**-1986` |
| amounts, dates of documents | unchanged | unchanged (not identifying alone) |

`run_evals.py` scans the export for PAN, Aadhaar and mobile patterns before writing it and refuses if it finds one;
a test does the same. The full confidently-wrong report, with values, stays inside the building, which is where the
eval owners read it.

Two more points, both previews. Masking is not anonymisation: a masked row with a branch, a date and an amount can
sometimes be re-identified by someone with access to the core system, so the export goes to named people, not a
shared drive. And the legal frame (the DPDP Act's purpose limitation, consent, retention, what "nothing leaves India"
means for model choice) belongs to [Day 24](../../04-deploying-into-their-world/24-data-residency-and-indian-law/README.md).
The eval's design here is built so Day 24 can say yes to it.

## 8.4 Reusing the set as models change

OpenAI's FDE practice names the long-term value of an eval set: "As models improve, the evaluation framework provides
a consistent way to measure progress." For Godavari that sentence becomes a procedure, run whenever a new model or
model version is a candidate (a new release from the provider, a cheaper tier, a self-hosted model the CISO prefers):

1. **Same files, same truth-file version, same normaliser, same policy.** Anything else and the comparison means nothing.
2. **Run both models, with the same envelope and rules.** The model is one box (Day 11); the eval measures the system.
3. **Read the field-level, stratum-level comparison, not the headline.** A new model is usually better at some fields
   and worse at others. "Better on gold weights, worse on handwritten names" is a decision the eval owners make.
4. **Read cost and latency in the same report.** Day 12's ledger turns a model switch into rupees per file.
5. **Recalibrate the thresholds.** A new model's confidences mean something different. The trimmed-prompt candidate
   showed what happens when confidence rises and accuracy does not: thresholds set for the old model let more wrong
   values through. Day 18 refits them on the development split before the new model goes anywhere.
6. **Recalibrate any judge** whose model changed (section 06.6).

Done this way, "should we switch to the new model?" stops being a debate about benchmarks and becomes a one-page
report the customer can read.

## 8.5 Growing and refreshing the set

The set is never finished. It grows from three places, all labelled the same way:

- **Pilot corrections** (Day 18: the first pilot week adds forty of them). Each correction is an analyst saying "the
  system said X, the answer is Y" on a real file. They go to the **development split**, where they become examples
  and threshold data. They are not test files: they were chosen by the system's failures, so they over-represent
  what it gets wrong.
- **Fresh test files from production**, about twenty a month from the pilot branches, drawn by the same quotas and
  weights, double-labelled and adjudicated. They keep the test split representative as the branches, scanners and
  customers change.
- **New products and branches.** Small-business loans are out of these 90 days; when they come in, they need their
  own stratum of at least 20 files before the first pilot file.

Old files are never deleted. A file whose label is reopened gets a new truth-file version; a test file retired into
development is marked in the manifest with the date. Every score is quoted with the truth-file version, so the week-6
number and the day-90 number can be compared honestly.

## 8.6 Cost and cadence

The cadence and its costs are in the eval plan (`worksheet/godavari-eval-plan.md`, section 3): the gate on every
pull request in about a second; the real model nightly and before every promotion, about Rs 950 to Rs 1,300 a run;
the report to the eval owners every Monday; the gate's error rates and any judge recalibrated when their inputs
change; twenty fresh test files a month.

Two observations for the COO. Running the eval is cheap; the experts' hours are the cost, and they are paid once
and then in small monthly amounts. And skipping the nightly real-model run to save Rs 1,000 is the most expensive
saving in the engagement: Day 13's 2.1.0 would have reached Guntur's live files.

## 8.7 The eval set is the thing that generalises

Most of what Kaagaz built for Godavari is specific to Godavari. The eval set is different: a masked golden set with
its guide, definitions and per-stratum results turns "customers need better handwritten Telugu" from an anecdote into
a measured gap the next model release can be tested against. The published OpenAI accounts describe the loop:
Klarna's work wrapped "each intent with evaluation sets to enable scaling", and evaluation data "feeds back to
post-training teams". [Day 36](../../06-from-customer-to-product/36-feeding-product-and-research/README.md) owns
spending it; this chapter owns making it good enough to spend.

## 8.8 Key takeaways

- Leakage scores the test with its own answers; check prompts, examples and corpora mechanically before scoring.
- Identifiers prove a leak; names and addresses are weak matches for a person to look at.
- Looking at test failures is a slow leak: develop on development, count the looks, keep a sealed slice.
- Real files stay in the building; the export to the vendor is masked and checked for PII patterns before it is written.
- Reuse the set for every model decision: same files, same version, both models, field-level, with cost, then recalibrate.
- Grow the set from corrections (development) and fresh production files (test); never delete, always version.
- The masked eval set is what generalises back to the product; Day 36 spends it.
