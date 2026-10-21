# 14 · Interview Questions

> Day 7 · Section 14 of 16 · [Chapter overview](README.md) · Previous: [13 · Mistakes and debugging](13-mistakes-and-debugging.md) · Next: [15 · Exercises](15-exercises.md)

---

Sixteen questions in the forms they take in FDE loops: some are asked directly in the behavioural or
hiring-manager screen ("walk me through how you scope a problem"), most are the pushes and follow-ups
inside the decomposition round itself. Answer out loud first, then compare. Section numbers point to
the full explanation. Day 44 has ten full timed problems; these are the questions inside them.

## The method

**Q1. Walk me through how you turn a vague customer goal into something you can build.**

Five steps, and I do not name a technology until the fifth. First, clarify: the goal as a number with a
unit and a date, the trade-off being optimised and who decides the acceptable loss, the constraints
that cannot move, and my assumptions, written so I can revisit them. Second, stakeholders and the
metric each would accept: sponsor, operators, blockers, the ghost such as a regulator, the upstream
producer of the inputs, the owner of the system I write to. Third, the inputs as they actually are:
shape, owner, freshness, access, what is missing, and the data that does not exist yet. Fourth,
workstreams from those three steps, scored on value and on risk (how likely to change the plan), and
ordered risk first. Fifth, a walking skeleton: one product, one site, one path, every layer present and
each one thin, with what it proves by week three and the failures I expect. (Sections 02 to 07.)

**Q2. Why not just propose the architecture? You clearly know what it would look like.**

Because the architecture I can see in minute one is built on assumptions I have not checked: that the
documents are structured, that the system I write to tolerates retries, that the sponsor's metric is
the one that matters, that the analysts will use what I build. On a lender's loan intake, steps one to
three changed the design in at least six places: classification before extraction, an idempotency key,
reading the operators' spreadsheet before replacing it, group-filtered access, signed deterministic
completeness rules, and an expert-labelled eval set. None of those is in the minute-one architecture.
The method is not a delay; it is where the architecture comes from. (Sections 02.2, 08.7.)

**Q3. What is a walking skeleton, and why is it better than a working prototype of the hardest part?**

The thinnest end-to-end slice with every layer of the final system present: input, processing, checks,
a human decision, the write to the system of record, measurement. Each layer is deliberately small and
the stubbed parts are written down. It beats a polished component because the risks that kill
engagements are at the joints, not in the components: the write into a 2009 system, the access rules,
whether the operators will use a queue. Only an end-to-end slice tests the joints, and the skeleton
tests them in week three when a surprise costs a conversation, instead of week eleven when it costs a
rewrite. (Section 07.)

**Q4. How do you decide the order of the workstreams?**

Risk first, value second, dependencies respected loosely. Risk means how likely the work is to change
the plan, not how hard it is: an eight-week security review outside my control is a five even though
the work is filling in a questionnaire; completeness rules the compliance head can sign in a week are a
two even though they are high value. The riskiest two start in week one. Low-risk, high-value work is
not last; a thin version goes into the skeleton and the full effort comes later. Every position gets a
one-sentence reason I could say to a COO. (Section 06.)

**Q5. What does "state assumptions and revisit them" look like in practice?**

In the first five minutes I say things like "I will assume the nine days are mostly waiting rather than
analysis, and that decides the whole approach, so I will come back to it." Then after the inputs step
I do come back: "the nightly batch and the 31 percent send-backs support the waiting assumption, so the
lever is completeness and visibility, not analysis speed." If the evidence had gone the other way I
would have said so and changed the order: extraction accuracy becomes the centre and the trade-off
tightens. On the job the same assumptions sit in the worksheet and are checked at the week-one,
week-three and week-four moments. (Sections 03.5, 11.3.)

## Stakeholders and inputs

**Q6. Who are the stakeholders people usually miss?**

Three kinds. The upstream producer of the input, who is not a user but causes a share of the problem
(branch managers sending incomplete files; drivers photographing challans). The owner of the system
you write to, who can veto by being slow and has a metric of his own (zero duplicates). And the ghost:
the regulator, auditor or insurer who is in no meeting and can stop everything, whose metric (an audit
trail with a human decision) is cheap in week one and impossible to retrofit. (Section 04.4.)

**Q7. What do you ask about each data source, and why does it matter?**

Shape (what one unit looks like: a row, a 40-page scan, an XML message), owner (the person who can say
yes), freshness (real time, nightly, quarterly), access (ticket, service account, review), and what is
missing or untrustworthy. Each column changes the design: shape decides whether classification is
needed; owner is a dependency; freshness bounds what "same day" can mean; access is on the critical
path; missing data becomes a workstream with people in it. Then one more line: the data that does not
exist yet, such as ground truth, and who creates it. (Section 05.)

**Q8. The customer says all the data is in the warehouse. What do you do with that?**

Treat it as the sponsor's version and check it with the operators. In every engagement I have seen or
read about there is an unofficial channel (a spreadsheet, WhatsApp photos, a shared drive) that holds
the real state, and a join that fails (GPS to unit status, trip to purchase order). I would ask "show me
the last one you did" and watch where the data actually came from, then write the inputs table from
that. If the warehouse really does hold everything, the check costs a day. If it does not, the check
saves a month. (Sections 05.1, 05.3; Day 6.)

