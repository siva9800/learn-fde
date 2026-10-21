# 07 · 2026 Patterns, What Is Hype, and How a Bad Pick Shows Up in Production

> Day 4 · Section 7 of 12 · [Chapter overview](README.md) · Previous: [06 · The problem statement and declining](06-the-problem-statement-and-declining.md) · Next: [08 · Project: the problem selection memo](08-project-problem-selection-memo.md)

---

## 7.1 What practitioners do in 2026

Three patterns in how teams pick problems now, each from a source in section 12, each with what it
means for a Kaagaz-sized vendor:

| Pattern | Who describes it | What it means at Godavari |
|---|---|---|
| **Qualify before you deploy.** OpenAI's team qualifies whether a problem is FDE-shaped and has a path to recurring revenue before an engineer is assigned; Ramp prefers roadmap features that serve several customers over custom builds | the 2026 ZenML panel (OpenAI, Ramp, Nominal, Dataland) | Day 3's assessment was that qualification; Day 4's sponsorship column repeats it per candidate. The chatbot would fail it even with a baseline unless two other lenders wanted it |
| **The discovery playbooks start from the human whose day gets better.** The getperspective playbooks tell FDEs to name "the specific human whose day gets better" and to validate requirements with 8 to 10 end users before building | getperspective.ai, 2026 | the operator gate. A candidate with no named operator is declined on Day 4; Day 6 interviews the operators of the one that passed |
| **Narrow and core beats broad and safe.** The deployments that reached daily use were narrow slices of a core process; broad "AI for the whole department" programmes stalled | OpenAI's 2025 interview; the practitioner's field manual | one problem, one product line, one branch (Day 7's skeleton), chosen because it is at the centre of loan origination, not because it is uncontroversial |

## 7.2 What is hype

| Claim you will hear | What is true |
|---|---|
| "Let the model find the use cases: point it at the documents and see what it can do" | The model finds document types, not costs. Every candidate it suggests still needs a volume, a baseline, an owner and an operator before it can be scored. Exploration has a place (the 2026 panel names it for early-stage customers), but it is not selection |
| "Start with a chatbot; it is the fastest way to show value" | It is the fastest way to show activity. Curiosity drives initial use; value sustains it (Atlassian). A chatbot with no baseline shows neither at day 90 |
| "Pick the safest problem first to build trust" | Trust is built by moving a number the sponsor cares about (Day 31). A safe problem at the edge of the business moves no number anyone reports |
| "Do several small ones in parallel to hedge" | With one FDE and twelve weeks, parallel means none in daily use by day 90 and no renewal case. The ranked list is the hedge: the second candidate is written down and waits |
| "Agentic workflows mean you no longer need to pick; the agent handles the whole process" | An agent across all seven candidates needs all seven baselines, all seven data owners and all seven operator groups. Selection gets harder, not easier, as the system gets more capable |

## 7.3 How a bad pick shows up, by week

A wrong choice on Day 4 does not fail on Day 4. It fails later, and each trap has its own week:

| Week | Symptom | The Day 4 cause |
|---|---|---|
| 2 | the data request has gone to a third party (the dialler vendor, the lawyers) and nobody can say when it returns | the data-owner gate skipped |
| 3 | the walking skeleton works and nobody can say what number it moved | the baseline gate skipped; measurability scored on hope |
| 6 | the pilot users are polite and do not log in on the second day | the operator gate skipped; the sponsor's problem, not theirs |
| 8 | the compliance head sees the system for the first time and stops it | blast radius scored as 2 on a problem that was a 5 |
| 10 | the sponsor asks for the demo-shaped candidate again, because the chosen one is unglamorous and slow | the "not now, because, and instead" sentences never written; nothing to point back to |
| 12 | the engineer is still on site and the renewal depends on it | the sponsorship column ignored product fit; services work was picked |
| month 4 | usage falls to zero after the FDE leaves | a curiosity problem was picked over a value problem |

Day 7's section 11 has the same table for a bad decomposition. Read together, they are the two
ways a twelve-week engagement is lost in its first fortnight.

## 7.4 The sheet as a living document

The scores on Day 4 are the best available on a Friday after one week. They change:

- **Day 6** replaces the team leads' estimates with the shadowed workflow; the hours per unit move,
  and a candidate's pain can move with them.
- **Day 9** replaces the planning rate and the monthly-report numbers with a two-week hand count.
  The ranking should not change; if it does, the memo is versioned and the COO is told why.
- **Day 20 and the pilot** produce the first evidence on the second candidate (income verification
  waits on documents intake now catches on day one). The "next slice" line gets a number.
- **Day 42** runs the same sheet on a hospital and finds the anchors need one change (the blast
  radius anchor's "customer harmed" becomes "patient harmed"), which is the test that the method
  transferred.

Keep the CSV in the engagement folder and rerun the script at each checkpoint. A ranking that is
stable from Day 4 to day 90 is evidence that the method works; a ranking that flipped is a lesson
worth a line in Day 10's document.

## 7.5 Cost, latency, scale and security at selection time

Selection is the cheapest moment to notice four production concerns, because each one is a column
or a gate:

- **Cost.** Volume a month is the inference bill's first factor. 18,000 collections calls a month
  of Telugu audio is a different bill from 1,400 files of 8 to 40 pages; the catalogue's volume
  column is where that difference first appears. Day 12 budgets it.
- **Latency.** Frequency and the workflow map together say whether the unit of work is a queue
  (intake, overnight is fine) or a conversation (the chatbot, seconds). A queue problem is far
  easier to deploy into a 2009 system with a 6 pm batch.
- **Scale.** 300 branches is the "many people" end of the frequency anchor, and it is also the
  reason Day 7's skeleton starts with one. A candidate that only makes sense at 300 branches at
  once (the chatbot) has no thin first slice.
- **Security.** Blast radius and the data-owner gate are the CISO's and the compliance head's
  columns. A candidate whose data is held by a vendor (C6) or that touches KYC directly (C3) will
  spend its first eight weeks in Day 23's questionnaire; the sheet makes that visible on Day 4.

## 7.6 Key takeaways

- 2026 practice: qualify before deploying, start from the human whose day gets better, narrow and
  core over broad and safe.
- The hype runs the other way: let the model choose, start with a chatbot, pick the safe one, do
  several in parallel, let an agent do all of it.
- A bad pick has a week in which it fails; the table maps each symptom to the gate or column
  skipped.
- The sheet lives in the engagement folder and is rerun at Days 6, 9, 20 and 42.
