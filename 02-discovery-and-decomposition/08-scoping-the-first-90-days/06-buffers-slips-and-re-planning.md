# 06 · Buffers, What Slips First, and Re-planning When the Sandbox Is Stale

> Day 8 · Section 6 of 12 · [Chapter overview](README.md) · Previous: [05 · What you will not do](05-what-you-will-not-do.md) · Next: [07 · 2026 patterns and production concerns](07-2026-patterns-and-production-concerns.md)

---

## 6.1 Something will slip

Every 90-day plan is wrong by week three; that is what "the long pole is outside your control" means.
The question is whether, when it slips, everyone already knows what moves and what does not. Three
tools do that: **buffers** (measured slack), **the slip order** (what is cut first, agreed in week 2)
and **re-planning** (the plan versioned, not rewritten, when a fact changes).

## 6.2 Buffers belong in front of hard dates

A buffer is the working time between when something is planned and when it absolutely must happen.
Spreading "20 percent contingency" across every task hides it where nobody can see it being used. Put
buffers in front of the hard dates instead, and measure them:

| Milestone | Dated | Must happen by | Buffer | What the hard date is |
|---|---|---|---|---|
| M14 live writes to the core system | Tue 8 Dec | Wed 16 Dec | 6 working days | the freeze starts on 17 December |
| M19 the Vijayawada wave | Mon 18 Jan | Thu 28 Jan | 7 working days | month end from 27 January, then the RBI inspection from 1 February |

Those are the only two hard dates the milestones file needs. Others are enforced by the calendar
itself: the day-90 review is tagged `compliance`, so if it slips past Friday 22 January it runs into
the compliance head's inspection preparation and then the inspection, and the script will say so.

Six and seven working days are thin (the script flags anything under five). They are acceptable
because the slip order says what is sacrificed to protect them, and because the staged approval took
the security review off the critical path (03.3).

## 6.3 What a slip actually does

The script's `--slip` option moves every milestone of one workstream by some weeks and recomputes
everything that depends on it, through the calendar. Three runs on the real plan (full output in
section 08):

**The security review is one week late** (`--slip W5=1`). The CISO's meeting, the questionnaire, the
interim approval and the full approval all move a week. The pilot go or no-go moves to 11 December
and the pilot starts on 14 December. The Mumbai cutover does not move, because it was already after
the freeze. Cost: one week of pilot. The checks flag "no checkpoint lands in week 2" and "in week 6": both
meetings waited for a slipped dependency. In real life a checkpoint stays on the calendar and its answer
becomes "not yet, and here is the new date"; the flag says a decision has lost its date.

**Integration is two weeks late** (`--slip W4=2`), the stale-sandbox case in section 6.5:

```text
== what a slip of W4 +2 week(s) does ==
  M02 Thu 29 Oct -> Thu 12 Nov  +10 working days, direct
  M14 Tue 08 Dec -> Mon 04 Jan  +17 working days, direct, amplified by 7 working day(s) (Core-system release freeze (last two weeks of the quarter); Christmas; New Year's Day (Godavari HQ closed))
  M16 Mon 04 Jan -> Tue 05 Jan  +1 working days, direct (after M14, M15)
  M21 Tue 12 Jan -> Wed 27 Jan  +7 working days, direct (Republic Day)
  M22 Fri 22 Jan -> Thu 01 Apr  +48 working days, knock-on (after M19, M20, M21; Compliance head preparing for the RBI inspection; RBI inspection on site (expected; notice awaited))

checks after the slip:
  - M14: HARD DATE MISSED: due by Wed 16 Dec
  - M21: after day 90 (23 Jan)
  - M22: after day 90 (23 Jan)
```

