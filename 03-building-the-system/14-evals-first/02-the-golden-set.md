# 02 · The Golden Set: 150 Real Files, Chosen From the Hard Cases, Split So It Stays Honest

> Day 14 · Section 2 of 16 · [Chapter overview](README.md) · Previous: [01 · Why evals first](01-why-evals-first.md) · Next: [03 · Labelling with the customer's experts](03-labelling-with-the-experts.md)

---

## 2.1 What a golden set is, and what it is not

A golden set has four parts, and a set missing any one of them is not golden:

| Part | Godavari's version | What goes wrong without it |
|---|---|---|
| **examples** | 150 real loan files (synthetic in the repository), each the full scanned bundle as it arrived | you measure on whatever was convenient, usually clean files |
| **answers** | every mandatory field, every checklist document, the completeness verdict and the send-back decision, per file | "accuracy" means whatever the person computing it decided that day |
| **people** | Lakshmi and the senior analyst label; Srinivas and the Vijayawada team lead settle fields; the compliance head settles rules | the vendor defines correct, and the customer's sceptic is right not to believe it |
| **a version** | a manifest with a fingerprint of each file's pages, a truth file with a version number, a change log | the set drifts, numbers from different weeks cannot be compared, and nobody notices |

It is not a **benchmark**. Public benchmarks (the leaderboards model vendors publish) tell you how a model does on
somebody else's task. They cannot tell you whether it reads a Guntur branch's phone photo of a handwritten Telugu
income declaration, because no benchmark contains one. The Part 3 plan's Short says it in one line: "150 files
labelled by the customer's best analysts beat any benchmark."

> **Analogy (Telugu audience).** Exam preparation with previous years' question papers and the official answer
> key. A tutor who never tests you is guessing about how you will do. A tutor who tests you on his own made-up
> questions is guessing too, just more confidently. The golden set is last year's real paper, with the answer key
> written by the customer's own toppers, and you are not allowed to see the paper before the exam.

## 2.2 How many: 100 to 200, and why that range

The course uses **100 to 200** examples (the Part 2 plan; [Day 6](../../02-discovery-and-decomposition/06-discovery-interviews/README.md)
captured 180 candidates, Day 8 booked 200). The range is a compromise between two costs.

**Too few, and the numbers wobble.** The uncertainty in a measured share shrinks with the square root of the
number of things measured. Here is what that means for Godavari's set, taken from this chapter's real run (the
intervals are 95 percent Wilson intervals, explained in section 05):

| What is measured | Count | Measured | 95 percent interval | Width |
|---|---|---|---|---|
| all mandatory field cells | 1,800 | 97.5% | 96.7% to 98.1% | 1.4 points |
| one branch (Dilsukhnagar), all fields | 240 | 98.3% | 95.8% to 99.4% | 3.6 points |
| one field (on-road price) | 100 | 92.0% | 85.0% to 95.9% | 10.9 points |
| completeness recall, incomplete files | 76 | 100% | about 95% to 100% | 5 points |

Read the last two rows twice. With 100 two-wheeler files, the on-road price could plausibly be anywhere from 85 to
96 percent accurate. With 76 incomplete files and zero misses, the most you can say is that the true miss rate is
probably under about 5 percent, not that it is zero. That is why the compliance head's "no misses" is checked on
the golden set and then monitored in production every month (Day 9 registered both).

**Too many, and the experts cannot label it.** This chapter's run logged the labelling time of both eval owners:
about 42 minutes a file for Lakshmi and 48 for the senior analyst, 303 analyst hours for 200 files labelled twice,
which is about Rs 1.38 lakh at Day 9's loaded cost of Rs 456 an hour. Day 9 estimated "about 300 hours" before a
single file was labelled; the estimate held. Double it to 400 files and you have taken two of Godavari's best
analysts off the queue for most of a quarter, during the pilot.

**The real constraint is strata, not the total.** A set is big enough when every slice you will make a decision
about has at least about 20 files (so its interval is narrower than the differences you care about) and the
smallest stratum the sponsor will ask about has enough failures to see. Section 2.4 designs to that.

## 2.3 Drawn from the hard cases, deliberately

The most common way to waste a golden set is to fill it with the files that were easiest to get. Day 6's branch
managers offered their worst ("I can give you thirty"; "take the whole month"), and Day 6's manifest drew from
send-backs, Guntur phone photos and handwritten Telugu declarations, the senior analyst's already-decided files,
and only then clean SFTP scans. A set drawn from clean scans "would pass and mean nothing".

This chapter's code does the same thing in a way you can read and rerun (`code/evals/golden.py`):

1. **The pool.** Day 7's generator stands in for Godavari's file store. One call with a new seed and 2,400 files is
   one synthetic month of applications (Day 4's volume). Only the two products with reviewed or signed rules,
   two-wheeler and gold, are eligible. Every file gets a new number in the GF-4xxxx range, so no golden file is one
   of the 200 files Day 7 and Day 11 developed against (a test asserts it).
2. **Quotas per branch and product.** The test split has 100 two-wheeler and 50 gold files. The two pilot
   branches, Kukatpally and Guntur, get 35 files each (24 two-wheeler, 11 gold); the other four branches get 20
   each. The pilot branches are where the system meets real users first, so they need the tightest numbers.
3. **Hard cases weighted up inside each quota.** Phone photos count 2.5 times, mixed channels 1.3, Telugu files
   1.6, mixed-language files 1.2, files that were sent back 1.5. The draw is weighted sampling without replacement
   (each file gets the key u^(1/w) for a random u and weight w, and the top k keys win), seeded, so it is the same
   every time.

The result, from `build_golden_set.py`:

```text
  test by product  gold 50, two-wheeler 100
  test by branch   Dilsukhnagar 20, Guntur 35, Kukatpally 35, Rajahmundry 20, Vijayawada-Benz Circle 20, Warangal 20
  test by channel  mixed 33, phone_photo 48, sftp_scan 69
  test by language english 45, mixed 55, telugu 50
  test files the analysts would send back: 92; incomplete by the checklist: 76
```

Phone photos are 15 percent of Day 7's generator and 32 percent of the golden set. Ninety-two of 150 files would
be sent back, against 28 percent in Day 9's measured baseline. That is the point and also the danger: **a golden
set is not a forecast**. Its overall accuracy is lower than production's will be, by design, because it is full of
hard files. When the COO asks "so what will production look like", the answer is the per-stratum numbers
reweighted by production's real mix, never the golden set's average (section 05.5 shows how).

## 2.4 Stratify by what varies and by what you will decide

A **stratum** is a slice of the set that shares a property: all Guntur files, all phone photos, all handwritten
Telugu fields. You stratify for two reasons, and each picks different slices.

**What varies in production.** If accuracy depends on something, and production's mix of that something will
differ from the set's or will change over time, it is a stratum. For Godavari: product (different documents and
rules), branch (different staff, scanners and customers), channel (SFTP scan, phone photo, mixed), language
(English, Telugu, mixed). Day 19 watches the same four in production.

**What you will decide.** If a decision depends on a slice, the slice must be reported on its own with enough
examples. Godavari has three such decisions written down already: the pilot branches (Kukatpally and Guntur go
live first, so they each need their own number), handwritten Telugu fields (Day 9: "handwritten Telugu fields
reported separately"; Day 10's risk R1 decides at week 6 whether they stay manual), and the product (gold could
slip to the next 90 days under risk R7).

Two practical rules:

- **Report the margins, not every cell.** Six branches times two products times three channels times three
  languages is 108 cells for 150 files; most cells would have one or two files and an interval from 0 to 100
  percent. Report each property on its own (the "margins") and only the crossings a decision needs (pilot branch
  by product, for example).
- **At least about 20 per reported value.** Below that, the interval is wider than any difference worth acting on.
  A test in the chapter (`test_every_reported_stratum_has_enough_files_to_mean_something`) fails the build if any
  reported margin drops under 20 files.

Field-level strata are different from file-level ones. "Handwritten Telugu" is a property of a field's source
page, not of a file: one file can have a handwritten Telugu application form and a printed salary slip. The harness
computes it per field from the page the analyst read it from (496 of 1,800 field cells).

## 2.5 Two splits: development and test

The 200 labelled files are split into **50 development files** and **150 test files**. Only the test files are the
golden set; only they are scored in reports and in the gate.

The development split exists so that the people building the system have labelled examples to look at, tune on and
copy into prompts, without contaminating the measurement. Three things may come from it and nothing else:

- **few-shot examples** in a prompt (Day 13's "examples from the golden set, kept out of the test split");
- **threshold tuning** (Day 18 sets the confidence thresholds; it fits them on development files and confirms on test);
- **the gate's noise floor** (section 07 measures how much an unchanged model wobbles, on development files only).

The thirty files Lakshmi labelled for M05 on 6 November are in the development split, not the test split, because
they were used while building the week-3 skeleton: the engineers have seen them, debugged against them and, in at
least one case, adjusted a prompt because of one. Once you have looked at a file to improve the system, it cannot
measure the system any more. Day 9 registered this as "accuracy on all mandatory fields, on a held-out part of the
golden set", and listed the opposite ("on the golden set the prompts were tuned on") as a known way to game the
number.

The test split is drawn first, from the whole pool; the development split is drawn from what remains. That way the
golden set does not change if someone later decides the development split should be bigger.

## 2.6 Real, masked or synthetic

On the engagement, the golden set is **real files**: they are the only thing that contains Godavari's real scanners,
real handwriting and real customers. Real files never leave the machine in the Hyderabad building (decision D08 in
Day 10) and are never copied to a laptop. The labels are stored by file number; the harness runs where the files are.

**Masked** real files (identifiers replaced consistently) are for anything that must leave: the vendor's
regression suite, a product review (Day 36), a demo; accuracy on them is a proxy, so the official number is always on
real files in place. **Synthetic** files generated by code are for this repository, unit tests and CI; their noise is
the generator's idea of noise and cannot surprise you the way a real Guntur phone photo can. Everything in this
chapter is synthetic, and the stub's error rates are realistic in kind, not calibrated in size (Day 11 said so
first). Day 24 owns the law behind "nothing leaves India"; section 08 covers what it means for the eval.

## 2.7 Version it like code

The golden set changes: new files are added from the pilot, a label is found to be wrong, a product is added. Each
change must be visible, or numbers from different weeks cannot be compared and a regression can hide behind a
quietly edited label. The chapter's set carries three versioning devices:

- **a manifest** (`data/golden/manifest.csv`) listing every file, its split, its strata and a SHA-256 fingerprint of
  its pages. The harness recomputes the fingerprint before scoring and refuses (`LabelsChanged`) if the pages differ
  from the ones the analysts labelled. A rescan, a re-OCR or an accidental edit cannot slip in.
- **a truth file** (`data/golden/truth-adjudicated.jsonl`) that is replaced, never edited, when a label changes; the
  old version stays beside it with its date. Scores are always quoted with the truth-file version.
- **the labelling guide's change log** (`worksheet/godavari-labelling-guide.md`): a rule change in the guide is a
  change to the metric and is signed like one.

The gate (section 07) also refuses to compare a candidate against a baseline scored on a different set of files or
fields, or against a different version of the truth file ("the baseline was scored against a different version of
the truth file; re-baseline first"). Comparing
across versions is the commonest way two honest numbers combine into a dishonest claim.

## 2.8 Key takeaways

- A golden set is examples, answers, the people who own the answers, and a version. Missing any one, it is a sample.
- 100 to 200 examples, sized by the smallest stratum you must decide about (at least about 20), not by the total.
- Draw from the hard cases on purpose, and never read the set's average as a forecast of production.
- Stratify by what varies in production and by what you will decide; report margins, not every cell.
- Split development and test; few-shot examples, thresholds and noise floors come only from development.
- Real files on the engagement, in place; masked for anything that leaves; synthetic for the repository and CI.
- Fingerprint the files, version the truth file, and refuse to compare across versions.
