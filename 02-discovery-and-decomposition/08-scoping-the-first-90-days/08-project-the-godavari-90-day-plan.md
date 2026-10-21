# 08 · Project: The Godavari 90-Day Plan, Dated From Day 7's Real Output

> Day 8 · Section 8 of 12 · [Chapter overview](README.md) · Previous: [07 · 2026 patterns and production concerns](07-2026-patterns-and-production-concerns.md) · Next: [09 · Mistakes and debugging](09-mistakes-and-debugging.md)

---

## 8.1 The brief

It is Friday of discovery week two. Day 7 left a sequenced plan in
`../07-decomposition/data/godavari-decomposition-plan.json`: six workstreams, risk first, each with a
suggested start and end week. By four o'clock you owe the COO the page he will sign, and the
engagement folder needs four things:

1. the **customer's calendar as data**: every blackout with what it blocks;
2. the **milestones as data**: dated by week and weekday, each with a Kaagaz owner, a Godavari owner,
   a line the COO can read, its dependencies and any hard date; plus the **two-company RACI**;
3. a **script** that reads Day 7's JSON and those files, dates everything, moves milestones out of
   blackouts, runs the checks, simulates slips, and writes the tables and the Gantt;
4. the **plan page** itself: the dated table, the Gantt, the "will not do" list, the parked list, the
   RACI, the slip order and the change log, in `worksheet/godavari-90-day-plan.md`.

The thinking is in the files and the page. The script exists so that the dates are reproducible, so
that the checks cannot be skipped, and so that re-dating on a Friday takes a second instead of an
afternoon.

**Files:** the four CSVs in `data/` (calendar, adjustments, milestones, RACI), `code/date_the_plan.py`,
the two generated files (`data/godavari-90-day-schedule.json`, `data/godavari-90-day-plan.md`) and the
three worksheets (the plan page, the empty template, an AI-written draft for exercise 3.1). The README's
Files table describes each.

Run from the chapter folder, on Python 3.14.3 (October 2026), with no packages, keys or downloads:

```bash
python -X utf8 code/date_the_plan.py
python -X utf8 code/date_the_plan.py --slip W5=1
python -X utf8 code/date_the_plan.py --no-write --milestones my-variant.csv
```

Each run takes about a third of a second. `--no-write` prints without touching `data/`, for
experiments; a `--slip` run never writes.

## 8.2 Part A: the inputs

The calendar and the milestones share section 03.8's idea: a blackout blocks a kind of work, and a
milestone is a kind of work. A blackout hits a milestone when the dates overlap, the sites overlap
(`all`, `hyderabad`, `vijayawada`) and the blackout blocks `all` or shares a tag with it. Three more
milestone columns carry judgement: `depends_on` (dated no earlier than the working day after the last
dependency), `direction` (`earlier` only for the week-12 checkpoint, because a handoff check that slides
into week 13 leaves no time to act on a "no") and `hard_by` (16 December for live writes; 28 January for
the Vijayawada wave), against which the script measures the buffer in working days. The adjustments
file is the only place Day 8 may disagree with Day 7, and only with a reason; the script marks each
changed workstream with an asterisk and prints the reason.

## 8.3 Part B: run it against Day 7's output

This is the real output of `python -X utf8 code/date_the_plan.py`, run against the JSON Day 7's script
wrote (one block of 22 lines elided and marked, because the plan page reproduces it):

