# 10 · Project: The Baseline Measurement Pack and the One-Page Business Case

> Day 9 · Section 10 of 14 · [Chapter overview](README.md) · Previous: [09 · 2026 patterns and production concerns](09-2026-patterns-and-production-concerns.md) · Next: [11 · Mistakes and debugging](11-mistakes-and-debugging.md)

---

## 10.1 The brief

It is discovery week four. Day 4 chose the problem, Day 5 mapped who would believe which number,
Day 6 found the real workflow, Day 7 wrote the metrics into step 2 and generated a synthetic sample,
and Day 8 dated the plan. Before the Day 10 readout you owe the engagement folder three documents and
the code that produced their numbers:

1. a **baseline measurement pack**: the method, the frame, the stratified draw, the results with
   intervals, and what the report could not see;
2. a **one-page business case** for the COO and the CFO, with a floor, a break-even and a sensitivity
   table, reconciled with Kaagaz's side from Day 3;
3. the **pre-registered metric definitions**, ready for the COO's and the compliance head's signatures.

The files are listed in the [chapter overview](README.md#files). The script is [`code/baseline_and_case.py`](code/baseline_and_case.py); the three documents are in `worksheet/`.

Run on **Python 3.14.3** (October 2026), standard library only, from the chapter folder, in about half
a second. It needs Day 7's folder beside it, because it imports Day 7's generator rather than copying it:

```bash
python -X utf8 code/baseline_and_case.py
```

## 10.2 How the script reuses Day 7

The script loads Day 7's `inputs_inventory.py` by path with `importlib`, registers it in `sys.modules`
(its dataclasses need their module to be findable), and calls `make_loan_files(700, ...)` with Day 7's
own seed. The generator draws files in order from one seeded stream, so the first 200 frame rows are
exactly Day 7's sample; the script checks this against Day 7's CSV on every run. Day 7's files carry a
total turnaround and total hours; `hand_count()` simulates how they split (four timestamps, four
activities) and the outcome, with its own seed, so the parts always add up to the totals. In an
engagement that function is replaced by a reader for the filled form (section 03.6).

## 10.3 The run

```text
== 1. The sampling frame ==
700 new files received in the two-week window (Day 7's generator, seed 7)
first 200 frame rows identical to Day 7's sample: yes

== 2. The stratified draw ==
strata: 24 (6 branch clusters x 4 products); sample 120; at least 2 per stratum; seed 9
frame / sampled              two-wheeler            gold  small-business        personal
Dilsukhnagar                     51 / 9          39 / 7          23 / 4          21 / 3
Guntur                           43 / 7          27 / 5          20 / 3          12 / 2
Kukatpally                       48 / 8          29 / 5          22 / 4          19 / 3
Rajahmundry                      39 / 7          30 / 5          21 / 4          17 / 3
Vijayawada-Benz Circle           53 / 9          25 / 4          28 / 5          18 / 3
Warangal                         40 / 7          29 / 5          28 / 5          18 / 3

== 3. The baseline against the ops report (95 percent intervals) ==
metric                       ops report  hand count        interval   report inside?
median turnaround, days             9.2         9.1      8.7 to 9.7   yes
analyst hours per file              4.5         4.6      4.5 to 4.7   yes
send-back rate                      31%         28%      21% to 35%   yes

What the report never had (hand count only):
  addressable hours per file             1.59   (1.52 to 1.66)
  decided with a document missing        4.1%   (0.9% to 7.2%)
  withdrawn by the customer             10.1%   (5.2% to 14.9%)
  recall of today's human check           87%   (incomplete files that were sent back)
  approval rate among decided files       81%

Where the days go (weighted means, days):
  transit: signed -> on SFTP              1.1   (1.0 to 1.1)
  queue: on SFTP -> first opened          6.4   (6.1 to 6.7)
  work: opened -> decision                1.6   (1.5 to 1.6)
  branch wait (zero if not sent back)     0.9   (0.6 to 1.1)
Where the hours go (weighted means, hours per file):
  re-keying into the core                0.97   (0.93 to 1.00)
  completeness check                     0.35   (0.34 to 0.37)
  chasing the branch                     0.27   (0.21 to 0.33)
  credit assessment and memo             3.01   (2.87 to 3.15)

Why one number is not a baseline yet:
  20 files picked at random            median 8.6 days, interval 8.0 to 11.4
  120 files, stratified                median 9.1 days, interval 8.7 to 9.7
  all 700 files in the frame           send-back rate 30%
  two-wheeler SFTP scans only (n=166)  send-back rate 22%  <- a pilot chosen this way flatters any tool

== 4. Hours into rupees: the loaded cost of one analyst, per year ==
  CTC (includes employer PF and gratuity)         6.00 lakh  counted     the payroll cost of the seat
  benefits outside CTC (medical cover, bonus)     0.45 lakh  counted     paid per head
  seat and facilities (Hyderabad, Vijayawada)     0.75 lakh  counted     a seat not filled is not rented
  IT, laptop, licences                            0.35 lakh  counted     per head
  supervision share (2 leads, half a manager)     1.08 lakh  counted     spans grow with heads
  attrition: hiring and training replacements     0.50 lakh  counted     25% attrition x 2 lakh each
  HQ overhead allocation (finance, HR, board)     0.90 lakh  NOT counted same with 40 or 47 analysts
  the core system and its licence                 0.60 lakh  NOT counted runs whatever the headcount
  loaded 9.13 lakh / 2000 productive hours = 456 rupees an hour (Day 4 placeholder 300; CTC alone gives 300)
  the problem's cost:  16,800 files x 1.59 h x 456 = 1.22 crore a year   (Day 4's question: is it big enough?)
  the system's share at 60% capture: 0.73 crore of capacity   (Day 9's question: how much, and is it cash?)

== 5. The capacity plan: the freed hours are spent once ==
  utilisation today 96.6%; next year's +18% volume needs 7.2 more analysts without the system
  hires made  utilisation  queue days  median days  hires avoided  capacity cash
           0        90.3%         2.1          4.5            7.2      65.7 lakh
           1        88.1%         1.7          4.1            6.2      56.6 lakh
           2        86.0%         1.4          3.8            5.2      47.5 lakh
           3        84.0%         1.2          3.6            4.2      38.3 lakh
           4        82.1%         1.0          3.5            3.2      29.2 lakh
           5        80.3%         0.9          3.4            2.2      20.1 lakh
           6        78.5%         0.8          3.3            1.2      11.0 lakh
           7        76.9%         0.7          3.2            0.2       1.8 lakh
           8        75.3%         0.7          3.2            0.0       0.0 lakh

== 6. The steady-state case (year two onwards; 3 hires made) ==
  benefit  capacity: 4.2 hires not made x 9.13 lakh      38.3 lakh
  benefit  retention: 44.0 loans a month kept x 24,000 x 12    126.6 lakh
  cost     subscription + cloud + staff time               -150.0 lakh
  net a year                                                 15.0 lakh
  one-time: deployment fee + staff time                     -45.0 lakh
  median turnaround 9.1 -> 3.6 days; break-even needs 38.8 loans a month kept (of about 1198 sanctioned)
  operating cost per file next year: 2,174 rupees without the system, 2,737 with it (a speed system, not a cost cutter)
  listed, not added to the headline:
    risk: 4.1% of files decided with a document missing today; expected finding cost 7.5 lakh a year at the invented odds
    disbursement pulled forward: 5.8 crore arrives 5.5 days earlier, once; worth about 0.9 lakh of margin, not every year

== 7. Sensitivity: net a year in lakh, one assumption moved, the rest at base ==
  capture share (Day 14's accuracy)        30% -> -53.0     45% ->  -1.3     60% ->  15.0     70% ->  21.1
  walk-aways kept per day cut               0% ->-111.7      3% -> -48.3      6% ->  15.0      9% ->  78.3
  contribution per loan (rupees)        12,000 -> -48.3  18,000 -> -16.7  24,000 ->  15.0  36,000 ->  78.3
  loaded cost per analyst (lakh)           7.5 ->   8.1     8.5 ->  12.3     9.1 ->  15.0    10.5 ->  20.7
  cloud bill a year (lakh)                  12 ->  29.0      18 ->  23.0      26 ->  15.0      40 ->   1.0
  hires the COO still makes                  0 ->  22.2       2 ->  20.4       3 ->  15.0       5 ->   2.9

Two-way: net a year in lakh, capture share (rows) by walk-aways kept per day cut (columns)
                 0%       3%       6%       9%
       30%   -111.7    -82.3    -53.0    -23.7
       45%   -111.7    -56.5     -1.3     53.9
       60%   -111.7    -48.3     15.0     78.3
       70%   -111.7    -45.3     21.1     87.5

wrote data/godavari_baseline_sample.csv (120 rows) and data/godavari-baseline-and-case.md
```

## 10.4 Reading the run

Section 1 is the reproducibility check. Section 2 shows all 24 strata, the smallest (Guntur personal,
12 files) at the floor of 2. In section 3 the send-back rate came out at 28 percent against the
report's 31; it was not re-drawn, the frame itself has 30, and the interval says 28 is an ordinary
draw. The queue's 6.4 days is the finding that reorganises the plan's story. Sections 4 to 7 are the
money: the loaded rate, the problem's cost beside the captured share, the COO's choice as a table, the
case with its floor and break-even, and the sensitivity tables, in which the walk-away assumption
dominates and the loaded rate barely matters.

## 10.5 Write the three documents

Fill [`worksheet/business-case-template.md`](worksheet/business-case-template.md): pack, case,
definitions, copying numbers from the run with the method beside each; compare with the filled
Godavari files afterwards. Then take the definitions to the compliance head first, the team leads
second and the COO last, because he will ask whether the others agreed.

The pack and the case feed Day 10's discovery document; the definitions feed Day 14 (the accuracy
threshold) and Day 19 (the dashboard); all three are what Day 37 measures against. The script is
rerun at every checkpoint and handed to Bhavani by day 90 (Day 28).

