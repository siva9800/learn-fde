# 10 · Interview Questions

> Day 2 · Section 10 of 12 · [Chapter overview](README.md) · Previous: [09 · Mistakes and debugging](09-mistakes-and-debugging.md) · Next: [11 · Exercises](11-exercises.md)

---

Twelve questions in the forms they take in FDE loops: the recruiter screen ("what do you think the job
is?"), the hiring-manager round ("how is this not a solutions engineer?"), and the behavioural round
("which part of this role are you weakest in?"). Answer out loud first, then compare. Section numbers
point to the full explanation. Day 43 covers the whole loop; these are the questions about the job.

## The buckets

**Q1. In one minute, what does a forward deployed engineer's job consist of?**

Three buckets, measured from roughly 1,000 postings analysed in the first half of 2026. Core
engineering, in 95 percent or more: Python or TypeScript, SQL, cloud, containers, APIs and pipelines,
in a codebase and an environment you did not build. Applied AI, in 80 percent or more: LLM
applications, retrieval, evals, agents and guardrails; not training. Customer-facing discovery, in 70
percent or more and rising fastest: finding the right problem, scoping it, winning trust, saying no,
handing off. The week splits roughly 60 percent customer-facing, 30 deployment code, 10 internal. It is
an engineering job in which the customer is in the room for most of the hours. (Sections 02, 04.)

**Q2. Why is customer-facing discovery rising fastest?**

Because it is the scarce one. Engineers who can build a retrieval pipeline are easy to find and coding
agents draft most of it. Engineers who can sit with a credit-ops analyst for a morning, notice the
spreadsheet nobody mentioned, and turn "nine days to three" into a plan a CISO signs are not. The round
that tests it, decomposition, has the lowest pass rate in the loop, and the most common rejection is
jumping to a solution before scoping: a bucket-3 failure by people strong in the other two. (Sections
01.2, 03.3.)

**Q3. Where do those percentages come from, and how much do you trust them?**

A June 2026 analysis by a recruiting-platform vendor of about 1,000 English-language postings from the
first half of 2026, normalised against public postings at Palantir, OpenAI, Anthropic and Scale and
checked against third-party trackers. The method is described but not reproducible, so I quote the
figures exactly, with the date and source type, and rely on the direction rather than the digits: all
three buckets in most postings, bucket 3 rising, the week mostly with the customer. Every published
team account says the same in different words. (Section 02.)

**Q4. Is applied AI for an FDE the same as being an ML engineer?**

No. An ML engineer is judged on a benchmark; an FDE on whether forty analysts trust the output on a
Tuesday. So the bucket is weighted towards evals built with the customer's experts, deterministic code
for anything a regulator cares about, and verification in the interface. No training, rarely
fine-tuning, agents with a human approval step. The eval is the contract. (Section 03.2.)

## The week

**Q5. Sixty percent customer-facing. Is this still an engineering job?**

Yes. The customer-facing hours are engineering input: seven hours with Lakshmi found that the nine days
live in a spreadsheet and that the model's strongest document type is not the one the queue waits on,
and both changed the architecture. The deployment hours are denser because of them: Thursday's six-hour
SOAP spike found the duplicate on retry because the week before was spent with the core-system owner
and the WSDL. And the customer judges the engineering, not the meetings; OpenAI's team says its FDEs now
write much less plumbing and spend more time on actual use cases, the same trend. (Section 04.3.)

**Q6. Walk me through your first two weeks at a customer like Godavari.**

Week one is on site and almost all discovery: the COO's kickoff and "nine days doing what?"; the CISO's
three questions and the no, no, not yet; shadowing analysts in Hyderabad; a day beside Lakshmi in
Vijayawada where the Excel tracker turns up; counting which document the queue waits on; the
core-system owner and the 6 pm batch; page one of the discovery document by Friday. Week two shifts to
code: the questionnaire draft with our security lead, extraction measured on twenty real files, thirty
files labelled with Lakshmi, the sandbox spike that produces a duplicate on retry, a pattern memo to
product on Friday. Counted, week one is about 77 percent customer-facing and week two about 43; the
fortnight lands near 60/28/11 without planning for it. (Section 05.)

**Q7. How do real teams pace this?**

Ramp's FDEs handle five to six customers each, mostly remotely, and the team is measured on enterprise
revenue over FDE salaries. Atlassian's playbook says about twelve weeks to a self-sufficient customer
team. OpenAI runs about ten major engagements with a team that grew from two to over ninety, splits
them into product-shaped and research-shaped, and declines pure services work. The Ramp and OpenAI
figures are from interviews summarised in the ZenML LLMOps database; Atlassian's is vendor-published and
dated October 2026. (Section 04.4.)

**Q8. What goes wrong with the split under pressure?**

Two failures. The week that goes 90/10/0 late in an engagement: every meeting defensible, no code, no
internal hours, so no patterns, which is the moment the FDE model becomes consulting. The week that goes
10/90/0 in a hard integration: the engineer goes quiet and the customer's next question is "what have
you been doing?". The fixes are mechanical: a protected pattern block, and never a week without a
readout hour and a customer hour. (Section 07.)

## Titles and neighbours

**Q9. How is this not a solutions engineer?**

Three tests. When I arrive: an SE arrives before the deal and leaves when it closes; I arrive after and
leave when the customer's team runs the system without me. What I build: an SE builds the demo; I build
the production system in their environment. How I am paid: an SE's pay leans on deals closed; I am paid
on the outcome, and the team is measured on recurring revenue per FDE. "The SE sells the vision, the
FDE builds it, the CE maintains it." (Section 06.2.)

**Q10. And not a consultant?**

A consultant delivers a recommendation or a one-off build, bills the hours, and every project starts
from zero. An FDE builds on a product and owes the product team the patterns that make the next
customer cheaper; that 10 percent internal slice is the structural difference, and Day 3 gives the
economics. The tell in a posting is the missing internal slice: if nothing I learn goes back into a
platform, it is services under the FDE title. (Sections 06.2, 06.3.)

## You

**Q11. Which of the three buckets are you weakest in, and what are you doing about it?**

Answer from your rubric, with the number. A good answer names the bucket, two or three rows, the
evidence, and a plan with practice in it: "Customer-facing discovery, mean 0.8. I have never picked a
problem with a sponsor or written a business case. I am working through the discovery chapters with
recorded 25-minute decomposition drills, and I shadowed our own ops team for two days last month to
practise the interviews." A bad answer names a strength disguised as a weakness. (Section 08.)

**Q12. Tell me about a time you owned something in production.**

This is the question your rubric's 3s exist for: a system, a decision you made, a failure you can
explain. Ravi's version: "I own the settlement service, forty thousand lines I inherited. When I rewrote
the reconciliation queries against the bank's mirror schema I found a merchant-ID join that was
silently dropping two percent of rows; I added the check that would have caught it and we re-ran three
months of settlements." Day 45 drills the form; the rubric is where the story is found. (Section 08.3.)

## Quick-fire round

- **Three buckets and their 2026 shares?** Core engineering 95 percent or more; applied AI 80 percent or
  more; customer-facing discovery 70 percent or more, rising fastest.
- **The week?** Roughly 60 customer-facing, 30 deployment code, 10 internal.
- **The source?** About 1,000 postings, H1 2026, a recruiting vendor; quoted as published.
- **Which bucket does the decomposition round score?** Bucket 3.
- **What is not in bucket 2?** Model training.
- **Ramp's pace?** Five to six customers per FDE, mostly remote.
- **Atlassian's bar?** About twelve weeks to a self-sufficient team.
- **The audience test?** Customer's person in the room or reading: C. Code or environment for the
  deployment: D. Kaagaz reading: I.
- **The SE test?** Paid on the deal, leaves when it closes.
- **The services test?** No internal slice.
- **What does a 3 need?** A system, an action, a result, and a failure story.
