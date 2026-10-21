# 08 · Pre-Registration, the Numbers That Get Gamed, and the Eval Metric Underneath

> Day 9 · Section 8 of 14 · [Chapter overview](README.md) · Previous: [07 · The one-page case](07-the-one-page-case.md) · Next: [09 · 2026 patterns and production concerns](09-2026-patterns-and-production-concerns.md)

---

## 8.1 Why write the definition down before the pilot

Every metric has choices hidden in it: when the clock starts, which files count, what "sent back"
means, what happens to a file that is withdrawn. Make those choices after you have seen the pilot's
numbers and you will make them, honestly or not, in the direction that helps. Everyone does. Goodhart's
law says it in one line: when a measure becomes a target, it stops being a good measure.

**Pre-registration** is the defence medical research uses: write the outcome, the method and the
analysis down before the trial starts, and get it signed. For an FDE it means a one-page metric
definition, signed by the sponsor and the compliance head (and, for the operational metrics, the two
team leads) in discovery week four, before the pilot touches a file. The filled Godavari version is
[`worksheet/godavari-metric-definitions.md`](worksheet/godavari-metric-definitions.md).

The COO signs because the headline is his and he must not be able to move it after a bad month; the
compliance head because the risk metric is hers and a definition she signed can be shown to the RBI
inspector; the team leads because the hours are measured on their floors. A definition Kaagaz wrote
alone is a vendor's claim.

## 8.2 What a definition contains

| Field | Godavari's turnaround, as signed |
|---|---|
| name | median turnaround |
| definition | days from the customer's signature on the application form to the decision (sanction, rejection, or withdrawal recorded) |
| unit and statistic | calendar days, median; mean reported in the appendix |
| population | every new file (not resubmissions) arriving on SFTP from the pilot branches; resubmissions keep the original signing date |
| exclusions | none; withdrawn and rejected files are included at their decision date |
| source | the form's signing date; the core's decision date; the SFTP log as the frame |
| baseline | 9.1 days (8.7 to 9.7), 120 stratified files, fortnight of the 6th to the 19th, method in the baseline pack |
| target | 3 to 4 days in the pilot branches by day 90 |
| comparison | pilot files against the baseline cohort, same definition; seasonal months flagged; Day 37 owns the analysis |
| what counts as a change | the pilot's interval entirely below 8.5 days |
| measured by, and when | the FDE and Bhavani, monthly; the compliance head re-draws one month in three |
| guardrail | files decided with a mandatory document missing must not rise above the baseline's 4.1 percent |

Two fields do most of the work. **Population** closes the "only the easy branches" door. **What counts
as a change** closes the "8.8 is an improvement" door, because the threshold was written before
anyone knew the result.

## 8.3 The numbers that get gamed (a preview; Day 37 owns the catalogue)

Most gaming is not fraud. It is people making reasonable-sounding choices after seeing the data.
These are the ones to close in the definition, now.

| The number | How it gets gamed | The line in the definition that closes it |
|---|---|---|
| turnaround | the clock starts when the file reaches the core, not when the customer signed | definition: from the signature |
| turnaround | a resubmitted file gets a new start date | resubmissions keep the original signing date |
| turnaround | withdrawn files disappear from the median (survivorship: the slowest files are the ones that vanish) | exclusions: none |
| turnaround | the pilot runs in the branches with clean SFTP scans (22 percent send-backs against 30 for the frame) | population: the pilot branches named in advance, with their own baseline |
| hours per file | self-reported by people who want the tool to succeed (or to fail) | measured by the review screen's own timer, checked against shadowed files |
| send-back rate | falls because analysts stop sending files back | guardrail: files decided with a document missing |
| field accuracy | computed only on the fields the model is good at, or on the golden set the prompts were tuned on | accuracy on all mandatory fields, on a held-out part of the golden set (Day 14) |
| the sample itself | re-drawn until it agrees with the report | seed and list fixed before counting; "never re-drawn" in the pack |

The baseline can be gamed both ways: timed slowly to flatter the tool, or fast by a team afraid for
its headcount. Keeping the timing log running for a fortnight after launch, on the same rules, gives
Day 37 one instrument on both sides.

## 8.4 The leading indicators, registered too

Register the weekly indicators from section 02.4 with an expected direction and level (section D of
the definitions worksheet), so that a late lagging number can be explained by an on-track leading
one, and a bad leading number is an early warning rather than an excuse after the fact.

## 8.5 The eval metric the case depends on

Section 07's sensitivity table said the case fails below about 45 percent capture. Capture is not
something the system has; it is what the analysts do with the system's output. They stop re-typing a
field only when they trust it, and they trust it only when it is right almost every time. So the
capture share rests on one system metric: **field-level accuracy on the mandatory fields, measured on
the golden set** ([Day 14](../../03-building-the-system/14-evals-first/README.md): 100 to 200 real
files, labelled by Lakshmi and the senior analyst, the completeness labels signed by the compliance
head, agreed before a model is chosen).

The link is an assumption, and it is registered as one:

| Field-level accuracy on mandatory fields (golden set) | Assumed capture share | Net a year at base retention |
|---|---|---|
| 95 percent or more, with uncertain fields routed to review | 60 percent | +15 lakh |
| 90 to 95 percent | 45 percent | about break-even |
| below 90 percent | 30 percent (analysts re-check everything) | -53 lakh |

Three consequences. **The golden set is the case's first checkpoint**: if Day 14's held-out run says
88 percent, the case is below break-even before the pilot, and the COO hears it at the next readout.
**The accuracy definition is registered too**: correct means what Lakshmi would have typed, per
field, mandatory fields named, handwritten Telugu fields separate (Day 6, A8). **Human accuracy is a
baseline**: double-keying 30 golden-set files gives the analysts' own error rate, the fair comparison
for the compliance head.

The model metric is never the headline (section 02.2). It is the first number that can sink the case,
which is why it is measured first.

## 8.6 Key takeaways

- Pre-register: write the definition, population, exclusions, baseline, target and "what counts as a
  change" before the pilot, signed by the COO, the compliance head and the team leads.
- Most gaming is a reasonable choice made after seeing the data; close each door in the definition.
- Register leading indicators with expected directions so they can be early warnings, not excuses.
- The case depends on capture share, which depends on field-level accuracy on the golden set; register
  that link as an assumption and measure it first.