Read the second line slowly. A two-week slip became a seventeen-working-day slip, because the live
writes fell into the freeze and waited for it to end. That is **slip amplification**: a blackout turns
a small delay into a large one. Then read the last line. The day-90 review moved to 1 April, because
it depended on M21 (Godavari's engineer releasing a change on his own), M21 slipped into the
compliance head's preparation week, and the review cannot be held without her until the inspection
is over.

That last line is partly a real risk (live writes after the freeze shorten the pilot's useful
measurement) and partly a flaw: the day-90 review needs to report whether M21 happened, not wait for
it. Telling those apart is the skill; section 6.5 fixes both.

**The security review is three weeks late** (`--slip W5=3`). The interim approval moves to 24
December, the pilot go or no-go to 28 December, the pilot start to 4 January, and the pilot results
milestone to 5 January. The script flags the same two lost checkpoints and nothing else. Look at the
dates it did not flag: the pilot started on 4 January and its results are due on 5 January. The pilot
ran for one day. The script checks what it is told to check, and nobody told it that a pilot needs at
least three weeks between start and results. That is exercise 3.2, and it is the most useful thing in
this section: **a run with no findings means the checks passed, not that the plan is sound**.

## 6.4 The slip order, agreed in week 2

When something slips, something else gives. Agree in advance what, in this order, and put it in the
plan the COO signs:

| Order | What gives | What it costs |
|---|---|---|
| 1 | gold loans (W1's weeks 8 to 10), planned as an extension | the second product waits for the next 90 days |
| 2 | Guntur's phone photos, the hardest input | they stay manual in the pilot |
| 3 | the Vijayawada wave moves after day 90, but not after 28 January | day 90 reports twenty-two analysts, not forty |
| 4 | the pilot shortens, never below three weeks of measurement | a smaller sample in the pilot results |
| never | the audit trail, an analyst's approval on every file, the compliance head's signature before rules run, the security gate, the November baseline | |

The "never" row matters as much as the order. Under pressure, people first offer to cut what makes the
system trustworthy ("the audit trail can come after the pilot"). Saying in week 2 that those are not on
the table means the FDE does not have to win that argument in December.

## 6.5 Re-planning when the sandbox turns out to be stale

Day 6 found it and Day 7 expected it: the core system's test copy is refreshed quarterly, its business
rules are three months behind the live system, and only field validation can be trusted there. Suppose
the week-3 skeleton confirms the worst case. On Friday 13 November the ten files go in cleanly, but on
Monday the core-system owner reports that the live system would have rejected three of them under a
rule added in September. The month of clean test calls he requires does not count calls the live system
would reject, so his month restarts after he refreshes the test copy, which he can do in week 5.

That is the `--slip W4=2` run. The re-plan, in the order an FDE would work through it:

1. **Find the real hard date.** Live writes land by 16 December or wait until 4 January; with a
   week-5 refresh the month of clean calls ends in week 9, inside the freeze.
2. **Ask for the one thing that would rescue it.** A refresh in week 4 instead of week 5, so that the
   month ends on 16 December. Ask the core-system owner with the date and the reason, and give him a
   way to say no.
3. **Decide what the pilot does without live writes.** It runs in assisted mode: the system extracts
   and checks, the analyst approves, and the analyst still keys the approved fields into the core
   system. The pilot then measures intake and completeness time and send-backs, but not re-keying.
   Say that in the pilot results milestone's line, so the number is not oversold.
4. **Fix the dependency that was wrong.** The day-90 review depends on the waves and the handoff check,
   not on M21. Remove M21 from M22's `depends_on` and rerun: the review stays on 22 January and reports
   M21's status instead of waiting for it.
5. **Version the plan and say so.** Version 2, dated, with one paragraph: what changed, why, what it
   costs, and what the customer is being asked for. It goes to the COO at the next Friday readout
   ([Day 29](../../05-working-with-the-customer/29-communication-for-engineers/README.md) owns the
   readout, [Day 30](../../05-working-with-the-customer/30-delivering-bad-news/README.md) owns how to
   deliver it).

Version 1 stays in the change log, because the COO will ask "what did we originally say?" and the
honest answer is a line in a table.

## 6.6 Key takeaways

- Put buffers in front of hard dates and measure them; Godavari has six working days before the freeze
  and seven before the inspection.
- Blackouts amplify slips: a two-week integration slip became seventeen working days at the freeze.
- A run with no findings means the checks passed, not that the plan is sound; the three-week security
  slip left a one-day pilot that no check caught.
- Agree the slip order in week 2, including the "never" row: trust features are not buffer.
- Re-plan by finding the hard date, asking for the one rescue, choosing the degraded mode, fixing wrong
  dependencies, and versioning the plan.