## 10.6 Build it with AI

An agent writes the sampling and bootstrap code well, drafts the page from your numbers, and plays a
sceptical CFO. Its danger is inventing numbers.

**Context to provide:** the baseline pack's results with intervals, the loaded-cost build-up, Day 3's
prices, the capacity plan, every assumption marked measured or assumed, and the rule that no model
name appears on the page. Do not give it the sampled rows: they come from customer files, and the
agent does not need them to draft prose.

**A strong prompt (draft from given numbers only):**

> Draft a one-page business case for a COO and a CFO from the numbers below. Use only these numbers;
> if you need one that is not here, write [MISSING: what, and who owns it] instead of estimating.
> Keep capacity (hours freed) separate from cash (hires not made); never multiply hours by a rate and
> call it savings. Do not annualise one-time effects. Put any benefit whose input is assumed rather
> than measured in a "not counted" block unless I mark it as headline. State the case on measured
> levers alone, then the break-even on the main assumed lever, in words a COO can judge. No model or
> product names. Every number keeps the method I gave it.

**A second prompt (the CFO):**

> You are the CFO of a mid-sized Indian NBFC. Here is a vendor-assisted business case. Name the three
> numbers you trust least and why, anything counted twice, any one-time effect counted as annual,
> and the one assumption you would make the vendor prove before renewal.