```text
== Godavari 90-day plan: day 1 Mon 26 Oct 2026, day 90 Sat 23 Jan 2027 ==

phases (they overlap on purpose):
  P1 Discovery              weeks  1 to  4  26 Oct to 20 Nov
  P2 Walking skeleton       weeks  1 to  3  26 Oct to 13 Nov
  P3 Prototype              weeks  3 to  6  09 Nov to 04 Dec
  P4 Pilot (two branches)   weeks  7 to 10  07 Dec to 01 Jan
  P5 Rollout and handoff    weeks 11 to 13  04 Jan to 22 Jan

workstreams, dated (Day 7's order; changed weeks are marked *):
  code workstream                                     weeks  from    to     days  accountable
  W4   Integration: SFTP, tracker, SOAP create with  1 to  8* 26 Oct  18 Dec   40  K:FDE
  W5   Security review and VPC path                  1 to  8  26 Oct  18 Dec   40  G:CISO
  W3   Evals: golden set of 100 to 200 labelled fil  1 to 13* 26 Oct  22 Jan   60  G:eval owners
  W1   Extraction: pages and fields from scanned PD  2 to 10* 02 Nov  01 Jan   43  K:FDE
  W2   Completeness checks: deterministic rules per  5 to  7  23 Nov  11 Dec   15  G:compliance head
  W6   Enablement: review queue, tracker migration,  6 to 13* 30 Nov  22 Jan   35  G:credit-ops team leads

why the weeks changed from Day 7, and what the calendar takes away:
  W4: production writes need the core-system owner's month of clean test calls (week 7) and must land before the 17 December freeze
  W4: 2 working day(s) inside 'Core-system release freeze (last two weeks of the quarter)'
  W3: the golden set reaches 100 files by week 4 and 200 by week 6, then runs as the weekly regression gate until handoff (Day 14); Day 7 counted only the build
  W3: 2 working day(s) inside 'Sankranti week (half the Vijayawada analysts on leave)'
  W1: Day 7's six weeks cover the two-wheeler slice; weeks 8 to 10 add gold loans and phone photos, and that extension is the first thing to slip
  W6: Day 7 stopped enablement at the pilot; it carries the rollout to forty analysts to day 90 (Day 33)
  W6: 4 working day(s) inside 'Month-end disbursement push'
  W6: 2 working day(s) inside 'Sankranti week (half the Vijayawada analysts on leave)'

milestones (moved out of blackouts where needed):
  id  kind       planned    dated      wk  Kaagaz                 Godavari                   moved by
  M01 milestone  Wed 28 Oct Wed 28 Oct  1  Kaagaz security lead   CISO
  M02 milestone  Thu 29 Oct Thu 29 Oct  1  Kaagaz FDE             IT identity team
  M03 milestone  Tue 03 Nov Tue 03 Nov  2  Kaagaz security lead   CISO
  M04 checkpoint Fri 06 Nov Fri 06 Nov  2  Kaagaz FDE             COO
  M05 milestone  Fri 06 Nov Fri 06 Nov  2  Kaagaz FDE             Lakshmi and the senior ana
  M06 milestone  Fri 13 Nov Fri 13 Nov  3  Kaagaz FDE             Srinivas and the Vijayawad
  M07 milestone  Fri 13 Nov Fri 13 Nov  3  Kaagaz FDE             Vijayawada team lead and c
  M08 checkpoint Fri 20 Nov Fri 20 Nov  4  Kaagaz FDE             COO
  M09 milestone  Fri 20 Nov Fri 20 Nov  4  Kaagaz FDE             Lakshmi and the senior ana
  M10 gate       Wed 02 Dec Wed 02 Dec  6  Kaagaz FDE             Compliance head
  M11 gate       Thu 03 Dec Thu 03 Dec  6  Kaagaz security lead   CISO
  M12 checkpoint Fri 04 Dec Fri 04 Dec  6  Kaagaz FDE             COO
  M13 milestone  Mon 07 Dec Mon 07 Dec  7  Kaagaz FDE             Srinivas and the Vijayawad
  M14 gate       Tue 08 Dec Tue 08 Dec  7  Kaagaz FDE             Core-system owner
  M15 gate       Wed 16 Dec Wed 16 Dec  8  Kaagaz security lead   CISO
  M16 milestone  Thu 17 Dec Mon 04 Jan 11  Kaagaz FDE             Core-system owner and Goda Core-system release freeze (last two weeks of the quarter); Christmas; New Year's Day (Godavari HQ closed)
  M17 milestone  Fri 01 Jan Mon 04 Jan 11  Kaagaz FDE             COO                        New Year's Day (Godavari HQ closed)
  M18 milestone  Wed 06 Jan Wed 06 Jan 11  Kaagaz FDE             Srinivas
  M20 checkpoint Fri 15 Jan Tue 12 Jan 12  Kaagaz FDE             COO                        Bhogi, Sankranti, Kanuma (to confirm against the 2027 notifications)
  M21 milestone  Tue 12 Jan Tue 12 Jan 12  Kaagaz FDE             Godavari application-suppo
  M19 milestone  Mon 11 Jan Mon 18 Jan 13  Kaagaz FDE             Vijayawada team lead       Sankranti week (half the Vijayawada analysts on leave); Bhogi, Sankranti, Kanuma (to confirm against the 2027 notifications)
  M22 checkpoint Fri 22 Jan Fri 22 Jan 13  Kaagaz engagement lead COO

the COO's view (one line per milestone, in date order):
  [22 lines elided here: word for word the "What the COO reads" column of the milestone table in
   worksheet/godavari-90-day-plan.md, in the same order]

checkpoints and the question the customer answers at each:
  week  2 Fri 06 Nov: Is this the problem, and is this the plan you will hold us to?
  week  4 Fri 20 Nov: Do you commit to a two-branch pilot in December, on these terms and these numbers?
  week  6 Fri 04 Dec: Is accuracy on your analysts' files at the agreed bar, and are the rules and the security approval signed, so two branches start on Monday?
  week 12 Tue 12 Jan: Can your team run this without us?
  week 13 Fri 22 Jan: What do the next 90 days buy you?

hard dates and buffers:
  M14 due by Wed 16 Dec, dated Tue 08 Dec: buffer 6 working day(s)
  M19 due by Thu 28 Jan, dated Mon 18 Jan: buffer 7 working day(s)

checks:
  - all clear

wrote data/godavari-90-day-schedule.json and data/godavari-90-day-plan.md
```

