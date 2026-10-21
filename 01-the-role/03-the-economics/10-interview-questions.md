# 10 · Interview Questions

> Day 3 · Section 10 of 12 · [Chapter overview](README.md) · Previous: [09 · Mistakes and debugging](09-mistakes-and-debugging.md) · Next: [11 · Exercises](11-exercises.md)

---

Twelve questions in the forms they take in FDE loops: the hiring-manager screen ("why FDE", "how is
this not consulting"), the behavioural round, and the pushes inside a client simulation when a
sponsor offers money for the wrong thing. Answer out loud first, then compare. Section numbers
point to the full explanation. [Day 43](../../08-capstone-and-career/43-the-interview-loop/README.md)
covers the whole loop; [Day 45](../../08-capstone-and-career/45-behavioural-and-client-simulation-prep/README.md)
drills "why FDE" as a story.

## The economics

**Q1. How is forward deployed engineering different from consulting?**

By what the company sells and how the engineer is measured. A consultancy sells hours or a
fixed-price build; each customer starts from zero; the engineer is measured on utilisation. An FDE
team sells a product subscription with a bounded deployment fee; the engineer is on site for weeks,
leaves when the customer is self-sufficient, and is measured on recurring revenue per engineer and
on the patterns sent back to product, which make the next deployment shorter. The published teams
say it plainly: Ramp tracks enterprise revenue divided by FDE salaries, Dataland tracks ARR per FDE
head, and OpenAI checks for a path to recurring revenue before taking an engagement and declines
pure services work. (Sections 02.1, 02.3.)

**Q2. Why would a vendor pay an engineer's salary to sit inside one customer for three months?**

Because for the problems FDEs are sent to, the subscription does not renew without one. OpenAI's
Morgan Stanley deployment took six to eight weeks to build and four more months to earn the
advisors' trust; the 98 percent adoption is what made the licence worth renewing. The FDE's weeks
are the cost of the renewal, and the renewal is recurring revenue that then needs a tenth of an
engineer to keep. The engineer's time drops while the revenue recurs; that is the whole model.
(Sections 02.2, 02.4.)

**Q3. What is "ARR per FDE", and why does the number decide whether a team survives?**

Annual recurring revenue that would still bill if the FDE resigned tomorrow, divided by the FDE
heads needed to keep it live. It decides survival because the FDE is paid from product margin: if
each engineer's engagements do not leave behind enough recurring revenue to cover several times
her cost, the team is a cost centre that sales will cut, or a services practice that will be
re-priced as one. Dataland reports multiple millions of dollars per head on a two-person team. In
the Godavari model, the renewal scenario gives 12 crore of ARR per FDE head because the steady
state needs a tenth of an engineer; saying yes to the branch CRM drops it to 1.2 crore. (Sections
02.3, 08.2.)

**Q4. What is the services trap, and how would you notice it in month one?**

The slow conversion of an FDE team into a systems integrator through reasonable yeses: a custom
screen, a side-build the product cannot absorb, paid extra weeks, an engineer who cannot leave, a
next customer who starts from zero. It happened to Palantir ("the dark ages", when field teams built
parallel systems the product could not absorb). Month-one signs: work described in hours not
outcomes, no written "not now" list, nothing sent to product, a deployment fee that grows with the
weeks, no exit date, and a custom request for which nobody can name a second customer. (Sections
03.1 to 03.4.)

**Q5. The sponsor offers to pay for a custom module your product will never include. What do you
say?**

I run the test out loud: which other customer would want this, in this shape, within a year? If
none, it is services work, and I say so: "We will not build the branch CRM. It is not our product,
no other lender would buy ours, and it would keep an engineer here for a year doing work your own
IT team or a CRM vendor does better. What we will do is expose the loan-file status so your CRM can
read it." Then I write it into the "will not build" list with the reason. The CEO sees it in the
model: a full-time FDE for 36 months drops revenue over FDE cost from 11x to 2.2x. (Sections 03.5,
08.3.)

**Q6. OpenAI's team says it turns down lucrative services work. Why would a company turn down
revenue?**

Because services revenue is, in their leader's words, a drug consultancies cannot quit: it arrives
fast, feels like growth, and builds a company that cannot stop without a revenue cliff. The team's
measure is long-term value, ARR unlocked for customers who can then self-serve, and model gains
that help every customer, not this quarter's invoice. It also keeps the team from becoming "a cast
of thousands". A 40-person vendor has less protection than OpenAI (whose product and research
organisations, not its commercial side, set strategy), so it has to let the ratio say no. (Sections
02.3, 03.3.)

## Titles and pay

**Q7. FDE, solutions engineer, consultant, applied AI engineer: who pays for each, and what is each
measured on?**

