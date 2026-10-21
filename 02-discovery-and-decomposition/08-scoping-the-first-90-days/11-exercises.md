# 11 · Exercises

> Day 8 · Section 11 of 12 · [Chapter overview](README.md) · Previous: [10 · Interview questions](10-interview-questions.md) · Next: [12 · Further reading](12-further-reading.md)

---

Ten exercises in three levels. Those marked **(tested)** were run on Python 3.14.3 (October 2026) from
the chapter folder and the outputs shown are real. Use `--no-write` for every variant so that `data/`
keeps the real plan. Learning mode: write the change yourself and use an AI assistant to question your
reasoning, not to write the answer. Try first, then open.

## Level 1: warm-up

**1.1 Which list?** Put each in "will not do", "not in these 90 days" or "constraints": (a) the branch
CRM; (b) income verification from bank statements; (c) an analyst approves every file; (d) no change to
the core system's data model; (e) the branch chatbot; (f) the 6 pm batch window is not negotiable.

<details><summary>Solution</summary>

(a) will not do, signed (Day 3's reason). (b) not now, the first candidate for the next 90 days. (c)
constraint: the auditor's condition, never in the slip order. (d) will not do, a blocker's condition
restated as scope so nobody drifts into it. (e) not now, revisited at the day-90 review once Kukatpally
has counted its calls. (f) constraint (Day 5's list). (Section 05.2.)

</details>

**1.2 Does it move?** Using the blackout table in section 03.8, say whether each moves and why: (a) a
training session for Hyderabad analysts on 22 December; (b) the Mumbai cutover on 28 December; (c) the
Vijayawada wave on 12 January; (d) a labelling session on 30 November.

<details><summary>Solution</summary>

(a) No: the freeze blocks `core-change`; training is not one, and Hyderabad is outside Sankranti. (b)
Yes: it is a `core-change` inside the freeze (to 31 December), and 1 January is a closure; the first
allowed day is Monday 4 January. (c) Yes: Sankranti week blocks `go-live` and `analyst-event` at Vijayawada; it lands on 18
January. (d) The calendar file does not move it (month end blocks `go-live` and `measurement`), but
section 03.4's rule says never book labelling in the last three days of a month. A rule in prose that is
not in the data is a rule the script cannot enforce: add `analyst-event` to month end, or accept it.

</details>

## Level 2: the script

**2.1 Predict the output (tested).** Change M20's `direction` from `earlier` to `later` and run with
`--no-write --milestones <your copy>`. Where does the week-12 checkpoint land, and what does the script
say?

<details><summary>Solution</summary>

```text
  M20 checkpoint Fri 15 Jan Mon 18 Jan 13  Kaagaz FDE             COO                        Bhogi, Sankranti, Kanuma (to confirm against the 2027 notifications)
  - no checkpoint lands in week 12
```

It moves forward past the holidays to Monday 18 January, week 13, and the week-12 checkpoint disappears.
Four days before the day-90 review there is no time to act on a "no". That is why the row says
`earlier`. (Section 04.3.)

</details>

**2.2 Break it (tested).** In a copy of the adjustments file, start W6 (enablement) in week 4 "so the
team leads are involved earlier". Predict the finding, run it, then fix the plan without losing the
early involvement.

<details><summary>Solution</summary>

```text
checks:
  - W6 starts in week 4, before the week after W2 starts (week 5): Day 7's dependency rule is broken
```

The fix is not to move W2. Keep W6 in week 6 and represent the early involvement as what it is: the
champion named in week 1 and present at the skeleton demo, and the review-queue design session with the
team leads as a PLAN milestone in week 4. Early involvement is not the same as the workstream's full
effort. (Section 03.6.)

</details>

**2.3 Break it (tested).** Give the security-review row two As: the Kaagaz security lead and the CISO.
What does the script say, and who should keep the A?

<details><summary>Solution</summary>

```text
checks:
  - RACI W5: 2 people accountable; exactly one is allowed
```

The CISO. She decides the review; the Kaagaz security lead is responsible for the answers. Two As across
two companies is how "whose job was it?" starts in week 10. (Section 04.4.)

</details>

**2.4 Explain a slip (tested).** Run `--slip W3=2` (the analysts cannot label until week 4). Why does a
two-week labelling slip cost the pilot only one day, and what is the real cost?

<details><summary>Solution</summary>

```text
== what a slip of W3 +2 week(s) does ==
  M05 Fri 06 Nov -> Fri 20 Nov  +10 working days, direct
  M07 Fri 13 Nov -> Mon 23 Nov  +6 working days, knock-on (after M02, M05)
  M08 Fri 20 Nov -> Tue 24 Nov  +2 working days, knock-on (after M06, M07)
  M09 Fri 20 Nov -> Fri 04 Dec  +10 working days, direct
  M12 Fri 04 Dec -> Mon 07 Dec  +1 working days, knock-on (after M09, M10, M11)
  M13 Mon 07 Dec -> Tue 08 Dec  +1 working days, knock-on (after M12)

checks after the slip:
  - no checkpoint lands in week 4
  - no checkpoint lands in week 6
```

The pilot moves one day because the week-6 checkpoint already waited for the compliance signature and
the CISO's approval in the same week. The real cost is upstream: the skeleton demo and the week-4
readout lose their dates, and the 100-file set arrives on the day of the pilot decision with no slack to
look at the failures. The fix is a conversation with the team leads in week 1, not a later pilot.

</details>

## Level 3: judgement

**3.1 Review this AI-written plan.** [`worksheet/ai-draft-90-day-plan.md`](worksheet/ai-draft-90-day-plan.md)
was written by a general-purpose assistant given only Day 7's week grid. Find at least ten problems and
name the section that fixes each.

<details><summary>Solution</summary>

1. "All 300 branches" by day 90: productised confused with finished (02.5).
2. A waterfall with no overlap and no week-3 skeleton (02.2, 02.4).
3. The security review starts on 18 December, once a demo exists; its eight weeks end inside the RBI
   inspection (03.2, 03.3).
4. Live SOAP writes on 22 December, inside the freeze; a big-bang go-live on 15 January, a Sankranti
   holiday, with no pilot (03.7).
5. The golden set by "the QA team" in January: wrong people, too late to decide anything (03.4).
6. "Fine-tuned on 28,000 historical labelled files": Day 6 found no field-level ground truth.
7. A RAG pipeline nothing in the metrics needs (Day 7 step 4), and jargon in every milestone (04.1).
8. Training as one session after go-live (03.6).
9. A RACI by company, two As on integration, Godavari only "I" on support (04.4); owners "Kaagaz" or
   "TBD", never a Godavari name (04.1).
10. Out of scope refuses nothing anyone asked for; the CRM is missing; the chatbot is promised as a
    "quick win" (05.3, 05.5).
11. "The sandbox mirrors production": Day 6 found it three months stale (06.5).
12. "Add resources" as the only mitigation: no buffers, slip order or checkpoints (06.2, 06.4).

</details>

**3.2 Close the gap the checks missed (tested).** Section 06.3's three-week security slip left a one-day
pilot that no check caught. Add an optional `min_gap` column to the milestones: the minimum working days
after the last dependency. Give M17 a `min_gap` of 15. Rerun the plan and `--slip W5=3`.

<details><summary>Solution</summary>

In `schedule()`, after the dependency floor is applied:

```python
if floor is not None and m.min_gap:
    earliest, n = floor, 0
    while n < m.min_gap:
        earliest += timedelta(days=1)
        n += is_working_day(earliest, cal)
    if day < earliest:
        day = earliest
        m.moved_by.append(f"{m.min_gap} working days after {', '.join(m.depends_on)}")
```

(plus a `min_gap: int = 0` field and `int(r.get("min_gap") or 0)` when loading). The normal plan is
unchanged and clean: M17 on 4 January is already nineteen working days after the pilot starts. The
slip now tells the truth:

```text
  M17 Mon 04 Jan -> Mon 01 Feb  +16 working days, knock-on (after M13; 15 working days after M13; Month-end disbursement push)
  M18 Wed 06 Jan -> Thu 01 Apr  +57 working days, knock-on (after M16, M17; RBI inspection on site (expected; notice awaited))
  M19 Mon 18 Jan -> Fri 02 Apr  +53 working days, knock-on (after M18)
  M22 Fri 22 Jan -> Mon 05 Apr  +50 working days, knock-on (after M19, M20, M21)
...
  - M19: HARD DATE MISSED: due by Thu 28 Jan
```

A three-week security slip, with an honest pilot, pushes the rollout past the RBI inspection into April.
That is the sentence the COO needs in week 6, and the reason the staged approval (03.3) is worth asking
for in week 1.

</details>

**3.3 Write version 2.** The skeleton found the test copy stale (06.5). Write the paragraph that goes to
the COO at Friday's readout, in under 120 words: what changed, why, what it costs, and what you are
asking for.

<details><summary>Solution</summary>

"Plan version 2, 20 November. The core system's test copy is three months behind the live system, so
the core-system owner's month of clean test calls restarts after he refreshes it. If he can refresh it
in week 4, live writes still land on 16 December, before his freeze. If not, they land on 4 January,
and the pilot runs from 7 December with analysts keying approved files into the core system
themselves; we will measure intake and completeness time, not re-keying. The rollout dates do not
change. Our ask: a week-4 refresh, which he is considering, with your support."

</details>

**3.4 Your own 90 days.** Take the Day 7 decomposition you did for your own project, write its calendar
(holidays, freezes, audits, festivals at each site) and its milestones in the template, run the script
with `--plan` and your files, and present the COO view, the buffers and one slip to someone outside the
project. Where did they stop you?
