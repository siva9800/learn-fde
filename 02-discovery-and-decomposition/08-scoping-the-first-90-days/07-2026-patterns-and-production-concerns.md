# 07 · 2026 Patterns and Production Concerns

> Day 8 · Section 7 of 12 · [Chapter overview](README.md) · Previous: [06 · Buffers, slips and re-planning](06-buffers-slips-and-re-planning.md) · Next: [08 · Project: the Godavari 90-day plan](08-project-the-godavari-90-day-plan.md)

---

## 7.1 What practitioners do in 2026

| Pattern | What it looks like | At Godavari |
|---|---|---|
| **The plan as data** | milestones, calendar and RACI in files a script reads; charts and tables generated, never hand-drawn | four CSVs and `date_the_plan.py` |
| **A shared plan with owners on both sides** | what enterprise sales teams call a mutual action plan: one document, both companies' names on every line | on Godavari's SharePoint, because Day 6 agreed engagement notes stay on site |
| **Eval-gated checkpoints** | the pilot decision is a number on the customer's own labelled files, agreed before it is known | the week-6 question names the bar on the 200-file set |
| **Staged approvals** | a narrow approval inside the customer's walls, then the full review | M11 at week 6, M15 at week 8 |
| **Weekly re-dating** | the script rerun every Friday with actual dates; buffers first in the readout | the Friday readout (Day 29) opens with six and seven working days, or less |
| **Agents in the tooling** | an agent writes the script and the first tables; the engineer owns dates and refusals | section 08.7 |

## 7.2 What is hype

- **"Agents compress 90 days to nine."** They make code faster. They do not shorten the CISO's review,
  the analysts' labelling time, the freeze or the inspection. Godavari's critical path is almost
  entirely other people's calendars.
- **"No discovery needed; the model is general."** The model is. The stale test copy, the 18:00 batch,
  the tracker and Sankranti are not, and every date here came from discovery.
- **"Production in two weeks."** A demo, yes; the skeleton is in three. Forty analysts, a passed review
  and Godavari's own engineer releasing changes take the 90 days.
- **An AI planner that schedules it for you.** It produces a confident Gantt with no freeze, festival or
  inspection on it, because none were in its input. The calendar is the customer's knowledge and has to
  be asked for (Day 5's sponsor script asks in minute 25).

## 7.3 Production concerns

**Cost.** The real budget is FDE weeks. Every week past day 90 at full FDE time moves Day 3's ratio
toward the floor, which is why the slip order cuts scope before it extends time.

**Latency, of the calendar kind.** A one-to-two-week ticket queue, an eight-week review and a quarterly
test-copy refresh are latencies on the critical path. Start them first, run them in parallel, and never
trigger one twice (an incomplete questionnaire restarts the review).

**Scale.** Day 90 is forty analysts and two branches' measurement, not 300 branches. The parked list
says what day 91 is for.

**Security.** The plan names people, systems and weaknesses (a stale test copy, a window when nothing
can be patched). Keep it where the customer keeps such documents, share it with the RACI, and keep
customer data out of it entirely.

**Monitoring.** A plan nobody re-dates is not being followed. Rerun it every Friday; when a buffer drops
below five working days, the readout says so before the sponsor asks.
