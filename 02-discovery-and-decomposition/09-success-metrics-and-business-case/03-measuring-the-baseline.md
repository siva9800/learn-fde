# 03 · Measuring the Baseline by Hand

> Day 9 · Section 3 of 14 · [Chapter overview](README.md) · Previous: [02 · The metric ladder](02-the-metric-ladder.md) · Next: [04 · Confidence intervals in plain words](04-confidence-intervals-in-plain-words.md)

---

## 3.1 Why count by hand when there is a report

Godavari already reports turnaround and send-backs, and Day 4 chose intake partly because it was
"already measured". But a report is a number with a method you have not read. Before building
anything judged against it, you need **what it counts**, **which files it leaves out**, **how much it
would move if counted again** and **what it cannot see**. A two-week hand count answers all four
before the system touches a file; afterwards the baseline can never be measured again. That is why
Day 7's step 3 made the hand sample a line item.

## 3.2 Read the report's method first

Ask whoever produces the report (at Godavari, the core-system owner) for the query. Line by line:

| The report says | What it actually counts | What that does to the number |
|---|---|---|
| "median turnaround 9.2 days" | core-system *received date* to sanction date, sanctioned files only, last quarter | the received date is typed by the analyst from the form; on resubmitted files some analysts type the resubmission date (the core-system owner confirmed it when asked in week 3). Withdrawn and rejected files are not in the median at all |
| "4.5 analyst hours per file" | the team leads' estimate in a 2024 staffing note | never timed |
| "31 percent sent back" | files with a "returned to branch" status in the core | a send-back by phone or WhatsApp that never got the status is not counted; a file returned twice counts once |

The COO's own interview (Day 6, transcript 03) holds two definitions in two sentences: "from the
customer signing the application at the branch to the sanction letter", and "received date to
sanction date" in the core. The customer feels the first; the report measures the second. **Write
down which one the baseline uses before you count** (section 08 makes it a signed definition). At
Godavari it is the customer's clock, signed at the branch to the decision, because that is what the
COO promised the board and what a faster competitor competes on.

## 3.3 Two clocks, two methods

Turnaround takes nine days, so you cannot wait for files that arrive this week to finish. Hours are
spent in the moment, so you cannot reconstruct them from records. The baseline therefore uses two
methods.

| Measure | Method | Window | Source |
|---|---|---|---|
| turnaround and its stages; send-backs; outcome; documents present | **retrospective cohort**: files received in a past fortnight, all decided by now, reconstructed from records | a fortnight five to six weeks back, chosen to avoid month-end, Sankranti and Dussehra (Day 5's calendar) | the signed application form (signing date), the SFTP server's arrival log, the core's record-creation timestamp (when an analyst first opened and keyed the file) and decision date, the core's status history, the tracker's "waiting on" text |
| analyst hours and their split | **prospective timing log**: analysts log start and stop by activity on sampled files | discovery weeks 2 and 3, the first two days discarded | a two-column addition to the tracker, checked against ten files the FDE shadows end to end |

The first two days of timing are discarded (people work differently when they know they are timed,
and it fades), and ten shadowed files check the self-reported times; a gap above 15 percent means the
log is redesigned.

## 3.4 The frame: every file, from the source that cannot forget one

A **sampling frame** is the complete list you draw from. The commonest error is to use a list that
has already lost the files you most need. At Godavari:

- the **core** has no record of files withdrawn before an analyst keyed them;
- the **tracker** has no row for a file until a team lead assigns it;
- the **SFTP arrival log** has every file the branches sent, with a timestamp.

So the frame is the SFTP log: every new loan file (not resubmissions) that arrived in the fortnight.
At about 1,400 new paper and PDF files a month (60 percent of the roughly 2,400 applications in Day 7's
inventory), that is about 700 files. Day 7's generator produces exactly this
frame when asked for 700 files with its own seed, and its first 200 rows are Day 7's sample (the
script checks this).

## 3.5 Drawing the sample: stratified by branch cluster and product

Counting all 700 files would take about 230 hours; a well-drawn sample of 120 gives nearly the same
answer for about 40.

**Stratified sampling** in one paragraph: split the frame into groups that differ from each other
(the strata), draw at random inside every group, and weight each group by its share of the frame
when you add the answers up. It guarantees that every group is in the sample (a simple random draw
of 120 can easily give you one personal loan from Guntur), and it makes the estimate more precise
when the groups really differ.

