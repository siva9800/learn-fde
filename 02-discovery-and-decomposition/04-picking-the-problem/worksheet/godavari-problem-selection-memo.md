# Problem selection memo: Godavari Finance Ltd

> Engagement folder · Day 4 · Written on the Friday of week one · Companion to `data/godavari-candidates.csv`, `data/godavari-candidates-ranking.md` and `code/score_candidates.py`
> Author: the Kaagaz AI FDE on the Godavari engagement · Status: draft for the COO's Friday twenty minutes · Version: 1 (to be revised at Day 6, Day 9 and Day 20)

Every number about Godavari is invented for the course. Volumes are from the credit-ops monthly
report and the team leads' counts on Thursday; hours per unit are the team leads' estimates, to be
measured by a two-week hand count on Day 9; rupees use a planning rate of 300 per analyst hour,
also to be replaced on Day 9.

## 1. The one-sentence problem statement

> New loan files take a median of nine days from receipt to decision because intake is manual and a
> third of files are incomplete.

Signed by: the COO (sponsor) · Srinivas, credit-ops team lead, Hyderabad · the credit-ops team
lead, Vijayawada
Read by: Lakshmi, credit-ops analyst, Vijayawada ("yes, that is the job")

## 2. The catalogue

Seven candidates from the COO's kickoff and second call; one from the floor walk. The branch CRM is
not listed: it was declined before the contract was signed (Day 3).