## 8.4 Reading the output

1. **Day 7's order survived; four of its spans changed, each with a printed reason.** Evals and
   enablement run to day 90 because both are people's work through the pilot and rollout; integration
   runs to week 8 for the month of clean calls; extraction's extension is the first thing to slip.
2. **The freeze moved the Mumbai cutover ten working days**, from Thursday 17 December to Monday 4
   January, through three blackouts it names. That was the first draft's error; running the pilot in
   the building through December (03.3) makes it harmless.
3. **Integration has two working days inside the freeze.** The response is a rule, not a new date:
   the last change on the core-system owner's side is Wednesday 16 December.
4. **Sankranti moved two milestones in opposite directions**: the Vijayawada wave later (11 to 18
   January), the week-12 checkpoint earlier (15 to 12 January, its row says `earlier`). The Hyderabad
   wave did not move, because Sankranti week is tagged for Vijayawada.
5. **The COO's view is the plan**: twenty-two lines, none over 25 words, none using a jargon word.
6. **Two buffers, both thin, both named**: six working days before the freeze, seven before the
   inspection. They are why the slip order exists (06.4).
7. **"All clear" took two runs.** The first printed `RACI PLAN: runs past week 10 with nobody at
   Godavari responsible`: nobody at Godavari kept the plan after the FDE left. One cell fixed it. It
   also flagged a zero-day buffer on the day-90 review, whose hard date in the first draft equalled its
   own date; the date was redundant (its `compliance` tag already makes the calendar guard it) and went.

## 8.5 Part C: run a slip