Godavari's strata are **branch cluster x product**: six clusters (the generator's six branches, each
standing for about fifty that route through one hub) and four products, 24 strata, because they
differ for reasons Day 6 found (gold files are short; personal loans are sent back most; far branches
send phone photos). Allocation is proportional to stratum size with a floor of two, by largest
remainder, and each file carries a **weight**, stratum size over files sampled: a Vijayawada
two-wheeler file (53 in the frame, 9 sampled) stands for 5.9 files.

**How big?** For a rate near 30 percent, plus or minus 8 points at 95 percent needs about 126 files;
the finite frame of 700 brings it to about 107, and the floors push it to 120. Precision depends on
the sample size far more than on the frame, and halving an interval needs four times the files.

**Rules for the draw**, each there to stop an argument later: the draw is seeded and the seed is in
the pack, so the compliance head can re-run it; the list is fixed before anyone opens a file; a file
whose records cannot be found is recorded as "not found", never replaced (above about 5 percent, that
is itself a finding); and nobody re-draws because the answer looks wrong (section 10 shows a 28
percent send-back rate against the report's 31, and why it stands).

## 3.6 The hand-count form

One row per sampled file. Every column names its source, so a second counter can check it.

| Column | Source | Notes |
|---|---|---|
| file number, branch, product, channel | SFTP log, form | channel: scan, phone photo, mixed |
| signed at branch (date) | the application form | the customer's clock starts here |
| visible on SFTP (timestamp) | the SFTP server log | transit ends |
| first opened (timestamp) | the core's record-creation time | queue ends; the tracker cannot give this |
| each send-back: date out, date back, reason | core status history, tracker text, analyst's note | count every round, including phone and WhatsApp chases the analyst remembers and can date |
| decision and date | the core | sanctioned, rejected, withdrawn |
| mandatory documents present at decision (PAN, address proof, income proof, photo) | the file of record | "present" means in the file, not on someone's phone |
| hours: re-keying, completeness check, chasing, assessment and memo | the timing log | for the timing sample |
| counter's initials; second counter's initials (10 percent) | | disagreements are discussed and the rule written down |

Twelve files (10 percent) are counted twice, by Bhavani and the FDE for example. Disagreements (the
send-back count and the "present" judgement on address proof) become a written rule, and the first
counter's other files are rechecked against it.

## 3.7 What Godavari's hand count found

The full output is in section 10. The short version, with 95 percent intervals:

| Metric | Ops report | Hand count |
|---|---|---|
| median turnaround, days | 9.2 | 9.1 (8.7 to 9.7) |
| analyst hours per file | 4.5 | 4.6 (4.5 to 4.7) |
| send-back rate | 31% | 28% (21% to 35%) |

The report survives: each of its numbers sits inside the hand count's interval. That is a good
outcome, and it is information: from now on the monthly report can be trusted as a trend, with the
two definition caveats from 3.2 written beside it.

The hand count also found what the report cannot see (every interval is in the baseline pack):

- **Where the days go.** Transit 1.1 days; **queue 6.4 days** (SFTP arrival to first opened); work
  1.6 days; about 3 days of branch wait on each file sent back. The analysts' "a clean file takes a day
  and a half" (Day 6, C1) is the work stage, timed from when they open it. The COO's nine days include
  six in a queue nobody reports, because the tracker has no timestamps and the core starts its clock
  late. Everyone was right from where they sat (Day 5's theme); the hand count reconciles them.
- **Where the hours go.** Re-keying 0.97, completeness 0.35, chasing 0.27, assessment and memo 3.0.
  The first three, **1.59 hours**, are addressable; Day 4's memo needed at least 1.2. The pick holds.
- **Risk.** 4.1 percent of files (0.9 to 7.2) were decided with a mandatory document missing; today's
  human check caught 87 percent of incomplete files. The compliance head's "never" is not today.
- **Walk-aways.** 10.1 percent of customers (5.2 to 14.9) withdrew, invisible in a median of
  sanctioned files.

## 3.8 What it cost

About 40 hours of reconstruction, two minutes of logging per timed file, ten shadowed files and an
hour with the compliance head: under a week of one person, for a renewal that depends on it.

## 3.9 Key takeaways

- Read the report's method before trusting its number; choose the customer's clock.
- Frame from the source that cannot forget a file; stratify, weight, seed, fix the list, never re-draw.
- The hand count usually confirms the report and always finds what it cannot see.