| Code | Candidate | Raised by | Volume a month (source) | Hours a unit (source) | What the floor says |
|---|---|---|---|---|---|
| C1 | Loan-file intake and completeness check | COO, kickoff | ~1,400 new files (monthly report) | ~1.5 of the 4.5 hours a file (Srinivas's estimate) | 60 percent paper or PDF; re-keyed into the 2009 core; 31 percent sent back at least once; turnaround and send-backs already reported monthly |
| C2 | Income verification from bank statements | COO, kickoff | ~900 (salaried and small-business files, monthly report) | ~0.75 (two analysts' estimate) | thirty-odd bank formats, some password-protected; the cost is days waiting for the statement, visible in the tracker's "waiting on bank statement since" column |
| C3 | KYC document checks and periodic re-KYC | COO, kickoff | ~3,000 customers due (compliance desk) | ~0.3 (compliance desk) | done by branch staff and a two-person compliance desk; the compliance head owns it and said "not this year" for any vendor |
| C4 | Title-deed review for secured loans | COO, kickoff | ~120 (monthly report) | ~3, by empanelled lawyers (the COO's estimate) | outside lawyers; scanned registered deeds in Telugu; the legal head has not been met; nobody times it |
| C5 | Branch chatbot for policy questions | COO, kickoff | ~2,000 calls (the COO's guess; nobody counts) | ~0.1 (guess) | forty circulars in email with unclear versions; no branch manager was asked; the COO saw a demo at a conference |
| C6 | Collections call summaries | COO, second call | ~18,000 calls (dialler report, via the COO) | ~0.08 of note-writing (the COO's estimate) | a different team of forty agents; Telugu recordings held by the dialler vendor; consent and DPDP questions open; the collections head not in the room |
| C7 | Credit-memo drafting | COO, kickoff | ~1,400 (one per file) | ~0.5 (Srinivas's estimate) | Word files on a shared drive; the inputs are the fields intake would produce; the auditor reads the memo |
| C8 | Replace the Excel tracker | the FDE, floor walk (Wednesday, Vijayawada) | every file, every day | ~0.4 of upkeep per file (Lakshmi's estimate) | forty workbooks; the true state of every file; the COO does not know it exists; the analysts fear losing it |

## 3. The gates

| Code | Baseline exists? | Data owner exists? | An operator wants it? |
|---|---|---|---|
| C1 | yes: median turnaround and send-back rate in the monthly report; file status in the tracker | yes: scans on the SFTP share (branch operations); the tracker (the Vijayawada team lead) | yes: Srinivas and Lakshmi, unprompted ("stop making us type it twice") |
| C2 | yes: the tracker's waiting column | yes: statements arrive with the file | yes: the same analysts, though nobody raised it |
| C3 | yes: overdue re-KYC count against RBI due dates | yes: the compliance desk | no: branch staff not asked; the compliance head said not this year |
| C4 | no: nobody times the review | no: the lawyers hold the opinions | no: the legal head not met |
| C5 | no: the calls are not counted | no: nobody owns the circulars | no: no branch asked |
| C6 | yes: the dialler counts calls | no: the recordings are with the dialler vendor | no: the agents and their head not asked |
| C7 | yes: one memo per file; the time is Srinivas's estimate | yes: the shared drive, credit-ops | yes: the analysts, after intake |
| C8 | yes: the tracker itself | yes: the Vijayawada team lead | no: the analysts want it to stop being a second system, not to be replaced |

## 4. The scores

From `code/score_candidates.py` (run Friday; output in `data/godavari-candidates-ranking.md`):

| Rank | Code | Freq | Pain | Meas | Data | Blast | Spons | Gates | Score /100 | The one-line reason |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | C1 intake and completeness | 5 | 5 | 5 | 4 | 3 | 5 | pass | 93 | every file, every day; 2,100 hours a month plus a third of files reworked; already in the monthly report; the data is on shares we were shown; a wrong field is caught by the analyst who approves; the COO funds it, the team leads want it, every lender needs it |
| 2 | C2 income verification | 4 | 4 | 3 | 3 | 4 | 3 | pass | 67 | most files; the pain is waiting days; not timed separately; thirty formats; a wrong income is a wrong decision; the sponsor is neutral |
| 3 | C7 credit memo | 5 | 3 | 3 | 3 | 4 | 3 | pass | 65 | every file; half an hour; not timed; needs intake's fields; the auditor reads it |
| - | C8 the tracker | 5 | 4 | 4 | 5 | 2 | 2 | operator | 80 | see section 5: folded into C1 |
| - | C3 KYC and re-KYC | 5 | 3 | 4 | 3 | 5 | 2 | operator | 63 | different operators; the compliance head's "not this year"; a regulatory blast radius |
| - | C6 collections summaries | 5 | 3 | 3 | 2 | 2 | 2 | owner, operator | 62 | different team; vendor-held recordings; DPDP open |
| - | C5 branch chatbot | 4 | 2 | 1 | 3 | 3 | 4 | all three | 55 | no count, no owner, no branch asked; the sponsor's enthusiasm is the only evidence |
| - | C4 title deeds | 2 | 3 | 2 | 2 | 5 | 3 | all three | 47 | rare, outsourced, untimed, high blast radius |

Consistency warnings the script printed, and the answer to each:

- C2: pain 4 on 675 hours a month, below the median -> the pain is the days each file waits for a
  bank statement (the tracker's waiting column), not the minutes spent reading one. The hours
  understate it; the waiting is counted on Day 9.
- C8: pain 4 on 560 hours a month, below the median -> the pain is forty people keeping the state
  of every file by hand in a second system, and the nine days being invisible to the core system.
  Hours understate it; the cost is duplicated state and lost visibility.

Sensitivity: the winner is stable under every alternative weighting the script tries (equal
weights; each criterion ignored; each criterion tripled). Intake wins however the columns are
weighted.

## 5. Why loan-file intake and completeness

1. **Frequent and at the core.** About 1,400 new files a month (the 60 percent of Godavari's roughly 2,400 monthly applications that
   arrive as paper or PDF, per Day 7's inputs inventory), every one of them through forty
   analysts in two cities, in the process that is Godavari's business. It is the largest unit of
   work on the list that the credit-ops team itself does.
2. **Painful in hours and in rework.** About 2,100 analyst hours a month on intake and completeness
   (6.3 lakh a month at the planning rate), and 31 percent of files sent back to the branch at
   least once, each send-back costing about three days of waiting. The 4.5 hours a file and the 31
   percent are the ops team's own numbers.
3. **Already measured.** Median turnaround and send-back rate are in the monthly report; file
   status is in the tracker. Day 9's hand count confirms rather than invents the baseline.
4. **Wanted by the people whose day changes, and absorbable by the product.** Srinivas and Lakshmi
   asked for it in their own words. Kaagaz can name two more NBFCs in the pipeline with the same
   intake shape (Day 3), so the fix becomes product, not a side-build.

**The tracker (C8) is folded into this pick as a constraint, not dropped.** It scored second on
the sheet and failed the operator gate, and both facts are correct: it is where the pain of C1
lives, and the analysts do not want it replaced by a vendor's screen; they want to stop running two
systems. So intake must read the tracker before it replaces anything and write file status back to
it, or the analysts will keep the tracker open beside the new system and the pick fails in month
four. Day 7's inputs map carries this as a row; Day 8's plan carries it as a condition.

**What this pick needs to be true by Day 9:** the two-week hand count finds the intake and
completeness share of analyst time at or above about 1.2 hours a file, the send-back rate at or
above 25 percent, and median turnaround near nine days. If the hours come in far lower, the pick
still stands on send-backs and turnaround, but the business case shrinks and the memo is versioned.

**Blast radius, handled by design, not avoided:** a missed mandatory KYC document is an audit
finding. The completeness rules will be deterministic code the compliance head signs (Day 11), and
an analyst approves every file (Day 18). Those are conditions of the pick.

## 6. Not now, because, and instead

Said to the COO in ranking order, so the first two he hears are "second" and "third":

| Candidate | Not now, because | And instead |
|---|---|---|
| C2 income verification | a third of statements have not arrived when the file is opened; it waits on intake | second in the ranking; the natural next slice once intake runs; Day 8 decides whether it fits the 90 days |
| C7 credit memo | its inputs are the fields intake would extract; building it first means building intake twice | third; revisit after the walking skeleton (Day 20) |
| C8 the tracker | the analysts do not want it replaced | a constraint on intake (section 5) |
| C3 KYC and re-KYC | the compliance head owns it and said not this year; the operators are branch staff we have not met | intake's completeness check enforces the RBI document list; re-KYC is a second-cycle candidate with her as sponsor |
| C6 collections summaries | a different team, vendor-held Telugu recordings, DPDP questions open | the collections head in the room for the next cycle; the dialler contract read first |
| C5 branch chatbot | no baseline: nobody has counted the calls | Kukatpally branch logs its policy calls for a month; score it next cycle with a number |
| C4 title deeds | 120 a month, reviewed by outside lawyers, no owner of the data, no baseline | a question for the legal head; likely never a Kaagaz problem |

## 7. The trap check

| Trap | Which row | How the sheet caught it |
|---|---|---|
| The demo | C4 title deeds | frequency 2; all three gates |
| The chatbot | C5 | named after a product category; measurability 1; all three gates |
| The sponsor's pet project | C6 collections (and the CRM on Day 3) | sponsorship 2: a sponsor, no operator, no product fit; the owner gate |
| No baseline | C5, C4 | the baseline gate |
| The edge case | none offered; the temptation was to avoid the compliance head by starting somewhere safe | the blast radius of intake (3) is a design condition, not a reason to pick a problem nobody reports on |

## 8. What this memo is not

Not a scope (Day 8), not a business case (Day 9), not an architecture (Days 7 and 11). It contains
no model, no product category and no target date. The numbers are Godavari's own reports and the
team leads' estimates, marked as such; the planning rate per hour is a placeholder until Day 9
measures the loaded cost. Version 2 follows Day 6's shadowing; version 3 follows Day 9's count.
