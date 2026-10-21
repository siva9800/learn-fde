# 03 · Step 1: Clarify the Goal and the Trade-off Being Optimised

> Day 7 · Section 3 of 16 · [Chapter overview](README.md) · Previous: [02 · The five steps](02-the-five-steps.md) · Next: [04 · Step 2: stakeholders and metrics](04-step-2-stakeholders-and-metrics.md)

---

## 3.1 The goal is never what the sponsor said

Sponsors speak in adjectives and round numbers: "faster", "nine days to three", "halve the response
time", "reduce spoilage". None of those is a goal you can build toward, for three reasons:

1. **The unit is missing.** Nine days measured how, from what event to what event, as a mean or a median,
   for which loans? Godavari's nine days turns out to be a median of 9.2 from "file received at credit-ops"
   to "decision recorded", across all products, including the 31 percent of files that went back to the
   branch at least once (Day 9 measures it properly; step 1 only has to ask).
2. **The date is missing.** Three days by when, and for whom? "By day 90, in two pilot branches" is a
   goal. "Three days" is a wish.
3. **The trade-off is missing.** Every speed goal is bought with something: error rate, cost, coverage,
   staff, risk. The sponsor rarely says what they are willing to spend, because nobody has asked. Your
   first job is to ask.

The output of step 1 is the goal rewritten as a sentence with a number, a unit, a date, a population,
and the trade-off named, plus the one constraint that cannot move.

## 3.2 Finding the trade-off

Almost every operational goal is one of a few pairs. Naming the pair is usually enough to find the
trade-off; naming who decides the balance is what makes it usable.

| Goal as stated | What is really being optimised | What is being traded away | Who decides the balance |
|---|---|---|---|
| "Nine days to three" (Godavari) | time from file received to decision | field-level error rate; completeness misses; analyst trust | the compliance head sets the error rate, the RBI auditor judges it |
| "Halve emergency response time" (a city) | minutes from call to arrival | coverage of low-density areas; dispatcher autonomy; false dispatches | the fire or EMS chief, under a public-safety standard |
| "Reduce cold-chain spoilage" (a logistics firm) | share of consignments within temperature range | truck utilisation; driver route freedom; cost per trip | operations head against a customer SLA |
| "Answer insurance pre-auth the same day" (the capstone hospital) | hours from discharge to insurer response | clinical accuracy of the summary; doctor time | the medical superintendent against the insurer's rejection rate |
| "Cut analyst hours per file" | labour cost | coverage of edge cases; the review queue's size | the ops head, within what the auditor allows |

Two patterns to notice. First, the person who sets the acceptable loss is **usually a blocker, not the
sponsor**. The COO wants three days; the compliance head decides how many wrong fields three days may
cost. Finding this person in step 1 is what makes step 2 complete. Second, the trade-off is often
**asymmetric**: a file that is a day slower costs rupees; a file with a wrong PAN number costs an audit
finding. The engineering consequences (deterministic rules for the asymmetric side, Day 11) start here.

## 3.3 The constraint that cannot move

Separate from the trade-off is the constraint: the line the project may not cross no matter what it
buys. At Godavari there are three, and all came from blockers in Day 5's map:

- no customer PII leaves India (the compliance head's first sentence),
- the mandatory KYC documents per RBI's Master Direction are never skipped,
- the core system's data model does not change (the core-system owner's condition for cooperating).

A constraint is not negotiated in step 1; it is written down so that every later step respects it. If
you reach step five and the skeleton violates a constraint, the skeleton is wrong, not the constraint.

## 3.4 The questions that clarify

These are the questions to ask in the first five minutes, on the job or in the interview. They are
deliberately short, and each has a reason.

| Ask | Because |
|---|---|
| "Nine days from what event to what event?" | the unit; and it reveals whether anyone has measured it |
| "Is the time mostly analysis or mostly waiting?" | it decides whether the lever is automation (analysis) or visibility and completeness (waiting); on Godavari it is waiting |
| "If we got to three days but the error rate doubled, would that be a success?" | it forces the trade-off into the open and names who decides |
| "What does the auditor (or regulator, or customer SLA) see?" | it finds the asymmetric cost |
| "What would you accept as done by day 90?" | the date and the population |
| "What has been tried before, and why did it stop?" | three vendors failed on the core system; the reason is a constraint |
| "What is not allowed, even if it would help?" | the constraints, from the people who own them |

Ask them in the sponsor's language, without technical words. You are not yet allowed to say "model".

## 3.5 Writing step 1 down

The worksheet row for step 1 (section 12 has the template) is seven cells. Filled for Godavari:

| Question | Answer |
|---|---|
| The goal in the sponsor's words | "Loan turnaround from nine days to three." |
| Rewritten as an outcome with a number and a date | Median turnaround for new loan files in the pilot branches from 9.2 days to 3 to 4 days by day 90, without raising the error rate the RBI auditor sees. |
| What is being optimised | Days from file received to decision; analyst hours per file. |
| What is being traded away, and who decides | Field-level errors and completeness misses; the compliance head decides, the auditor judges. |
| The constraint that cannot move | No PII leaves India; mandatory KYC documents; no change to the core system's data model. |
| What the sponsor would accept as done | Pilot branches at 3 to 4 days median, measured the way the operators agree, with no new audit findings. |
| Assumptions to revisit | The nine days are mostly waiting; intake and completeness are the biggest share; analysts will accept a review queue. |

The last row is the one most people leave empty. Fill it. "The nine days are mostly waiting" is a
guess at this point; Day 6's shadowing supports it, Day 9's baseline will test it, and if it turns out
to be wrong the whole decomposition changes (the lever becomes analysis speed, and extraction accuracy
becomes the trade-off's centre).

## 3.6 What step 1 sounds like in the interview

The interviewer says: "A regional lender wants loan turnaround from nine days to three. Go."

You say, in roughly ninety seconds:

> "Let me make sure I am optimising the right thing. Nine days measured from when to when, and is that a
> median or a mean? I will assume median, from file received to decision. Is the time mostly people
> analysing, or mostly files waiting for something: a missing document, a batch job, a signature? I will
> assume mostly waiting, and I will come back to that because it decides the whole approach. Then the
> trade-off: if we hit three days but the error rate the regulator sees goes up, is that acceptable? I
> would guess not, so I am optimising speed under a fixed error ceiling, and I need to know who sets
> the ceiling. Finally, what is off limits: data leaving the country, changes to the core system,
> anything the auditor would object to? I will assume all three are off limits for a lender."

Three assumptions stated, one flagged for revisiting, the trade-off named, a decider identified, the
constraints guessed and marked as guesses. No technology. Ninety seconds. That is step 1 scored at full
marks, and section 09 shows the same ninety seconds done badly for comparison.

## 3.7 Key takeaways

- Rewrite the goal with a number, a unit, a date, a population, and the trade-off named.
- Find the person who sets the acceptable loss; they are usually a blocker.
- Write the constraints that cannot move; later steps obey them.
- Write your assumptions, mark the one that would change everything, and revisit it when evidence arrives.