```text
== what a slip of W5 +1 week(s) does ==
  M01 Wed 28 Oct -> Wed 04 Nov  +5 working days, direct
  M03 Tue 03 Nov -> Tue 10 Nov  +5 working days, direct
  M04 Fri 06 Nov -> Wed 11 Nov  +3 working days, knock-on (after M03)
  M11 Thu 03 Dec -> Thu 10 Dec  +5 working days, direct
  M12 Fri 04 Dec -> Fri 11 Dec  +5 working days, knock-on (after M09, M10, M11)
  M13 Mon 07 Dec -> Mon 14 Dec  +5 working days, knock-on (after M12)
  M15 Wed 16 Dec -> Wed 23 Dec  +5 working days, direct

checks after the slip:
  - no checkpoint lands in week 2
  - no checkpoint lands in week 6
```

A one-week slip in the security review costs one week of pilot and nothing in January, because the
staged approval and the post-freeze cutover were designed for it. The two findings say that the week-2
and week-6 decisions lost their dates, which in real life means the meetings happen on time with the
answer "not yet". Section 06.3 runs the two-week integration slip (amplified to seventeen working days
by the freeze) and the three-week security slip (a one-day pilot that no check catches). Run all three
yourself before you present the plan, so that "what if the review is late?" has an answer with dates.

## 8.6 Part D: the plan page

The script's tables and Gantt go into [`worksheet/godavari-90-day-plan.md`](worksheet/godavari-90-day-plan.md),
together with the parts no script can write: the definition of "productised", the "will not do" list
with its signatures, the parked list with revisit dates, the slip order and its "never" row, the
assumptions to confirm, and the change log. Open it now; it is the artefact the COO signs. In its
Gantt, phases and workstreams are separate sections because they answer different questions (02.3),
and the customer's calendar is its own section, drawn as critical bars, so the freeze, the month ends
and Sankranti sit visibly against the work they constrain.

## 8.7 Build it with AI

An FDE in 2026 would hand most of this chapter's code to a coding agent and keep the dates, the owners
and the refusals for themselves. The script is exactly the kind of thing an agent writes well: CSV in,
date arithmetic, a report out.

**Context to provide:** Day 7's plan JSON and its schema; the customer's calendar as you have it, with
the source of each date and the ones still to confirm; the rule that a blackout blocks a kind of work;
the milestone columns and what each means; the checkpoint weeks and the RACI rules (one A, a customer R
on anything past week 10). State the run command and that it must be standard library only.

**A strong prompt:**

> Write a Python 3.14 standard-library script that reads Day 7's workstream JSON and four CSVs: a
> calendar of blackouts (start, end, name, blocks, site), plan adjustments with reasons, milestones
> (week, weekday, kind, tags, site, depends_on, direction, hard_by, a Kaagaz and a Godavari owner, a
> one-line description, a checkpoint question) and a RACI with K: and G: columns. Date everything from
> a Monday given on the command line. A milestone lands no earlier than the working day after its last
> dependency, then moves out of any blackout that blocks one of its tags (or all work) at an overlapping
> site, in its preferred direction, never before a dependency. Measure buffers in working days. Check
> the rules in section 08.8 of my notes [paste them]. Add --slip CODE=WEEKS and report what moved and
> where a blackout amplified it. Write JSON and a Mermaid Gantt. Do not invent any date.

**What the agent typically gets right:** the parsing, the date arithmetic, the report layout, the
Mermaid syntax (mostly), the slip simulation once it is described precisely.

**What it typically gets wrong for this concept:**

