# 11 · Interview Questions

> Day 10 · Section 11 of 13 · [Chapter overview](README.md) · Previous: [10 · Mistakes and debugging](10-mistakes-and-debugging.md) · Next: [12 · Exercises](12-exercises.md)

---

Fourteen questions in the forms they take in FDE loops: hiring-manager questions about the artifact,
and client-simulation prompts where the interviewer plays the customer. Answer out loud first, then
compare. Day 34 has the full scripted drills; Day 45 the behavioural stories.

## The artifact

**Q1. Walk me through the document you wrote at the end of discovery.**

It was a decision document, not a report. Page one gave the signed problem sentence, three findings
with numbers and methods, what we would do in operational words, the target as a range, the honest
money and the four things we would not do. Then twelve sections, each answering one reader's
question and linking the artifact behind it: people, the real workflow, the findings that changed the
architecture, the decomposition and skeleton, the dated plan, baseline and case, data and security,
risks, refusals, open questions, decisions needed. It ended with a decision log and a sign-off by the
sponsor, both blockers and the operator leads. (Sections 02, 09.)

**Q2. Who is it written for?**

Three readers at once. The COO reads page one and the decisions. The CISO reads data and security: her
conditions in her words, where files are processed at each stage, and the gate she controls. The
operator leads read the workflow, to see whether it describes their work as it is. The header says who
should read what. (Section 03.)

**Q3. Why no model names on page one?**

The sponsor cannot judge a model; he can judge a turnaround, a cost and a risk. A model name invites
the wrong argument and dates the document, since models change every few months and the problem does
not. The model is a component decision for the build phase, recorded where engineers read it. (03.2.)

**Q4. What is the difference between "will not do" and "not in these 90 days"?**

Will-not-do lines are refusals for this engagement, each with a reason, an alternative and the names of
who agreed, signed: the branch CRM, collections summaries, any change to the core data model, any PII
outside India. The parked list is real candidates deferred with a revisit point: the chatbot until it
has a baseline, income verification as the next slice. Mixing them either makes refusals look
temporary or makes candidates look dead. (05.6.)

**Q5. Your business case was negative on cost savings. Did you put that on page one?**

Yes. On analyst hours alone the system cost 1.12 crore a year more than it saved; at base, with
customers kept by faster turnaround, it was +15.0 lakh, breaking even at about 39 loans a month kept.
I put both on page one and made the retention number the pilot's question. A CFO who finds the floor on
page nine stops trusting page one. (03.2, 07.3.)

## The readout

**Q6. How do you run the meeting where it is signed?**

Pre-reads first: fifteen minutes one-to-one with each blocker on their section, the sponsor on page one,
the full draft to everyone two days ahead. In the room: the question for the day, page one, the
operator lead presenting the workflow, data and security with the CISO responding, the refusals read
aloud, then each decision put to its named decider. Changes are read back and signed in the room, and
the signed version goes out within two hours. (Section 04.)

**Q7. How do you handle an objection you did not expect?**

Acknowledge what is right in it, ask what would satisfy it, then decide whether it fits inside the
signed scope. If it does, write it as a change now and read it back with the decider's name. If it
does not, "not now, because, and instead", and it goes into decisions needed with a date. I do not agree
to scope in the room on enthusiasm. (04.4, 04.5.)

**Q8. How do you change a plan in response to objections without reopening the scope?**

Test each change against the signed lines: after it, does the problem, the workstreams or the refusal
list read differently? At Godavari four objections became four changes (a second branch counting policy
calls, stage gates for the CISO, a census before go or no-go, a per-file failure list) and none moved
a signed line. A change that would is costed in dates and taken to a checkpoint. (04.5.)

## Client simulation

**Q9. "The board saw a chatbot. Add it to the pilot." Go.**

"You are right that branches call Hyderabad about policy, and the board will ask. Not in this pilot,
because nobody has counted those calls, so we could not show the board it worked. Kukatpally is
already logging them; if Guntur does too from Monday, at the day-90 review you will have a month of
numbers from two branches, and if they cost what you think, it is the first thing we score next." The
pattern: acknowledge, a reason he can repeat, an alternative he controls, a date. (05.2.)

**Q10. "Nothing goes to the cloud until I say so." The CISO. Go.**

Treat it as a request for control, not a change of plan. "That is fair; nothing has been reviewed.
Today it runs in this building on masked files. Can I write it as three stages, each gated by your
written approval: masked files here; real files from two branches here; then our VPC in the Mumbai
region, nothing leaving India, after your review passes. Logs and backups included." (05.3.)

**Q11. "I need 100 percent accuracy." Go.**

Split the absolute. "Where it can be tested, yes: the rules you sign must miss nothing on the golden
set before they run. In production I cannot promise zero, because today is not zero: 4.1 percent of
files are decided with a document missing now. I can promise better than today, by your definition,
measured monthly, with you re-checking." Never promise what nobody can verify. (05.4.)

**Q12. The sponsor asks for something you declined before the contract. What do you say?**

The same reason as before, in the same words, and the same alternative. At Godavari the branch CRM came
back as "a small screen for follow-ups"; the answer was still that it is not our product, no other
lender would buy it, and it would keep an engineer on site for a year, with file status exposed so any
CRM can read it. A reason that changes each time it is asked is not a reason. (05.5.)

## Keeping it alive

**Q13. How do you version a discovery document?**

At every checkpoint, never rewritten. Minor versions change content inside the signed scope; major
versions change scope and go back to the signers. Changes are marked in the text and listed with
reasons. Decisions are never edited, only superseded, as in architecture decision records. One copy of
record on the customer's side. (06.4.)

**Q14. Would you let an AI write it?**

I would let an agent assemble the first draft from the artifacts and attack it as the CISO and the COO.
I would not let it decide what each reader needs or what is refused. Agents reliably invent connecting
numbers, soften conditions into adjectives, blur refusals into "phase 2", and name the vendor as the
decider. I run a checker for the mechanical failures and a review checklist for the rest. (09.6.)