FDE: paid by the vendor from product margin, after the deal, measured on recurring revenue, the
renewal and patterns to product; owns the outcome. Solutions engineer: paid from sales budget,
before the deal, measured on revenue influenced and deals closed; the deal is the finish line.
Consultant: paid by the client by the hour or the build, measured on utilisation and delivery
against the statement of work; the firm owns the outcome contractually. Applied AI engineer: paid
from engineering, often product-side, measured on evals and feature delivery; when the posting says
the engineer sits with customers and owns a deployment, it is an FDE with more evals in it.
(Section 04.1.)

**Q8. What is FDE pay in India in 2026, and how confident should I be in the number?**

As published, not very. Glassdoor's January 2026 average base is about 12 lakh (range 9 to 16) on
28 submissions; individual total-pay submissions for one to three years' experience run 22 to 27
lakh in Hyderabad and Bengaluru; employer-stated posting ranges in July 2026 ran from a 5 to 10
lakh services tier through 22 to 55 lakh at global platforms' India centres to 70 to 90 lakh for a
founding role at Cartesia. Indeed said its sample was too small for a reliable median. The spread
tracks the employer's economics (billed to a client versus recurring revenue per FDE), not the
title. I would quote the source and the date with any of these and refresh them yearly. (Sections
05.1, 05.3.)

**Q9. A US posting says 300 to 450 thousand dollars for a mid-level FDE. What should I read into
it?**

That it is a frontier-lab or well-funded vendor posting (the June 2026 analysis of 1,000 postings
gives exactly that band), that half or more of it is equity (50 to 60 percent at mid-level, up from
35 to 45 percent in 2024), and that the cash component is probably 160 to 280 thousand. A
recruiter's average across all employers is 238 thousand, and Palantir, the highest-volume hirer,
is recorded lower. The number is real for its population and meaningless as "what FDEs make".
(Section 05.2.)

## Offers and the engagement

**Q10. What would you ask a hiring manager before accepting an FDE offer?**

How the team is measured; customers per FDE and engagement length; what the last engagement sent
back to product; an engagement they turned down; whether the deployment fee is fixed or by time;
the self-sufficiency bar and who decides the FDE leaves; what the FDE owns after go-live; whether
product, sales or services sponsors the function; the equity share, valuation and when it can be
sold; and what happened to the last FDE who left. The two most revealing are the pattern sent to
product and the engagement declined. (Section 06.2.)

**Q11. Your CEO asks whether a new customer is worth an FDE. How do you answer?**

With a small model and five qualifying questions. The model: subscription plus a bounded
deployment fee against the FDE's loaded cost over 36 months, in the scenarios that matter (no
renewal; renewal; renewal plus two more customers buying the same pattern; and the services
alternative), reporting revenue over FDE cost, ARR per FDE head and the break-even, then stressed
with the two things that go wrong (custom work that never ends; a slip with no renewal). The
questions, from OpenAI's published practice: is the problem FDE-shaped (a general product, a
specific gap only an engineer on site can close), is there a realistic path to recurring revenue,
is there a product hypothesis or a research-interesting problem, is the value large enough for
the customer to pay a subscription, and would we take it if it were pure services. Godavari passes
four, fails "research-interesting" honestly, and the answer is yes with one "will not build" line.
(Section 08.)

**Q12. How does a customer-specific fix become a product feature?**

The published path: Klarna in 2023 needed its assistant to follow more than 400 policies;
hand-written prompts did not scale; OpenAI's FDE team parameterised the instructions and tools and
wrapped each intent with an evaluation set; the pattern became an open-source library (Swarm) and
then the Agent SDK. The test an FDE applies before building: would a second, named customer want
this, in this shape, within a year. At Godavari the completeness rules for RBI-mandated documents
pass (every lender needs them); the branch CRM fails. Days 35 and 36 teach the mechanics. (Section
03.5.)

## Quick-fire round

- **Ramp's measure?** Enterprise revenue divided by FDE salaries; five to six customers per FDE.
- **Dataland's?** Multiple millions of dollars of ARR per FDE head, on two heads.
- **OpenAI's qualifying question?** FDE-shaped, with a realistic path to recurring revenue.
- **The phrase for services revenue?** A drug consultancies cannot quit.
- **Palantir's name for the trap period?** The dark ages. Nominal's answer: rotation (Day 38).
- **Six title variants?** FDE, Forward Deployed AI Engineer, Applied AI Engineer, Deployment or
  Solutions Engineer, FDSE, FDE/Solutions Architect hybrid; a third of the market under the
  adjacent ones.
- **The posting words that mean consulting?** Billed to client, utilisation, statement of work.
- **India postings growth?** Nearly 19 times, June 2025 to June 2026, Indeed, reported October 2026.
- **Equity share at a frontier lab, mid-level, 2026?** About 50 to 60 percent of total.
- **ARR is?** Revenue that would still bill if the FDE resigned tomorrow.
- **The test before building anything custom?** Name the second customer who wants it.
