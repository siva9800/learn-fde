# Stakeholder map · (customer) · (problem)

> Drawn in week 0, updated at every checkpoint, never rewritten. Verbatim versions; roles not character; nothing a person would be surprised to read. Keep the rows in `data/<customer>-stakeholders.csv` too, and run `python -X utf8 code/stakeholder_grid.py data/<customer>-stakeholders.csv data/<customer>-conflicts.csv`.

**Customer:** · **Problem (Day 4 sentence):** · **Version:** · **Author:**

## The map

Power and interest 1 to 5 (4 and 5 are high). "Stops it by": funding, veto, slowing, ignoring, input quality, a finding, or none. "Must change": yes, partly, no. Ghosts need a proxy.

| # | Who | Role | Power | Interest | Stops it by | Must change | Their version of the problem (verbatim) | What they want | The number they would believe | Engagement, and when |
|---|---|---|---|---|---|---|---|---|---|---|
| S01 | | sponsor | | | | | | | | |
| S02 | | operators | | | | | | | | |
| S03 | | blocker | | | | | | | | |
| S04 | | ghost (proxy: ) | | | | | | | | |
| S05 | | upstream producer | | | | | | | | |
| S06 | | system owner | | | | | | | | |
| S07 | | eval owner | | | | | | | | |
| S08 | | champion | | | | | | | | |
| S09 | | sceptic | | | | | | | | |
| S10 | | own-side sponsor | | | | | | | | |

Roles to check for before calling the map complete: sponsor, operators, blockers (at least two on an enterprise problem), ghost with a proxy, upstream producer, system owner, eval owner, champion (found, not appointed), sceptic, your own side.

## The map as a picture

A Mermaid flowchart: one box per row with the role, the verbatim sentence and P/I; edges for "promised", "produces for", "writes into", "speaks for", "first user".

## The constraints list (hand to Day 7 step 1)

| Constraint | Said by | When | Where it lands |
|---|---|---|---|
| | | | |

## The customer's calendar

| Fixed date | Effect on the plan |
|---|---|
| | |

## Collisions

In `data/<customer>-conflicts.csv`: a, b, what each wants, where it collides, how it is handled, who decides, when. Rule: a blocker's or ghost's condition beats a sponsor's want; the collision goes on the readout agenda.

## Who is in the readout room (for Day 10)

## Change log

| Version | What changed |
|---|---|
| week 0 | |
