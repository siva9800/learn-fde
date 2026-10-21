# 03 · Sequencing in Time: Risk Then Value, Against a Calendar You Do Not Own

> Day 8 · Section 3 of 12 · [Chapter overview](README.md) · Previous: [02 · The shape of 90 days](02-the-shape-of-90-days.md) · Next: [04 · Milestones, checkpoints and the RACI](04-milestones-checkpoints-and-the-raci.md)

---

## 3.1 From an order to dates

Day 7 sequenced the six workstreams risk first, value second, dependencies loosely. That order is not
reopened here. Dating adds three questions the order cannot answer:

1. **Which clocks start first?** Some work takes calendar time however hard anyone works: a review, a
   ticket queue, a month of clean test calls. Their end date is set the moment they start.
2. **Which slice reaches users first?** That is a value question, and a different one from which work
   begins first.
3. **What does the customer's calendar forbid, and when?** A freeze or a festival stops particular
   kinds of work, not all work.

## 3.2 Risk first, in dates

The three riskiest workstreams all start in week 1, which in dates means:

| Date | Milestone | Why that day |
|---|---|---|
| Wed 28 Oct | M01 the CISO's written list of what her review needs | the review's clock starts when she says what she needs |
| Thu 29 Oct | M02 access requests raised | IT's queue takes one to two weeks; the skeleton on 13 November needs the access in week 2 |
| Tue 3 Nov | M03 complete questionnaire answers | "eight weeks if the answers are complete" (Day 6, B1); incomplete answers restart the clock |
| Fri 6 Nov | M05 thirty files labelled | "correct" is defined before anyone claims accuracy |

The Part 2 plan says the questionnaire starts "from week 2". Both are true: the review starts in week 1
when the CISO states her requirements, and the formal answers go in during week 2, as the COO ordered
(Day 6). What would be wrong is the line every architecture-first plan contains: "security review once
we have something to show".

## 3.3 The long pole you do not control

The security review is this plan's long pole: the longest chain of work you cannot shorten by trying
harder. [Day 23](../../04-deploying-into-their-world/23-security-review-and-procurement/README.md) owns
how to run it; Day 8 owns where it sits in time. Do the arithmetic out loud:

- eight weeks from the week-1 meeting ends on Friday 18 December;
- the core-system release freeze starts on Thursday 17 December;
- moving to the approved AWS Mumbai environment needs the core-system owner to let the new network
  origin through his firewall, a change on his side, which the freeze forbids.

So the review's natural end falls inside a freeze that blocks the very step the review unlocks. "VPC by
week 8, cutover week 8" is a milestone that cannot happen. The plan does three things instead:

1. **Split the gate.** Ask the CISO in week 1 for a staged approval: real files from two branches on
   the machine inside the Hyderabad building by week 6 (M11, 3 December), the full review for Mumbai by
   week 8 (M15, 16 December). The first stage is smaller because nothing leaves the building, and it is
   what lets the pilot start in week 7.
2. **Put the dependent step after the freeze.** The cutover (M16) is on Monday 4 January, the first
   working day after the freeze, Christmas and Godavari's New Year closure. The pilot runs in the
   building through December.
3. **Hang nothing else on the review's last day.** Then a one-week slip costs a week of pilot, not the
   rollout (section 06 runs it).

You cannot shorten the long pole. You can start it first, split it, and keep the rest of the plan from
leaning on its final day.

## 3.4 The eval set is people's time

The golden set ([Day 14](../../03-building-the-system/14-evals-first/README.md) owns building it) is
Lakshmi's and the senior analyst's hours, booked through their team leads while they do their day jobs:

| Date | Golden set | What it unlocks |
|---|---|---|
| Fri 6 Nov (M05) | 30 files | the skeleton's ten files can be judged |
| Fri 20 Nov (M09) | 100 files | the readout quotes accuracy with its method |
| Fri 4 Dec (M12) | 200 files, the bar agreed | the pilot go or no-go has a number |
| weekly to 22 Jan | regression on every change | Godavari's people can tell if a change broke something |

Day 7 gave evals weeks 1 to 4; Day 8 extends the workstream to week 13 because the set then becomes the
regression gate. A plan that ends evals at week 4 has nobody watching accuracy during the pilot, exactly
when real files arrive that look nothing like the labelled ones. Two rules follow from the people:
never book labelling in the last three days of a month (three times the files, Day 6), and let the team
leads, not the FDE, put the hours in the analysts' week.

