# 04 · The Scoring Sheet: Six Criteria, Three Gates, and Pain in Hours and Rupees

> Day 4 · Section 4 of 12 · [Chapter overview](README.md) · Previous: [03 · Start from the workflow](03-start-from-the-workflow.md) · Next: [05 · The traps](05-the-traps.md)

---

## 4.1 Why a sheet at all

You could pick intake by instinct, and at Godavari you would be right. The sheet is not there to
replace the instinct. It is there for three other reasons:

- **The sponsor can see the reasoning.** "Intake, because it scored 93 and the chatbot scored 55,
  and here is the column where the chatbot lost" is a conversation. "Intake, trust me" is not.
- **The same sheet runs on the next customer.** Day 42's hospital has its own seven candidates. A
  method you can repeat is a method you can be interviewed on.
- **It catches your own bias.** The traps in section 05 are all things an engineer does by instinct.
  A column with an anchor makes you write down the volume you are guessing at.

## 4.2 The six criteria

Each criterion is scored 1 to 5 against a written anchor. The anchors matter more than the
weights: two people scoring the same row against the same anchors should land within one point of
each other.

| Criterion | What it asks | 1 | 3 | 5 |
|---|---|---|---|---|
| **Frequency** | How often does the unit of work happen, and to how many people? | a few times a month, one team | daily, one team | many times a day, many people, in the core process |
| **Pain** | What does it cost today in hours, rupees, errors and waiting? Hours first, because they can be counted | nobody complains; cost unknown | a known cost that one team carries | a cost in the monthly report, with waiting and rework on top |
| **Measurability** | Is there a baseline today, counted by the customer, that the system would move? | no number exists; you would have to invent one | a number exists but needs cleaning or a hand count | turnaround, send-backs or error rate already reported monthly |
| **Data availability** | Do the inputs exist, can you see them, and is someone allowed to give them to you? | nobody knows where the data is, or a third party holds it | the data exists inside the customer but access needs a ticket and a review | the data is on a share you have been shown, with an owner who said yes |
| **Blast radius** (scored, then inverted to safety) | If the system is wrong on one unit, what breaks? | a bad draft someone edits | a wrong field that a reviewer catches most of the time | a regulatory finding, a wrong credit decision or a customer harmed |
| **Sponsorship** | Who funds it, who wants it, and does it fit the vendor's product? | the sponsor mentioned it once; no operator asked; Kaagaz would build it custom | the sponsor wants it; the operators are neutral; the product can absorb it | the sponsor funds it, a named operator asked for it, and two other customers would buy the pattern |

Blast radius is the column engineers skip and compliance heads read first. It is inverted in the
score (safety = 6 minus blast radius) so that a harmless failure scores high. A high blast radius
does not disqualify a problem; intake's own completeness check is a 3, because a missed KYC
document is an audit finding and a human approves every file. It changes what the solution must
contain, which [Day 7](../07-decomposition/README.md)'s step 1 writes down as the trade-off and
Day 18's review queue builds.

Sponsorship folds in the Part file's "strategic fit" and Day 3's second-customer test. A problem
with a sponsor and no operator is the sponsor's pet project (section 05). A problem with an
operator and no sponsor is a side-build nobody funds. A problem both want but that Kaagaz's product
cannot absorb is services work. The 5 requires all three.

## 4.3 The weights

The chapter's script weights them: pain 3; frequency, measurability, data and sponsorship 2;
safety 1. Pain is the heaviest because it is the only criterion that is also the business case.
Safety is the lightest in the score because a high blast radius is handled by design (a human in
the loop) rather than by avoidance; it is a condition, not a veto.

Weights are a convention to argue with. The script's last job is to try twelve other weightings
(equal weights; each criterion ignored; each criterion tripled) and say whether the winner changes.
If it does, the pick is a judgement call and the memo must say so. At Godavari it does not, which
is the strongest thing you can say to a COO: "intake wins however you weight the columns."

## 4.4 The three gates

Some problems are not scored low; they are not scored at all this week. The Part file lists the
three conditions for declining a problem on Day 4, and the sheet treats each as a gate that a
candidate passes or fails before its score counts:

| Gate | The question | Why it is a gate and not a score |
|---|---|---|
| **A baseline exists** | Can the customer say today how long it takes or how often it fails? | without a baseline there is no proof at day 90, and Day 9's business case has nothing to start from. "We will measure it after we build it" is a demo with a delay |
| **A data owner exists** | Is there a person inside the customer who can hand you the inputs? | if the data is held by a vendor (the dialler), by outsiders (the lawyers) or by nobody, the first eight weeks are a procurement exercise, not an engagement |
| **An operator wants it** | Has someone whose Tuesday would change asked for it, or at least said yes when shown? | adoption is decided here. A system the operators did not ask for is the prototype nobody runs; value cannot sustain use that never starts |

A failed gate is a reason, not a verdict: it tells you what has to become true before the
candidate can be scored. "Not now, because there is no baseline; count the calls for a month and we
will score it in the next cycle" is the sentence Day 10 says to the COO about the chatbot. The
gate is where that sentence comes from.

