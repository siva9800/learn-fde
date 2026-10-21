# 10 · Interview Questions

> Day 8 · Section 10 of 12 · [Chapter overview](README.md) · Previous: [09 · Mistakes and debugging](09-mistakes-and-debugging.md) · Next: [11 · Exercises](11-exercises.md)

---

Twelve questions in the forms they take in FDE loops: the hiring-manager screen ("walk me through your
first 90 days"), the follow-ups inside the decomposition round, and the capstone-style defence (Day 46).
Answer out loud first, then compare.

**Q1. Walk me through your first 90 days on a new customer engagement.**

Discovery in weeks 1 to 4 and a prototype in weeks 3 to 6, overlapping on purpose, a pilot in weeks 7 to
10, and in daily use by day 90, which is the practitioner convention. Day 1 and 2 are access. Week 1
starts every clock I cannot speed up: the security review, access tickets, the customer's experts
labelling examples. A walking skeleton by week 3. Checkpoints at weeks 2, 4, 6 and 12, each with a
question the customer answers. And in week 2 a signed list of what I will not build. (Sections 02, 03.)

**Q2. Why overlap discovery and the prototype? Isn't that building before you understand?**

Some discovery questions can only be answered by building: does the system of record accept the write,
will the operators use a queue, how accurate is extraction on their worst documents. A thin slice in
week 3 answers those while discovery is still open, and the answers go into the week-4 readout. What I
gate is decisions, not work: the pilot starts only when the week-6 checkpoint says yes. (Section 02.2.)

**Q3. How do you turn a sequenced list of workstreams into a dated plan?**

Three questions the order cannot answer: which clocks start first (reviews, tickets, people's time),
which slice reaches users first (value), and what the customer's calendar forbids. I date every
milestone against the calendar, where each blackout says what kind of work it blocks: a release freeze
blocks changes to their system, not training. Then I measure the buffer in front of every hard date.
(Section 03.)

**Q4. The security review takes eight weeks and is outside your control. How do you plan around it?**

Start it in week 1, answer the questionnaire completely in week 2 because incomplete answers restart the
clock, and ask for a staged approval: a narrow pilot inside their walls early, the full environment
later. Then make sure nothing but its own next step hangs on its last day. At a lender I worked the
arithmetic and the natural end fell one day into a quarter-end freeze, so the cutover went after the
freeze and the pilot ran on-prem through December. (Section 03.3.)

**Q5. What goes on a "will not do" list, and why write it down?**

Four to six things someone actually asked for, or a blocker's condition restated as scope, each with a
reason and the name of who agreed: the branch CRM, collections summaries, any change to the core data
model, anything that sends PII outside India. Written and signed in week 2, it protects the buffer, lets
the sponsor say no to his own people with his own signature, and stops my own sales team promising it at
renewal. Said only in a meeting, it is reopened every Friday. (Section 05.)

**Q6. What is the difference between "will not do", "not now" and a constraint?**

"Will not do" is refused for this engagement and changes only by a new written agreement. "Not now" is
parked with a reason and a revisit date. A constraint is a condition the work must meet, set by a
blocker, and is not scope at all. Mixing them makes the refusals look negotiable and the constraints
look optional. (Section 05.2.)

**Q7. What makes a good milestone?**

Observable by someone outside the team, dated to a day, owned by one person on each side, written in
words the sponsor would not need explained, and something later depends on it. "SOAP integration
complete" fails three of those; "approved files are written into the live core system with no
duplicates" passes. (Section 04.1.)

**Q8. How do you build a RACI across two companies?**

One accountable person per row, placed where the decision sits, which is often the customer: the
compliance head for the rules she signs, the CISO for the review. A named customer person responsible
on anything that runs past the handoff, or on day 91 it belongs to nobody. Roles, never "the vendor" or
"the customer". And a row for running it after day 90. (Section 04.4.)

**Q9. Your plan is slipping. What gives first?**

Whatever we agreed in week 2. On a lending engagement: the second product first, then the hardest input
type, then the last rollout wave, then a shorter pilot but never below a measurable length. Never the
audit trail, the human approval on every file, the compliance sign-off or the security gate. Those are
constraints, not buffer. (Section 06.4.)

**Q10. What is slip amplification?**

A small delay that becomes a large one because it falls into a blackout. A two-week integration slip
pushed live writes into a two-week freeze plus holidays and became seventeen working days. It is why
buffers go in front of hard dates and why I run slip scenarios before presenting a plan. (Section 06.3.)

**Q11. The sandbox you planned around turns out to be stale. What do you do?**

Find the real hard date (live writes before the freeze), ask for the one thing that would rescue it (an
earlier refresh, with a date and a reason), decide the degraded mode (an assisted pilot where analysts
still key the record, and say so in the results), fix any dependency that was wrong, and version the
plan with one paragraph to the sponsor at the next readout. Version 1 stays in the change log.
(Section 06.5.)

**Q12. A coding agent can write the scheduling script. What do you still own?**

The calendar, because the agent will invent holidays and freezes; the kinds of work each blackout
blocks; the dependencies; the refusals; and the question of what plan would pass every check and still
be wrong. On my own script, a three-week security slip left a one-day pilot and no check fired. (Sections
06.3, 08.7.)