## 3.5 Value: the slice that saves the most hours goes first

Day 7's sample already showed the slice: two-wheeler loans are the largest group (81 of 200 files) and
SFTP scans are sent back 19 percent of the time against 55 percent for phone photos. The first slice to
reach users is two-wheeler files from SFTP scans. In intake problems the highest-value slice is usually
the highest-volume, cleanest input, because that is where the hours go and where accuracy is easiest to
prove. The same logic orders everything after it:

- **products**: two-wheeler in the pilot; gold loans in weeks 8 to 10, first to slip;
- **inputs**: SFTP scans first; Guntur's phone photos stay manual unless weeks 8 to 10 hold;
- **people**: six pilot analysts in December; the twenty-two Hyderabad analysts on 6 January, beside
  the Kukatpally pilot and the FDE; the eighteen in Vijayawada after Sankranti, on 18 January.

## 3.6 Enablement is a workstream, not an afterthought

Enablement (W6: the review queue, the tracker migration, the resubmission flow) runs from week 6 to day
90 and is accountable on Godavari's side, to the credit-ops team leads. It cannot take full effort
before week 6, because Day 7's rule makes it wait until the week after completeness and integration
have started (the script checks this; exercise 2.2 breaks it). But adoption starts with who is in the
room: the champion, the Vijayawada team lead, is named in week 1 and is at the skeleton demo on 13
November. And enablement is the workstream that reaches day 90: the pilot proves six analysts will use
the queue, the rollout proves forty will. [Day 33](../../05-working-with-the-customer/33-adoption/README.md)
owns adoption; Day 8 makes sure the plan gives it weeks and named people, not "a training session in
week 13".

## 3.7 Dependencies you do not control

| Dependency | Whose calendar | Effect | How the plan handles it |
|---|---|---|---|
| A month of duplicate-free test calls before live writes | the core-system owner (Day 6, A5) | live writes no earlier than week 7 | test calls start with the skeleton; live writes on 8 December |
| Release freeze, 17 to 31 December | the core-system owner | no change on his side | live writes by 16 December; cutover 4 January |
| Month end (28 to 30 Nov, 29 to 31 Dec, 27 to 29 Jan) | the business | no go-live; hours not comparable | no launch or measurement on those days |
| Sankranti week, 11 to 15 January; holidays 13 to 15 | the analysts' families | half of Vijayawada on leave | Vijayawada wave on 18 January; week-12 checkpoint on 12 January |
| Inspection preparation from 25 January | the compliance head | she is unavailable | every compliance sign-off before 22 January |
| RBI inspection, expected from 1 February | the regulator | nothing new goes live | the Vijayawada wave by 28 January or April |

Everything here is from Days 5 and 6 except the 2027 Sankranti and inspection dates, which the calendar
file marks "to confirm". Verify them with the team leads and the compliance head in week 2.

## 3.8 A blackout blocks a kind of work

The freeze does not stop training, and Sankranti does not stop a firewall change. Treat every blackout
as "nothing happens" and you waste weeks; ignore them and you schedule the impossible. So each blackout
in `data/godavari-calendar.csv` says what it blocks, and each milestone says what kind of work it is:

| Blackout | Blocks |
|---|---|
| public holidays, Godavari's New Year closure | all work |
| core-system release freeze | `core-change` |
| month-end push | `go-live`, `measurement` |
| Sankranti week (Vijayawada only) | `analyst-event`, `go-live` |
| inspection preparation | `compliance` |
| RBI inspection | `go-live`, `compliance`, `analyst-event` |

The Mumbai cutover, tagged `core-change`, moves out of the freeze; the Hyderabad wave, an
`analyst-event` at `hyderabad`, does not move for Vijayawada's Sankranti week. Blackouts with kinds and
milestones with kinds are most of what the script in section 08 does.

## 3.9 Key takeaways

- Start the clocks you cannot speed up on day 1: the CISO's requirements, access, labelling.
- The long pole's natural end fell inside the freeze it unlocks: split the gate, move the dependent
  step past the freeze, hang nothing else on its last day.
- Order products, inputs and people by value; schedule the eval set and enablement as people's time,
  to day 90.
- A blackout blocks a kind of work; tag both sides and the calendar becomes checkable.
