# 05 · Quality Signals Without Ground Truth, and How They Connect Back to the Golden Set

> Day 19 · Section 5 of 15 · [Chapter overview](README.md) · Previous: [04 · Cost per file](04-cost-per-file-branch-and-product.md) · Next: [06 · Feedback capture](06-feedback-capture-as-a-product-feature.md)

---

## 5.1 The rule: every production signal is compared with something

A number on its own says nothing. "Eight percent of applicant names were corrected this week" is alarming or
reassuring only beside what the golden set measured for that field. Day 14 owns the definitions; this chapter computes
the same quantities on the production stream and puts each beside its baseline.

| Signal | Compared with | What it can tell you | What it cannot |
|---|---|---|---|
| corrections per field | the golden set's error rate for that field (Day 14 baseline run) | a field drifting beyond what the evaluation saw | whether accepted values are right |
| review-band corrections per analyst | the bands' expected wrong share, 5.4 percent (Day 18) | an analyst correcting far less than the files need | why |
| rubber-stamp sessions | Day 18's dwell and burst thresholds | a session worth a second read | that anything was missed |
| spot checks | zero, with an upper bound | confident-wrong values, directly | much, on 44 fields a week |
| rule and envelope fire rates | last week, per branch | that the files, the model or a rule changed | which, without the trace |
| unsure fields, unclassified pages | last week | the model saying "cannot tell" more or less often | whether it should |
| policy-panel zero results and refusals | zero | a metadata hole or a broken group sync | relevance |

## 5.2 Corrections per field, against the golden set

The quality job counts, per field, the files where an analyst changed the model's value (format-only tidy-ups
excluded, keyed values included), and puts a Wilson interval round it, the same interval Day 14 uses. The golden set's
error rate comes from Day 14's stored baseline run, `eval-baseline.json`. A field is flagged only when the two
intervals do not overlap.

```text
applicant_name      5 of 60    8.3% (3.6% to 18.1%)   golden  5.3% (2.7% to 10.2%)   in line
pan                 5 of 60    8.3% (3.6% to 18.1%)   golden  6.0% (3.2% to 11.0%)   in line
monthly_income      5 of 60    8.3% (3.6% to 18.1%)   golden  4.0% (1.6% to 9.8%)    in line
on_road_price       0 of 60    0.0% (0.0% to 6.0%)    golden  8.0% (4.1% to 15.0%)   in line
```

Two readings matter more than the verdict:

- **Sixty files is not much.** The interval on 5 of 60 runs from 3.6 to 18.1 percent. A real doubling of the error
  rate would take a few weeks to separate from the golden set. That is why the job reports intervals and not points,
  and why a single week is a reason to look, never a reason to roll back.
- **Zero is not good news by itself.** On-road price was the field with six confidently-wrong values in the golden
  set; in pilot week two, analysts corrected none in 60 files. Either the pilot files are cleaner, or the field is not
  being checked. Day 18 made on-road price the look-first field for exactly this reason, and the review span carries
  the seconds spent on it (GF-61070: 14.5). Dwell near Day 18's normal says people are looking; a zero with dwell
  near zero would be the rubber-stamp pattern. The two signals are read together.

A test injects 12 corrections of `monthly_income` into 40 files and checks the job says "higher than the golden set".

## 5.3 Overrides and the rubber-stamp signals

Day 18 built the detectors; this chapter runs them weekly and routes them. In week two, every pilot analyst's
review-band corrections were in line with the expected 5.4 percent, and no session met the rubber-stamp test (week
one had one: V2's Friday afternoon, which Day 18 planted and caught). Fast-only sessions (four in week two) are
reported and deliberately not acted on: Day 18's rule is that speed alone is not a flag.

These signals are about people, and they go to the analyst's own team lead and nobody else. The routing table in
`alerts.py` says so in code, and the team leads' page says so in words.

## 5.4 Spot checks: the only direct measure

Every week, Day 18's sampler draws approved files at random with a key the analysts' tool cannot read, and a second
reader checks the auto-accepted fields blind against the paper. In both pilot weeks: 0 wrong, in 47 and 44 fields.
The upper bound after week two is 8.0 percent. That is honest and weak: the bound falls slowly, and Day 18 computed that
proving a 1 percent rate needs about 299 fields. The FDE page shows the bound, not "0 errors", so nobody reads the
zero as proof.

## 5.5 Rule fire rates that drift

```text
ENV-CONFIDENCE   Guntur     16/30 -> 25/30
TW-DOC-05        Guntur     5/30 -> 2/30
```

Day 11 named this signal ("fields under threshold") and its likely causes: new scan quality, or a new branch's phone
photos. The quality job says the rate moved; the traces say why. Splitting Guntur's routes by the channel on the
root span:

| Guntur | scanner uploads | phone photos | mixed |
|---|---|---|---|
| week one: files (ENV-CONFIDENCE fired) | 15 (8) | 5 (5) | 10 (3) |
| week two | 9 (4) | 8 (8) | 13 (13) |

The rule fires on nearly every phone photo and, this week, on every mixed upload. The branch sent fewer scanner
uploads. The model did not change and the rules did not change; the files did. That is item O3 for the Vijayawada team
lead: is the scanner at Guntur working? A rule that moves for one branch, on one channel, is often a machine in a
branch office.

TW-DOC-05 (proof of address missing) going down from 5 to 2 is the other direction: Guntur's staff responded to week
one's send-backs. The same response gave Tuesday's long statements. Observability sees both halves of one human
decision.

## 5.6 Unsure, unclassified and retrieval

The pipeline-read span carries the fields the model said it could not read and the pages it labelled unknown. The
second number includes filler pages (terms and conditions, blank pages), so it is compared week against week, never
read as an error count. The policy panel's spans (Day 15) carried no empty results in either week and three refusals,
all on Thursday 17 December at 15:00, when the group snapshot was 37 hours old: the HR-to-AD export had not run that
night. The panel failed closed, which is right, and the digest told Godavari's IT identity team, which is the point.

## 5.7 Back to the golden set

The quality job's last output is a list for Day 14, not a verdict:

```text
- 24 files over 60 pages this week (the longest of the golden set's 200 files has 40): add five masked long-statement
  files to Day 14's development split, labelled and adjudicated as usual
```

This closes the loop the curriculum describes. The golden set measures accuracy on what it contains; production finds
what it does not contain; the corrections and the shapes production saw go back to Day 14 as candidates; Lakshmi and
the senior analyst label them; the gate then protects against the new failure for good. Day 18's corrections feed the
development split the same way, never the test split, and never without a second label.

> **Telugu callback for the video.** "Day 14 lo golden set lo 150 files unnayi. Production lo answer key ledu. Andhuke
> prati signal ni golden set number pakkana pedatam, interval tho."
