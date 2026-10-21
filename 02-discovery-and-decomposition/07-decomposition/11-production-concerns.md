# 11 · Production Concerns: How a Bad Decomposition Shows Up Months Later

> Day 7 · Section 11 of 16 · [Chapter overview](README.md) · Previous: [10 · Two more problems](10-two-more-problems.md) · Next: [12 · Project: decompose Godavari](12-project-decompose-godavari.md)

---

A decomposition is not a document that gets filed. It is the set of bets the engagement runs on, and
every bet that was wrong or missing comes due, usually between week eight and month four. This section
is the list of ways it comes due, so that you recognise the symptom and trace it back to the step that
was skipped.

## 11.1 The symptom table

| Month | What you see | Which step was skipped or wrong | What it costs |
|---|---|---|---|
| week 3 | the demo works on the five files you chose; on the analysts' ten it fails on page order | 3 (shape: no page index) and 5 (slice chosen to be easy) | two weeks adding classification that should have been a workstream |
| week 6 | the integration "just needs the sandbox", and the sandbox was refreshed last quarter with a broken WSDL | 3 (freshness and access of the sandbox), 4 (integration not first) | four weeks of code written against the wrong interface |
| week 8 | the security questionnaire arrives: 212 questions; the CISO's review takes eight weeks; the pilot cannot run in their account until week 16 | 2 (the CISO's metric), 4 (security review not started in week 2) | the demo lives in a vendor sandbox past the day-90 checkpoint; the sponsor's patience ends first |
| week 10 | the analysts in Vijayawada use the tool for a day and go back to the tracker: it does not show branch colour codes and it makes them enter status twice | 3 (the tracker is the real state), 2 (the analysts' fear), 4 (enablement not planned) | adoption collapses; the sponsor hears "the analysts do not like it" |
| week 10 | the compliance head sees a file where the model marked a missing address proof as "present" | 1 (the trade-off's asymmetry), 3 (the rules as deterministic code) | a governance conversation that should have happened in week two; possibly the engagement |
| week 12 | the COO asks "how many hours did we save?" and nobody can answer, because the baseline was never sampled | 2 (metrics measurable from the first slice), 3 (data that does not exist: timestamps) | the business case (Day 9) has no before; the renewal conversation has no number |
| month 4 | a branch manager in Guntur sees a Kukatpally file in the review queue | 3 (AD groups: who may see what) | an incident the CISO must report; retrofitting group filtering into every query (Days 15, 22) |
| month 4 | production runs two CreateApplication calls on a timeout and the core system has duplicates; the core-system owner stops answering email | 3 (no idempotency), 4 (integration risk retired late) | the relationship with the one person who could have made the integration work |
| month 5 | the second loan product (gold loans) has a different checklist and different forms; the extraction was tuned on two-wheeler forms and nobody wrote down that it was | 5 (the stubbed list was not written) | the "widen to all products" phase is a rebuild, and nobody warned the sponsor |
| month 6 | the auditor asks for the reasoning behind a decision on a file; the system has the model's output and no record of who approved it or what they changed | 2 (the ghost's metric: an audit trail with a human decision) | an audit finding; the thing the compliance head feared |

Every row has the same shape: a question that costs a conversation in week two and a rewrite, an
incident, or a relationship later. The guides describe the job-side failure exactly as the interview
failure: "a prototype built for the sponsor's version of the problem that the operators never use".

## 11.2 Why the costs grow

Three mechanisms turn a skipped step into a month-four problem:

1. **Code accumulates on the assumption.** Every week of building against "the sandbox works" or "the
   files are single documents" adds code that must be changed when the assumption breaks. Risk-first
   sequencing (step 4) exists to keep that pile small.
2. **People form opinions.** The analysts who tried the tool in week ten and went back to the tracker
   have decided. The core-system owner who got duplicates has decided. Opinions formed on a bad first
   contact are harder to change than code (Day 33 covers the operator who will not switch).
3. **Calendars run out.** The security review, audit month, quarter-end freezes (Day 5) are fixed. A
   review started in week eight ends in week sixteen whatever you do; the day-90 checkpoint does not
   move.

## 11.3 The decomposition as a living document

A good decomposition changes, on purpose, at known moments. The worksheet is versioned, not rewritten
(Day 10's rule for the discovery document applies):

| Moment | What is revisited | Typical change |
|---|---|---|
| end of week 1 (access and reality, Day 6) | step 3's access and freshness columns | the sandbox is stale: integration risk goes up, a WSDL stub is added |
| end of week 3 (the skeleton demo, Day 20) | step 1's assumptions; step 5's expected failures | "mostly waiting" confirmed or not; Telugu fields become a workstream or stay manual |
| end of week 4 (discovery closes, Day 10) | everything, signed | the readout's four changes |
| week 8 (the security review's first response) | step 4's order; step 1's constraints | VPC confirmed or on-prem required; model endpoint allowlist known |
| day 90 | step 2's metrics against the baseline | the business case (Day 9) and what Day 37 will measure |

If the decomposition has not changed by week four, nobody is reading it against reality.

## 11.4 Cost, latency, scale, security: where they enter

This chapter does not size infrastructure; Parts 3 and 4 do. But each of the usual production concerns
has a place in the decomposition, and leaving it out is how it surprises you:

| Concern | Where it enters the five steps | Godavari |
|---|---|---|
| cost | step 1 (what is traded) and step 2 (the sponsor's number) | cost per file is a condition in the business case; the skeleton logs it from file one |
| latency | step 3 (freshness) | the nightly SFTP batch bounds what "same day" can mean; nobody promises minutes |
| scale | step 5 (the slice) and step 4 (what widening costs) | 2,400 files a month across 300 branches is small; the scale risk is 300 branches' access rules, not throughput |
| security | step 1 (constraints), step 2 (the CISO), step 4 (the review first) | the questionnaire in week two; masked files; no vendor-held production credentials |
| monitoring | step 2 (metrics measurable from the first slice) | per-file time, corrections, flags, from the skeleton's first day; Day 19 builds the dashboard on the same numbers |

## 11.5 Key takeaways

- A skipped step comes due as a symptom months later: page order, a stale sandbox, a late security
  review, analysts going back to the tracker, a cross-branch leak, duplicates, no baseline, no audit trail.
- The costs grow because code accumulates on assumptions, people form opinions, and calendars do not move.
- The decomposition is revisited at known moments and versioned; if it has not changed by week four,
  nobody is checking it against reality.