## 4.5 Pain in hours and rupees

The pain score is judgement; the evidence under it is arithmetic, and the sheet carries both.
For each candidate: volume a month times hours per unit gives hours a month; hours a month times a
loaded cost per hour gives rupees a month.

| Candidate | Volume a month | Hours a unit | Hours a month | Rupees a month at 300 an hour |
|---|---|---|---|---|
| C1 intake and completeness | 1,400 | 1.5 | 2,100 | 6.3 lakh |
| C6 collections summaries | 18,000 | 0.08 | 1,440 | 4.3 lakh |
| C3 KYC and re-KYC | 3,000 | 0.3 | 900 | 2.7 lakh |
| C7 credit memo | 1,400 | 0.5 | 700 | 2.1 lakh |
| C2 income verification | 900 | 0.75 | 675 | 2.0 lakh |
| C8 the tracker | 1,400 | 0.4 | 560 | 1.7 lakh |
| C4 title deeds | 120 | 3 | 360 | 1.1 lakh (paid to lawyers, not analysts) |
| C5 branch chatbot | 2,000 (a guess) | 0.1 | 200 | 0.6 lakh |

Three cautions, each of which the script enforces or the memo states:

- **300 rupees an hour is a planning placeholder.** It is roughly a 6 lakh a year loaded cost over
  2,000 working hours, invented. [Day 9](../09-success-metrics-and-business-case/README.md) measures
  the real loaded rate, adds the disbursement pulled forward and the cost of a compliance finding,
  and owns the business case. On Day 4 the rupee column exists to rank, not to promise.
- **Hours are not the whole pain.** Income verification (C2) scores pain 4 on 675 hours because
  the real cost is days of waiting for a statement, not minutes reading it. The tracker (C8) scores
  4 on 560 hours because the cost is forty people maintaining duplicate state by hand. The script
  warns when a pain score is high and the hours are below the median, and the memo has to say in
  words what the pain is instead. That warning fires twice at Godavari, and both times the answer
  is in the catalogue's note.
- **A high hours figure for a guessed volume is a guess.** C5's 2,000 calls a month is the COO's
  estimate; nobody counts. The sheet keeps the row, scores measurability 1, and the gate fails.

## 4.6 The sheet on Godavari

The filled sheet is `data/godavari-candidates.csv`; section 08 runs it. The scores and the reasons
in one table:

| Code | Freq | Pain | Meas | Data | Blast | Spons | Gates | Score /100 | The one-line reason |
|---|---|---|---|---|---|---|---|---|---|
| C1 intake and completeness | 5 | 5 | 5 | 4 | 3 | 5 | pass | 93 | every file, every day; 2,100 hours a month plus a third of files reworked; already in the monthly report; PDFs on a share, tracker on a share; a wrong field is caught by the analyst; the COO funds it, Srinivas and Lakshmi want it, every lender needs it |
| C2 income verification | 4 | 4 | 3 | 3 | 4 | 3 | pass | 67 | most files but not all; the pain is waiting; not timed separately; thirty bank formats; a wrong income is a wrong decision; nobody asked for it yet |
| C7 credit memo | 5 | 3 | 3 | 3 | 4 | 3 | pass | 65 | every file; half an hour; not timed; needs C1's fields first; the auditor reads it |
| C8 the tracker | 5 | 4 | 4 | 5 | 2 | 2 | fails: operator | 80 | the analysts do not want it replaced; they want it not to be a second system. Folded into C1 as a constraint (section 08) |
| C3 KYC and re-KYC | 5 | 3 | 4 | 3 | 5 | 2 | fails: operator | 63 | different operators; the compliance head said not this year; a wrong KYC is a regulatory finding |
| C6 collections summaries | 5 | 3 | 3 | 2 | 2 | 2 | fails: owner, operator | 62 | different team; recordings held by the dialler vendor; DPDP questions open; the collections head not in the room |
| C5 branch chatbot | 4 | 2 | 1 | 3 | 3 | 4 | fails: all three | 55 | the sponsor loves it; nobody counts the calls; no owner of the circulars; no branch asked |
| C4 title deeds | 2 | 3 | 2 | 2 | 5 | 3 | fails: all three | 47 | 120 a month; outside lawyers; Telugu deeds; a bad title loses the loan |

Intake wins by 26 points over the next candidate that passes the gates, and the script confirms the
winner is stable under every alternative weighting. The tracker's 80 is the interesting number: it
is the second-highest score on the sheet, it fails a gate, and section 08 explains why the right
answer is neither to pick it nor to drop it.

## 4.7 Key takeaways

- Six criteria with written anchors: frequency, pain, measurability, data availability, blast
  radius (inverted to safety) and sponsorship. Anchors matter more than weights.
- Three gates before any score counts: a baseline, a data owner, an operator who wants it. A
  failed gate is a "not now, because" sentence.
- Pain is scored as judgement and evidenced as hours and rupees; the rupee rate is a placeholder
  until Day 9; the script warns when the two disagree.
- At Godavari intake scores 93, wins by 26, and survives every weighting. Say that to the COO.