**What it gets right:** the one-pager's shape, the sampling and bootstrap code, clean tables.

**What it typically gets wrong for this concept:**

| Mistake | How it shows | Fix |
|---|---|---|
| invents benchmarks | "a 40 percent productivity uplift (industry studies)", "98 percent accuracy" | the [MISSING] rule; delete any number without a source in your pack |
| hours times salary as savings | analyst hours x 300 rupees = "savings" | loaded rate; capacity versus cash; hires not made (05) |
| counts the whole job as automated | all 4.5 hours "freed" | addressable hours only, times a capture share tied to accuracy (05.3, 08.5) |
| annualises a one-time effect | "faster disbursement: 0.57 crore a year" | pulled forward once (06.3) |
| puts the risk line in the headline | "avoided RBI penalty: 2 crore" | an expected value with inputs, listed not added (06.1) |
| leaves out the customer's costs | "infrastructure included", "no additional resources" | cloud in their account, staff time, the learning dip (06.4) |
| agrees with you | asked to review your case, it praises it | the CFO prompt, with "the three numbers you trust least" |

The first two matter most: a confident benchmark nobody at Godavari measured, and hours turned into
savings by multiplication. Both read as competence; both are what a CFO finds first. Exercise 3.1
has the rest.

## 10.7 How do you know it's right?

1. **The frame check prints `yes`**, or Day 7 changed and every quoted number is stale.
2. **The allocation sums to 120, every stratum has at least two, and the weights sum to 700** (699.998
   after rounding).
3. **Every stage split adds up to the turnaround and every hours split to the hours** (the run found
   no mismatches in 120 rows).
4. **Intervals widen when the sample shrinks.** At `SAMPLE_SIZE = 60` hours per file goes from 4.5 to
   4.7 to 4.0 to 4.5 (exercise 2.2 explains what else that run shows).
5. **The consistency column is honest**: set the report's hours to 3.5 and it says `no`.
6. **Capacity is valued only as hires not made; one-time lines stay out of the annual net.**
7. **Sensitivity rows move the right way**: more walk-aways kept, more net; a bigger cloud bill, less.
8. **The ledgers reconcile** with Day 3, and the serving cost is flagged as counted twice.

**Review checklist** (the full pre-send list is in the template):

- [ ] the report's method read; the customer's clock written; withdrawn files included
- [ ] frame, strata, floor and seed recorded; list fixed; no re-draw; second counter on 10 percent
- [ ] every headline number has an interval; no subgroup below what the sample supports
- [ ] loaded rate built line by line; capacity valued only as hires not made; no hour counted twice
- [ ] the customer's staff time, learning dip and cloud bill in the costs; ledgers reconciled
- [ ] the floor, the break-even and the sensitivity on the page; targets as ranges per stakeholder
- [ ] the eval threshold named; definitions in the signature queue

## 10.8 Extend it

- Replace `hand_count()` with a reader for a filled hand-count CSV.
- Add a one-year view with the pilot ramp and the one-time costs; print the payback month.
- Try Neyman allocation (more files where turnaround varies most) and compare interval widths.