| Mistake | How it shows | Fix |
|---|---|---|
| **invents the customer's calendar** | it "helpfully" adds Indian public holidays from memory, with wrong 2027 dates, or a quarter-end freeze in the wrong weeks | every date comes from the calendar file with a source; the prompt forbids invented dates; check the file against the customer, not the agent |
| **treats every blackout as blocking everything** | the Hyderabad wave moves out of Vijayawada's Sankranti week; training is moved out of the freeze | the kinds-of-work rule; test with a milestone that should not move |
| **counts calendar days, not working days** | "buffer: 8 days" across a weekend and Christmas | test the buffer function on a span you can count by hand |
| **writes CRLF files on Windows** | the generated markdown and JSON have `\r\n` and the repo's line-ending rule fails | pass `newline="\n"` to `write_text`; check with `file` (this chapter's first run had exactly this problem) |
| **overwrites outputs on experimental runs** | a learner's break-it run replaces the real plan in `data/` | a `--no-write` flag; this chapter added one after a variant run overwrote the generated files |
| **reports only some findings in a mode it added later** | the slip report prints milestone problems but drops plan-level ones (the lost checkpoints) | test every mode against a case that should produce each kind of finding; this chapter's slip mode had this bug until it was tested |
| **checks only what it was told** | a one-day pilot passes every check | ask the agent "what plan would pass all these checks and still be wrong?", then add the check it names |

The last row is the one to watch most. The agent will write a correct script that checks the rules you
gave it. Whether those rules describe a sound plan is your job, and the three-week slip in section 06.3
shows the gap.

## 8.8 How do you know it's right?

1. **Every date traces to a source.** Each calendar row has a source column; the 2027 Sankranti dates
   and the inspection date are marked "to confirm". Before the week-2 checkpoint, confirm them with the
   team leads and the compliance head.
2. **Count one buffer by hand.** From Tuesday 8 December to Wednesday 16 December is six working days
   (9, 10, 11, 14, 15, 16). If the script says otherwise, the working-day function is wrong.
3. **Force each kind of finding once.** Break the dependency rule (exercise 2.2), give a RACI row two
   As (exercise 2.3), start on a Tuesday, and slip integration past the freeze. Each should produce its
   own message. A check you have never seen fire is a check you do not know works.
4. **Test a milestone that should not move.** The Hyderabad wave must not move for Vijayawada's
   Sankranti week. If it does, the site logic is wrong.
5. **Read the COO view aloud to someone outside the project**; rewrite any line they ask about.
6. **Every asterisk has a reason** a reviewer would accept; no workstream changed without one.
7. **Run three slips and cost each in a sentence**, then ask what plan would pass and still be wrong.
8. **Check the files**: LF line endings, UTF-8, the Gantt renders in a Mermaid preview.

**Review checklist:**

- [ ] day 1 is a Monday; the day-90 review date is stated; unconfirmed calendar dates are marked
- [ ] discovery and prototype overlap; the pilot is gated; the skeleton is in week 3 with its access and labelling in weeks 1 and 2
- [ ] the security review starts in week 1 and nothing but its own next step hangs on its last day
- [ ] evals and enablement run to day 90
- [ ] every milestone has two owners and a plain COO line; checkpoints in weeks 2, 4, 6 and 12, each with a question
- [ ] one A per RACI row, a customer R on every row past week 10, a RUN row
- [ ] buffers in front of hard dates; a slip order with a "never" row; three slips run and costed
- [ ] the "will not do" list: four to six lines, reasons, names, signed in week 2
- [ ] the script runs clean; the generated files are LF

## 8.9 What goes into the engagement folder

The signed plan page goes to Day 9 (a number on each milestone), Day 10 (the discovery document) and Day
29 (the Friday readout opens with the buffers). The calendar is reused by Day 9's baseline, Day 26's
deploys and Day 27's on-call; the milestones by Days 20, 23 and 28; the RACI's RUN row by Days 27 and 28;
the "will not do" list by Days 10 and 32.

## 8.10 Extend it

- Add a `min_gap` column (working days after the last dependency) and give M17 a minimum of 15 after
  M13. Rerun `--slip W5=3`. The one-day pilot should now be a finding (exercise 3.2).
- Add a `--confirm` mode that lists every calendar row whose source contains "assumed" or "to confirm",
  so the week-2 email to the compliance head writes itself.
- Write a Friday mode: read actual dates for the milestones done so far, re-date the rest from them,
  and print the buffers (the weekly rerun in section 07).
