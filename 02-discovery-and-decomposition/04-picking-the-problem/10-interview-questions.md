# 10 · Interview Questions

> Day 4 · Section 10 of 12 · [Chapter overview](README.md) · Previous: [09 · Mistakes and debugging](09-mistakes-and-debugging.md) · Next: [11 · Exercises](11-exercises.md)

---

Twelve questions in the forms they take in FDE loops: the hiring-manager screen ("how would you
choose?"), the client-simulation round (the sponsor who wants the chatbot), and the opening minutes
of the decomposition round, where the interviewer sometimes hands you several problems and watches
which one you take. Answer out loud first, then compare. Section numbers point to the explanation.

## The method

**Q1. A customer arrives with seven problems and twelve weeks. How do you choose?**

Three passes. First, turn the list into a catalogue: for each candidate, the volume a month, the
hours a unit, who raised it, and what the people who do the work said; I add anything the floor
shows that the room did not mention. Second, three gates before any scoring: a baseline the
customer already has, a data owner inside the customer, and an operator who asked for it. A
candidate that fails a gate is declined for that reason this cycle. Third, score the rest on
frequency, pain, measurability, data availability, blast radius and sponsorship against written
anchors, weight them, and check that the winner survives other weightings. Then I write one
sentence the sponsor and the operators both sign, and a "not now, because, and instead" line for
each of the others. (Sections 03, 04, 06.)

**Q2. What do "frequent, painful, measurable" mean in practice, and where does the phrase come from?**

Atlassian's forward deployed engineering playbook: pick problems that are frequent, painful and
measurable, then work backwards to the AI needed. Frequent: it happens every day to many people in
the core process, not twice a month. Painful: it costs hours, rupees, errors or waiting that someone
already complains about. Measurable: a number exists today, counted by the customer, that the
system would move. Work backwards: only after those three do I ask what AI, if any, the problem
needs; some of it is deterministic code and some is a form change. (Section 02.1.)

**Q3. And OpenAI's version?**

Three parts from the published interviews. Value: problems worth tens of millions to low billions to
the customer, because only at that size does the customer put its experts in the room and renew
without argument. Core, not edge: the deployments that worked were high-stakes use cases at the
centre of the business. FDE-shaped with a path to recurring revenue: qualified before an engineer
is assigned, and services work declined even when it pays. For a small vendor I scale the value
test: the problem must cost the customer clearly more than the subscription, measured in hours
first. (Sections 02.2, 02.4.)

**Q4. Why is "what can the model do?" the wrong first question?**

It produces a list of document types. Every place a document exists becomes a candidate, ordered by
what the model finds easy, not by what the work costs. The right first question is where people
wait, re-key or rework, which produces a list of costs. At a lender, the model-first list had seven
items; the workflow-first view showed three of them were points on one line that started at
intake. (Section 03.)

**Q5. Why gates rather than just scoring everything?**

Because some problems are not low-scoring; they are not scoreable yet, and treating them as
scoreable hides the reason. A problem with no baseline cannot be proven at day 90 whatever its
pain. A problem whose data a vendor holds spends eight weeks in procurement. A problem no operator
asked for is the prototype nobody runs. A failed gate gives me a sentence ("not now, because there
is no baseline; count it for a month") that a score never would. (Section 04.4.)

## The traps

**Q6. What is the demo trap, and how do you catch it?**

A problem that is real, that the model does something visibly clever with, and that happens rarely.
The tell is "the board loved it". It loses on frequency, and usually on measurability and data
because rare work is rarely timed and often outsourced. At the lender it was title-deed review:
a striking demo, 120 a month, done by outside lawyers. I showed it after the valuable thing was in
daily use. (Section 05.1.)

**Q7. What is the chatbot trap?**

A solution wearing a problem's clothes: the candidate is named after a product category, not a
cost. "A chatbot for the branches" is not a problem; "branch staff phone head office and wait" might
be, and nobody had counted it. It fails the baseline gate. Day 7's method calls the same thing the
"LLM with RAG in minute one" anti-pattern; the chatbot trap is that anti-pattern arriving from the
customer's side of the table. The fix is to rename it as a cost, score that, and offer the count
that would make it scoreable. (Section 05.2.)

**Q8. The sponsor's favourite problem scores badly. What do you say?**

The number, the reason and the alternative, in ranking order so that he hears "second" before he
hears "no". "Intake is 1,400 files a month, 2,100 analyst hours, a third of files reworked, and you
already report the numbers it would move. The chatbot has no count yet. If one branch logs its
policy calls for a month, we will know whether it is the second thing or the fifth, and it comes
back with a baseline." A sponsor who hears his list has an order has been listened to. (Sections
06.4, 06.5.)

**Q9. What is the sponsor's pet project, and why is it more dangerous than the demo trap?**

A problem raised in the second call with more energy than the rest, with a sponsor but no operator
and no product fit; at the lender, collections summaries and the branch CRM. It is more dangerous
because it comes with budget: saying yes is easy, pays this quarter, and is the services trap from
Day 3, the engineer who cannot leave. It loses on the sponsorship column, which needs three things,
not one. (Section 05.3.)

## The sheet and the engagement

**Q10. A candidate scores second-highest on your sheet and you still do not pick it. Defend that.**

The tracker at the lender: 80 out of 100, failed the operator gate. Both facts were right. It is
where the pain of intake lives, and the analysts do not want it replaced; they want to stop running
two systems. So it was neither picked nor dropped: it became a constraint on the winner. Intake
reads the tracker before replacing anything and writes status back, or the analysts keep the
tracker open and the pick fails in month four. The sheet ranks; the memo decides. (Section 08.4.)

**Q11. How does a bad pick show up later, and when?**

Each skipped gate has its week. Week two: the data request is with a third party. Week three: the
skeleton works and nobody can say what number it moved. Week six: the pilot users are polite and do
not log in. Week eight: the compliance head sees it for the first time and stops it, because blast
radius was under-scored. Week ten: the sponsor asks for the demo-shaped candidate again because the
"not now" lines were never written. Month four: usage falls to zero after the engineer leaves,
because a curiosity problem was picked over a value problem. (Section 07.3.)

**Q12. What does the one-sentence problem statement contain, and what does it leave out?**

Four parts: the unit of work, the cost as a number the customer already has, the cause as the
people on the floor see it, and no solution. "New loan files take a median of nine days from receipt
to decision because intake is manual and a third of files are incomplete." It leaves out the target
(a promise before the baseline), any technology (Day 7's rule, so decomposition can do its work), and
the fine-grained causes (the batch, the spreadsheet, the API), which Day 6 maps. The sponsor and the
operator leads sign it; signing means "this is the twelve weeks", not a scope or a number. (Section
06.)

## Quick-fire

- **Three verbs to look for on a floor walk?** Wait, re-key, rework. (03.1)
- **Three gates?** A baseline, a data owner, an operator who wants it. (04.4)
- **Why is blast radius inverted and weighted lowest?** A high blast radius is handled by design
  (a human decision, signed rules), not by avoidance; it is a condition, not a veto. (04.2, 04.3)
- **"Curiosity drives initial adoption; value drives sustained usage." Whose line, and what does it
  mean at selection time?** Atlassian's; pick the problem whose solution is used because it removes
  work, not the one anyone would try once. (02.1)
- **The sensitivity check does what?** Tries other weightings and reports whether the winner
  changes; if it does, the memo says it is a judgement call. (04.3)
- **What is on the list that the sponsor did not say?** The tracker, from the floor. What is not on
  the list that he did say? The CRM, declined on Day 3. (03.2)
