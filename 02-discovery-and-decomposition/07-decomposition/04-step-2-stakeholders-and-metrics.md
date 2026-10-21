# 04 · Step 2: Stakeholders and the Metric Each Would Accept

> Day 7 · Section 4 of 16 · [Chapter overview](README.md) · Previous: [03 · Step 1: clarify](03-step-1-clarify.md) · Next: [05 · Step 3: map the inputs](05-step-3-map-the-inputs.md)

---

## 4.1 What step 2 adds to Day 5

[Day 5](../05-the-stakeholder-map/README.md) taught the map: sponsor, operators, blockers, ghost
stakeholders, and why the sponsor's version of the problem and the operators' version are both true.
Step 2 takes that map and adds one column that Day 5 did not have: **the metric each stakeholder would
accept as proof that it worked.**

The reason is practical. "Success" is not one number. The COO's success is turnaround days. The
analysts' success is fewer hours per file and fewer chases to the branch. The compliance head's success
is that no mandatory document was ever skipped. The CISO's success is a passed review and nothing
leaving India. These numbers can move in different directions: a tool that cuts turnaround by letting
the model skip a completeness check makes the COO happy and the compliance head furious. Step 2 writes
every number down so that step 4 can plan for all of them and step 5 can measure them from the first
slice.

## 4.2 The table

One row per stakeholder, five columns. The last two are the ones Day 5 did not ask for.

| Stakeholder | Role | What they want | The metric they would accept | What they fear |
|---|---|---|---|---|
| COO | sponsor | a number the board recognises | median turnaround days in the pilot branches | a demo that never reaches production |
| 40 credit-ops analysts | operators | less re-keying, fewer chases to branches | analyst hours per file; send-back rate | a tool that adds a step, or blame when it is wrong |
| Credit-ops team lead, Vijayawada | operator and champion | the tracker's job done properly | files per analyst per day | losing the tracker before the tool works |
| CISO | blocker | nothing leaves India, no vendor holding production credentials | passed security review; VPC in AWS Mumbai | a data incident with her name on it |
| Compliance head | blocker | mandatory documents never skipped | field-level accuracy on KYC fields; zero completeness misses | an audit finding caused by a model |
| Core-system owner | blocker turned partner | no duplicate records, no surprise load on a 2009 system | zero duplicates; calls inside the batch window | being the fourth vendor's victim |
| RBI auditor | ghost | documented, reviewable decisions | an audit trail per file with a human decision | automation without a human in the loop |
| Branch managers | operators, upstream | fewer send-backs from credit-ops | files accepted first time | being blamed for incomplete files |

Read the "fear" column slowly. It is where the plan's failure modes come from, and the guides score
naming failure modes unprompted. The analysts' fear ("a tool that adds a step") becomes the enablement
workstream. The CISO's fear becomes the security review starting in week two. The auditor's fear becomes
the rule that a human approves every file in the skeleton.

## 4.3 Metrics that can be measured from the first slice

A metric in step 2 has to pass one test: **could the walking skeleton measure it on ten files in week
three?** If not, it is a wish, not a metric, and you need a leading indicator that stands in for it.

| Stakeholder metric | Measurable on ten files in week three? | If not, the stand-in |
|---|---|---|
| median turnaround days | no (needs weeks of files through the real process) | time per file through the tool, and the completeness result on day one versus day four today |
| analyst hours per file | partly (time in the review page) | fields corrected per file, time to approve |
| send-back rate | partly (completeness flags on intake) | share of files flagged incomplete on day one, compared with the sample's 31 percent sent back |
| field-level accuracy | yes, against labelled files (Day 14's golden set) | none needed; this is why the eval workstream starts in week one |
| zero duplicates in the core system | yes, in the sandbox | none needed |
| passed security review | no (weeks of questionnaire) | questionnaire started, open items counted |
| audit trail per file | yes | none needed |

This table is the bridge to [Day 9](../09-success-metrics-and-business-case/README.md), which owns the
baseline and the business case. Step 2 does not measure anything; it decides what will be measured and
by whom, and it makes sure the skeleton can produce the first numbers.

## 4.4 Three stakeholders people miss

The guides say the strongest signals in the round are clarifying first and **surfacing missing
stakeholders**. On any operational problem, three kinds are routinely left off the list:

1. **The upstream producer of the input.** At Godavari, the branch managers. They are not users of the
   tool, but 31 percent of the problem is files they send incomplete, and no amount of extraction speed
   fixes that. A metric for them ("files accepted first time") turns them from a cause into a
   stakeholder with something to gain.
2. **The owner of the system you write to.** The core-system owner can veto the integration by being
   slow. He has a metric (zero duplicates) and a fear (being blamed). Give him both in writing.
3. **The ghost.** The regulator, the auditor, the insurer's TPA, the public-safety standard. Not in any
   meeting, able to stop everything. The auditor's metric (an audit trail with a human decision) is
   cheap to build in week one and impossible to retrofit in week twelve.

In an interview, naming the upstream producer and the ghost is often the moment the interviewer's notes
change from "fine" to "strong". In a city emergency-response problem (section 10), it is the dispatcher
union and the public-safety regulator. In a hospital, it is the insurer's TPA and the state medical
council.

## 4.5 When metrics conflict

Sometimes two stakeholders' metrics pull against each other, and step 2 is where you say so. Godavari's
clearest conflict: the COO's turnaround metric improves if the tool auto-approves clean files; the
auditor's metric requires a human decision on every file. You do not resolve this in step 2. You write
it down as a decision for the readout (Day 10), and you make sure the skeleton does not pre-empt it: the
skeleton has a human approve every file, because the auditor's constraint cannot move and the COO's
preference can.

The pattern generalises: **when a sponsor's metric conflicts with a blocker's constraint, the skeleton
obeys the constraint and the conflict goes on the readout agenda.**

## 4.6 What step 2 sounds like in the interview

> "Who decides whether this worked? The COO, on turnaround days. The forty analysts, on hours per file
> and how often they have to chase a branch; if the tool adds a step they will go back to their
> spreadsheet, so adoption is a metric from day one. The compliance head and, behind her, the RBI
> auditor, on whether any mandatory document was ever missed, so field-level accuracy against a
> labelled set is a hard requirement, not a nice-to-have. The security head, on whether anything leaves
> India and whether we ever hold production credentials. Whoever owns the core system we write into,
> on duplicates and load. And the branch managers upstream, because a third of the delay is files they
> send incomplete, and the fastest fix for them is to be told on day one, not day four."

Eight stakeholders, a metric each, three fears named as failure modes, the upstream producer and the
ghost included, in about seventy seconds.

## 4.7 Key takeaways

- Step 2 is Day 5's map plus one column: the metric each stakeholder would accept.
- Every metric must be measurable from the first slice, or have a stand-in that is.
- The "fear" column is where failure modes come from; name them unprompted.
- Do not forget the upstream producer, the owner of the system you write to, and the ghost.
- When a sponsor's metric conflicts with a blocker's constraint, the skeleton obeys the constraint.
