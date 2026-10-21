# 08 · Dashboards for Three Audiences, Alert Fatigue, and Who Gets Paged at a Customer

> Day 19 · Section 8 of 15 · [Chapter overview](README.md) · Previous: [07 · What must never be logged](07-what-must-never-be-logged.md) · Next: [09 · 2026 patterns and production concerns](09-2026-patterns-and-production-concerns.md)

---

## 8.1 One reader, one decision, one page

A dashboard is designed backwards from the decision its reader makes with it. Grafana mechanics are the DevOps
module's ([day 3](../../../DevOps/learn-observability/day03-dashboards-grafana/notes.md)); the design question is what each
reader must be able to decide, and what to leave off so they can.

| Page | Reader | The decision | What is on it | What is deliberately not |
|---|---|---|---|---|
| `fde.html` | the Kaagaz FDE | what to fix this morning | trace completeness, cost per file per night with the ceiling, pages and pages to the model, cost by stage, latency by stage, rules that moved, upstream health, the alert list, the boundary's counters | per-analyst signals; the business case |
| `team-leads.html` | Srinivas and the Vijayawada team lead | which files and which people need attention | files, send-backs told the same day, hours before first opened, corrections per field against the golden set, correction reasons, review-band corrections per analyst, spot checks, sessions sent for a second read | rupees, tokens, model names |
| `coo-weekly.html` | the COO, every Friday | keep investing, and what to tell the board | one number (queue age), the pre-registered metrics with "not measurable yet" where true, cost per file and the month, one paragraph on the week, what is not known | everything else |

All three are static HTML written by the run: inline CSS and SVG, a native tooltip on every mark, a table beside every
chart, light and dark themes, no script, no external file, and a Content-Security-Policy that forbids loading anything.
Every value is escaped with `html.escape`, including the ones that "cannot" contain markup. The pilot machine has no
internet (the CISO's condition, Day 11), the CISO reads the source, and a page that fetches a charting library from a
CDN fails both.

## 8.2 The COO's number

The COO's sponsorship rests on one sentence: nine days to three. The page could lead with the cost line, or with
"files processed", both of which are green. It leads with the one number that moves the business case and that the
pilot can honestly measure in week two:

```text
Files waiting before an analyst opens them: 0.4 days (pilot week 2, mean, 60 files). Before the pilot: 6.4 days.
```

Day 9 found that 6.4 of the 9.1 days were files waiting in the queue, so this is the right lever. And the page says,
in the same box, that the analysts in this run are simulated and the real reading will be higher, and that the
headline metric, median turnaround, needs decided files and is not measurable yet. The table under it lists the four
metrics the COO, the compliance head and the team leads signed in week 4 (Day 9's pre-registered definitions), with
the status of each. The dashboard computes the pre-registered metric, never a convenient cousin of it (Day 9, section
09); where it cannot yet, it says so.

## 8.3 The team leads' page and the people on it

The team leads' page carries the only per-person numbers in the system: review-band corrections per analyst and
sessions sent for a second read. Day 18's agreement governs them: they go to the analyst's own team lead, never to HR,
never as a ranking, and a week is weak evidence. The page repeats that under the table, because a dashboard outlives
the meeting where its rules were agreed.

## 8.4 Alert fatigue, and the shape of a good alert

The pilot fortnight raised seven alerts. None paged anyone:

```text
page: 0
digest: 7; ceiling -> Kaagaz FDE; directory stale -> Godavari IT identity team; Kaagaz FDE copied;
latency -> Kaagaz FDE; rule moved -> Kaagaz FDE; ...; spike -> Kaagaz FDE
```

That is the design working. An alert is worth sending only if it has all four:

1. **An owner who can act**: a named role, not a channel.
2. **A threshold from a decision**: Rs 12 is Day 12's ceiling, 20 seconds is Day 12's classify budget, 36 hours is
   Day 15's snapshot rule. None was invented for the dashboard.
3. **The evidence attached**: the ceiling alert carries the trace id; the spike alert carries the three most expensive
   traces of the night.
4. **The right channel for its urgency**: a page, the 08:30 digest, or the Friday page.

The latency alert shows why the fourth matters. On Tuesday 8 December the classify stage's p95 was 26.9 seconds
against a 20-second budget. The queue was still ready by 09:00 every day; nothing waited on it. Paging someone at 02:05
for that would teach them to ignore the pager. In the digest, it is a line to read with the coffee.

## 8.5 Who gets paged at a customer

Paging at a customer is political before it is technical. Three questions decide it:

- **Whose system is broken?** The 02:00 job is Kaagaz's. The core system is Godavari's. The group sync is Godavari
  IT's. A page goes to the people who own the broken thing, with the others informed.
- **Who can act at that hour?** During the pilot, nobody at Godavari is on call for Kaagaz's software, and nobody
  should be woken for a model's cost. Godavari's application-support engineer is involved in business hours, for
  core-side failures.
- **Is it hurting the customer now?** A file over the ceiling costs Rs 2 too much; it can wait until 08:30. A queue not
  ready at 08:00 is six pilot analysts (forty after the waves) with nothing to do; that is a page.

So the pilot pages for exactly three things: the 02:00 job not finished by 07:30, a span quarantined at the boundary
(an identifier got past a validator), and the core system and the journal disagreeing. All three are checked every
night and none fired. Day 27 turns this into SLOs, error budgets and an on-call rota across the two companies, with the
hand-off to Godavari's own team at Day 28; the pilot's list is deliberately short so that the rota starts from three
alerts people trust rather than thirty they mute.

> **Telugu callback for the video.** "Okka dashboard andariki ante evvariki kaadu. FDE ki fix, team lead ki queue,
> COO ki okka number."