**Q9. What is the "LLM with RAG" anti-pattern, and when is RAG actually the right answer?**

The anti-pattern is naming retrieval plus a model as the solution before knowing the trade-off, the
people or the data: it anchors everything after it on "documents to index" and "users of the
chatbot", so the real inputs and the real metric never get written down. RAG is the right answer when
a step-2 metric is about finding or answering from documents, the inputs step shows the documents exist
in a retrievable shape with known access rules, and it appears in step five as a thin slice. On a
loan-intake problem whose metric is days to decision and whose lever is completeness, it does not move
the number first; it may serve the analysts' lookups later. (Sections 02.2, 09.6.)

## The round and the pushback

**Q10. An interviewer says "just tell me the architecture" at minute five. What do you say?**

I commit without abandoning the method: "Here is the shape I expect: one product, one site, files in,
fields and a completeness check out, a human approves, an idempotent write to the core, measured. Two
things would change it: whether the write interface tolerates retries, and whether field-level ground
truth exists. If either differs from my assumption, the first month's order changes, which is why I
asked." Then I continue with the next step. Folding gives up the method; refusing gives up the
commitment; the guides score committing while naming what would change the commitment. (Section 9.6.)

**Q11. How long should you spend asking questions in a 60-minute round?**

The guides expect ten to fifteen minutes of questions, with a thin slice proposed by about minute
thirty, and the second half for pushback and operational constraints. Each question must carry its
consequence ("if nightly, then same-hour intake is out"), or it is time spent rather than information
gained. Practising in 25 minutes with the same shape compressed makes the real round feel spacious.
(Section 9.3.)

**Q12. What does the interviewer actually score?**

Behaviours, not the answer: clarifying before solving (the strongest signal); surfacing missing data,
stakeholders and metrics; stating assumptions and revisiting them; decomposing and sequencing by risk
and value; proposing a thin first version then iterating; naming failure modes unprompted; and keeping
talking, because silence reads as stuck. Palantir-style rounds add raising adoption unprompted and
handling pushback by stating the trade-off, asking what constraint was missed, and updating. The most
common rejection is jumping to a solution before scoping. (Section 9.2.)

**Q13. Your first slice handles one branch and one product. The customer has 300 branches. Defend it.**

The slice is small so that the joints are tested in week three: the write into the core system, the
access rules, whether the analysts use a queue, whether the metrics can be logged. Those do not get
easier with more branches; they get three hundred times more expensive to fix. Once the pipe works,
widening is mostly configuration and the per-product rules the compliance head signs. The stubbed list
on the first slide says exactly what is not yet real, so nobody mistakes the skeleton for the pilot.
(Sections 07.4, 09.6.)

## On the job

**Q14. How does a bad decomposition show up later, and how would you know which step was skipped?**

Each symptom traces to a step. A demo that fails on the operators' files: the shape column or an easy
slice. Integration waiting for a stale sandbox: freshness and access, or integration not first. A
security review arriving in week eight: the blocker's metric missing, or the review not started in week
two. Operators going back to their spreadsheet: the unofficial channel not treated as the real state,
or enablement not a workstream. No baseline at day 90: the data that does not exist. A cross-branch
leak: the access rule. Duplicates: idempotency. An audit finding: the ghost's metric. (Section 11.1.)

**Q15. How do you use an AI agent to pressure-test a decomposition, and where does it fail?**

I give it the discovery notes and the filled worksheet and ask it to review, not rewrite, step by step,
citing a line of the notes for every point or saying it is a guess. It is good at structure, generic
stakeholder lists, and playing the interviewer with a timer. It fails in two ways that are exactly the
interview's two most common rejections: it invents inputs that do not exist (a labelled historical
database, a bureau API, "real-time" for a nightly batch), and it skips the stakeholders who can stop
the project (the CISO, the compliance head, the system owner, the auditor). It also scores risk as
difficulty, names technology in step one, and agrees with whatever it is shown unless given the
scoring rubric. (Section 12.7.)

**Q16. What goes into the decomposition section of the discovery document, and how is it different
from the worksheet?**

The same five steps, written for a COO: one page, numbers with their methods, no model names. The
goal as a number with the trade-off and its decider; the stakeholders with the metric each accepts;
the inputs as a table with owners and gaps; the workstreams in order with a one-line reason each and
the "not now" list; the skeleton as a paragraph with what it proves by week three and what is stubbed.
The worksheet is the working version with the assumptions and the narration notes; the document is
the signed version, updated at every checkpoint and never rewritten. (Sections 08, 11.3; Day 10.)

## Quick-fire round

- **Five step names, in order?** Clarify the goal and trade-off; stakeholders and metrics; map the
  inputs; workstreams by risk and value; walking skeleton.
- **The one rule?** No technology before step five.
- **Risk means?** How likely this work is to change the plan, not how hard it is.
- **Four workstreams an architecture-first plan always omits?** Evals, integration, security review,
  enablement.
- **The skeleton's scope sentence?** One product, one site, one path.
- **Three columns of the skeleton table?** Thin version, stubbed or manual, what it proves.
- **The strongest scored signal?** Clarifying before proposing.
- **The most common rejection?** Jumping to a solution before scoping.
- **Who usually sets the acceptable loss?** A blocker, not the sponsor.
- **What do you say under "just tell me the architecture"?** Commit in four sentences and name what
  would change it.
