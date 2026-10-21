# 09 · Common Mistakes and Debugging

> Day 8 · Section 9 of 12 · [Chapter overview](README.md) · Previous: [08 · Project: the Godavari 90-day plan](08-project-the-godavari-90-day-plan.md) · Next: [10 · Interview questions](10-interview-questions.md)

---

Each row is **symptom, cause, fix**, with the section that explains it.

## 9.1 On the engagement

| Symptom | Likely cause | Fix |
|---|---|---|
| Week 8: the security review is "still in progress" and the pilot cannot start | the review was started "once we had something to show" | start it in week 1; ask for a staged approval for the pilot (03.2, 03.3) |
| Week 3: the skeleton demo slips a week | the access tickets were raised in week 2 | raise access on day 4; the skeleton's date is set by tickets, not code (02.4) |
| A milestone lands on the first day of the freeze | the plan was drawn from week numbers, not dated against the calendar | date every milestone against the calendar; move the dependent step past the freeze (03.3, 08.4) |
| Week 9: three days lost to a "quick prototype" of something nobody planned | no signed "will not do" list, so the request could not be declined by pointing at anything | the list, signed at the week-2 checkpoint, before the demo (05.1, 05.5) |
| The pilot has no accuracy number at the go or no-go | the eval workstream ended at week 4, or was never booked in the analysts' week | evals run to day 90; the team leads book the labelling hours (03.4) |
| Day 85: the analysts keep the tracker open beside the queue | enablement planned as a training session in week 13 | enablement from week 6, a champion from week 1, the tracker written back to (03.6) |
| Day 91: nobody at the customer can release a change | handoff treated as an event, not a sequence of things owned from week 1 | the RUN row, the application-support engineer from week 2, M21 in week 12 (04.5) |
| A one-week slip becomes three weeks | a milestone with a hard date had no buffer in front of it, and the slip fell into a freeze | measure buffers before hard dates; run the slip in advance (06.2, 06.3) |
| The sponsor hears about the slip from someone else | no slip order, so the FDE tried to absorb it quietly | the slip order agreed in week 2; the buffers open the Friday readout (06.4, 07.1) |

## 9.2 In the plan and the script

| Symptom | Likely cause | Fix |
|---|---|---|
| `--start must be a Monday` | day 1 given as a Tuesday | weeks are computed from day 1; pass the Monday |
| `X starts in week N, before the week after Y starts` | an adjustment broke Day 7's dependency rule | move the start, or represent the early work as a milestone in another workstream (exercise 2.2) |
| `RACI W5: 2 people accountable` | two As in a row, often "both companies" | one A, where the decision sits (04.4) |
| `runs past week 10 with nobody at Godavari responsible` | the customer half of a long-running row is empty | a named Godavari R; the PLAN row needed one on the first run (08.4) |
| `HARD DATE MISSED` | a slip or a blackout pushed a milestone past its `hard_by` | re-plan: the rescue request, the degraded mode, the dependency check (06.5) |
| A milestone moves for a festival at the other site | its `site` is `all` | give site-specific milestones their site |
| No findings, but the plan looks wrong | the checks cover only what they were told | ask what would pass and still be wrong; add the check (06.3, exercise 3.2) |
| The generated files fail the repo's line-ending rule | `write_text` on Windows writes CRLF | `newline="\n"` (08.7) |

## 9.3 A routine for a plan that feels wrong

1. Read the COO view aloud. Any line you would not say to him is a problem.
2. Find the long pole and check what hangs on its last day.
3. Lay the calendar over the milestones by hand for the freeze, the festivals and the inspection.
4. Check every row past week 10 for a customer name.
5. Run three slips and cost each in a sentence.
6. Re-read the "will not do" list and ask whether each line refuses something someone actually wants.
