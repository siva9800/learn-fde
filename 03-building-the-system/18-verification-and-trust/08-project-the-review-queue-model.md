# 08 · Project: The Godavari Review-Queue Model

> Day 18 · Section 8 of 13 · [Chapter overview](README.md) · Previous: [07 · 2026 patterns and production concerns](07-2026-patterns-and-production-concerns.md) · Next: [09 · Build it with AI, and how you know it's right](09-build-with-ai-and-verification.md)

---

## 8.1 The brief

It is Thursday 3 December 2026, week 6. The COO's go or no-go for the pilot is tomorrow (M12), the pilot starts on
Monday (M13), and the team leads have asked one question: "what will my analysts actually see, and how many minutes
will it take?" You owe the engagement folder four things, as working software against synthetic data:

1. a **threshold tuner** that reads Day 14's golden-set results and outputs per-field, per-stratum bands with the
   expected analyst minutes and the residual confidently-wrong count per band;
2. a **review-queue renderer** that turns Day 11's pipeline output into a static, self-contained, escaped HTML page
   per file (evidence beside each field, the rule and version that fired, the clause, the band, the forced-look
   field) and a queue page;
3. a **spot-check sampler** for auto-accepted fields;
4. a **rubber-stamping detector** over a synthetic log of analyst actions;

plus the correction record that feeds Day 14 and Day 19, and a design note for the team leads and the compliance
head.

## 8.2 Setup

Everything was run on **Python 3.14.3** (Windows 11, October 2026; it needs 3.12 or newer). pytest is not on the
global Python, so create a virtual environment with the chapter's pins:

```bash
cd 03-building-the-system/18-verification-and-trust
python -m venv .venv
.venv\Scripts\activate            # Linux and macOS: source .venv/bin/activate
pip install -r code/requirements.txt   # jinja2 3.1.6, markupsafe 3.0.4, pytest 9.1.1 and its pins
python -X utf8 code/tune_thresholds.py
python -X utf8 code/run_pilot_week.py
python -X utf8 -m pytest code
```

Day 11, Day 14 and Day 15 must be at their FOLDERS.md paths; they are imported, never copied, and nothing is written
into their folders. No network, no API key, no model download. Each script takes under a second; the 31 tests take
about one second.

The files are listed in the [chapter overview](README.md#files).

## 8.3 Step 1: the tuner

`tune_thresholds.py` first refuses to run unless Day 11's placeholder thresholds still reproduce Day 14's baseline
(seven confidently wrong fields on the test split); otherwise this chapter would be tuning a different system from
the one Day 14 measured. Then it fits on development, confirms on test and prices three policies. Sections 03.2 to
03.4 read its output line by line; the start and the end:

```text
== Day 18 · bands from the golden set (bands-policy-1.0) ==
field rows: 600 development (50 files), 1800 test (150 files)
check: Day 11's placeholder thresholds on test leave 7 confidently wrong fields (Day 14 measured 7)
...
-- 3. what each policy costs on the 150 test files --
  policy                        auto review key in  wrong, nobody told  wrong, in front of her min/file hours/month
  every field reviewed             0   1742     58                   0                      42     2.91        67.8
  Day 11 placeholder            1408    334     58                   7                      35     1.31        30.5
  bands (this chapter)           971    771     58                   0                      42     1.83        42.6
...
wrote data/bands.json and data/band-report.md in 0.31 s
```

`data/bands.json` holds every cell with its threshold, status, reason, development counts and test counts, so that
anyone can ask "why is the on-road price always highlighted?" and get "confirmation failed: 6 wrong of 96
auto-accepted test fields", with the files.

## 8.4 Step 2: the pilot week

`run_pilot_week.py` builds 60 two-wheeler files from Kukatpally and Guntur (Day 7's generator with seed 18, built by
Day 11's synthesiser, numbered GF-61000 onwards so none can be a golden file), runs each through Day 11's pipeline,
bands its fields, and builds its screen. Its first lines show the sign-off gate doing its job:

```text
== Day 18 · pilot week 1: Kukatpally and Guntur, Monday 7 to Friday 11 December 2026 ==
files: 60 two-wheeler files (Counter({'Kukatpally': 30, 'Guntur': 30})); six analysts; Thursday's batch lands on Friday
pilot mode refuses to build a screen: two-wheeler rules are reviewed-draft; pilot mode runs signed rules only
prototype mode banner: two-wheeler rules v0.3: reviewed-draft (the compliance head, 2026-11-06); fingerprint matches the record
```

The repository stays frozen before M10, so the project runs in prototype mode and every page says "reviewed-draft"
in its banner. That is deliberate: a screen that hid the rules' status would be lying to the analyst.

Then Monday's queue (section 05.2 shows it), the week's bands, what the analysts did (section 06.2), the detector
(section 04.4) and the spot checks:

```text
  the week's fields by band: {'auto_accept': 412, 'review': 283, 'reject': 25}; look-first field: {'on_road_price': 60}
...
-- 4. spot checks after approval --
  files approved with auto-accepted fields: 60; drawn: 6 at random (10% per branch, at least 3) + 3 targeted
  second read (blind; Kukatpally by the senior analyst, Guntur by Lakshmi): 83 fields, 0 disagreements -> team leads: 0 approved values wrong, 0 second-reader slips
  random checks so far: 0 wrong in 47 auto-accepted fields, upper bound 7.6%; to see one error at a true 1 percent with 95 percent probability needs 299 fields, about 6 weeks at this rate

wrote data/pilot-week-1/: queue page and CSV, 12 file pages, action log, corrections, development candidates, this report; 0.50 s
```

The full report is `data/pilot-week-1/pilot-week-report.md`. Open `data/pilot-week-1/queue-2026-12-07.html` in a
browser and follow a link: the file page works offline, with no network requests at all.

## 8.5 What the file page shows

GF-61005, the largest loan on Monday's queue, opens on its forced look (rendered HTML, shown here as text):

```text
1. Look at this first  ముందుగా ఇది చూడండి
   On-road price / ఆన్-రోడ్ ధర     140750     model confidence 0.94: one signal, not the evidence
     3  Vehicle: scooter 110cc
     4  [On-road price: Rs 1,40,750]          page 1, line 4
   Check: confirm or correct / తనిఖీ చేయండి    ( ) Confirm  ( ) Correct  [corrected value]  [reason]
2. Fields to check (8)
   ...
   Residential address: 87-18, Brodipet, Guntur 522002
     address: value 87-18, Brodipet, Guntur 522002 is not what the quote says
     ('చిరునామా / Residential address: 37-18, Brodipet, Guntur 522002')
```

The second field is Day 11's envelope at work: the model's value does not match its own quote, so the field is in
review whatever its confidence, and the reason is printed beside it. V3 corrected it on Monday morning and approved the file
at 12:49; the decision record at the bottom of the page shows both (section 06.4).

## 8.6 The tests

| File | Tests | What they pin down |
|---|---|---|
| `test_bands.py` | 10 | Day 14's baseline reproduced; dev-only fit and test-only confirm; no extrapolation; nothing confidently wrong left; the pooled bound passes while the on-road price fails; thresholds never moved by test; handwritten Telugu blocked; findings and unknown cells fail closed; the cost ordering |
| `test_render_and_citations.py` | 12 | hostile values escaped; nothing loaded, CSP present; the `.j2` autoescape trap; `lang="te"`; a source or a problem for every field; one forced look, first; no bulk approve; pilot mode refuses; queue order; Indian grouping; every rule cites a clause in force, verbatim; superseded circulars refused |
| `test_pilot_tools.py` | 9 | the draw reproducible, keyed and floored; targeted files added; 299 fields; V2 flagged and H3 not; the detector blind to truth; a week of overrides flags nobody; corrections need reasons; format-only is not content; every logged correction has a reason |

```text
...............................                                          [100%]
31 passed in 0.87s
```

## 8.7 The engagement folder, and what to extend

Into the folder: `worksheet/godavari-review-queue-design.md` (the design note with the five decisions to sign before
Monday), `data/band-report.md` and `data/bands.json` for the M12 pack beside Day 14's accuracy report, and
`data/pilot-week-1/` as the rehearsal of what week one will log. To extend it: link a rule's finding to every field it
reads (exercise 2.3), quote the table row rather than the caption (exercise 2.4), and replace the assumed seconds with
the pilot timer's medians and re-price.
