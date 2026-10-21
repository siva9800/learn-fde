# 10 · Interview Questions

> Day 1 · Section 10 of 12 · [Chapter overview](README.md) · Previous: [09 · Project](09-project-lineage-map-and-day-one-note.md) · Next: [11 · Exercises](11-exercises.md)

---

Thirteen questions in the forms they take in FDE loops: the hiring-manager screen's "why this role",
the behavioural round's "how is this not consulting", and the pushes an interviewer uses to check
whether you know the lineage or a slogan. Answer out loud first, then compare. Section numbers point
to the explanation. Day 43 covers the full loop; Day 45 turns these into stories.

## The origin

**Q1. Where did the forward deployed engineer role come from, and why?**

Palantir, from about 2005 by a vendor source, with first-hand accounts from 2015. The company built a
data platform for intelligence customers that worked in the lab and could not be installed, because
making it useful meant learning each customer's workflow, negotiating access to their data, cleaning
and joining it, and building the screens their analysts needed. Nobody at the customer could do that
and nobody could do it from Palo Alto, so the company placed its own engineers inside the customer for
months at a time with a mandate to produce an outcome. The vendor source's phrase is that it turned out
to be a co-engineering problem, not a deployment problem. (Section 01.)

**Q2. What were Delta and Echo?**

Palantir's internal names, from the NATO alphabet, for two roles on the same customer team. Delta is
the forward deployed software engineer: on site three to four days a week, integrating data, building
what the product lacked for that customer, speaking to customer executives, paid from the
business-development budget. Echo is the deployment strategist: owning which problem mattered and the
relationship, mapping workflows with the customer's analysts, running training, building demos,
presenting to the C-suite. A third name, Dev, is the product engineer who rarely visited customers
and generalised what Deltas built into the platform. Palantir's own blog uses "Delta" in a post
title; the public titles are Forward Deployed Software Engineer and Deployment Strategist. (Section
02.)

**Q3. How did field work become product at Palantir?**

Deltas hand-built the same things at customer after customer: importers, joins, visualisations, work
screens. Devs watched what repeated and automated it. The first-hand account names Magritte (import),
Contour (visualisation) and Workshop (web app UI) as tools that came from that loop and became
Foundry's core, and puts Foundry at 50 percent or more of revenue by 2024. The combination of fast,
debt-carrying field code and slow, clean product code is what the account calls one of the company's
key secrets. (Section 03.)

**Q4. What were the "dark ages", and why do you bring them up unprompted?**

A period, described by people who were there on a 2026 panel, when Palantir's field teams, waiting on
a product that absorbed their work too slowly, stopped waiting and built parallel systems per customer.
No pattern came back; every customer started from zero; engineers could not be moved. The model had
collapsed into a systems integrator. I bring it up because it is the default failure of the model, not
an aberration: an engineer on site, measured on the customer's outcome, with a platform that does not
quite do the thing, will build the thing unless structure stops them. The newer teams built against it
from the start: Nominal rotates engineers between field and core, Ramp keeps custom work inside the
core codebase, OpenAI declines pure services work. (Section 04.)

## The AI era

**Q5. Why did generative AI make a Palantir role into everyone's role?**

Because it widened the gap between "the product works" and "the customer gets an outcome" for every
vendor at once. A general model knows nothing specific about the customer; its output is
probabilistic in a business that is not; and the demo is easy, so buyers decide on it and the value
is won or lost in the distance between the demo and forty people using the system. OpenAI's telecom
voice agent failed at reading back phone numbers and took six months of evals to run at 70,000 calls a
day. Nothing in a benchmark predicts that. Only an engineer inside the customer, with the authority to
build evals and change the system, finds and fixes it. (Section 05.)

**Q6. Give me the OpenAI numbers, with dates.**

The FDE practice was two people at the start of 2024, 39 at the time of a 2024 interview with a plan
for 52 by year end, and more than 90 by a 2026 panel, running about ten major engagements at a time.
Its leader joined in November 2022, the month ChatGPT launched. First enterprise GPT-4 customer was
Morgan Stanley in 2023: six to eight weeks to build the pipeline, about four more months of pilots and
trust, 98 percent adoption among advisers reported. Klarna in 2023: hand-written prompts for 400 or
more policies became unsustainable, the parameterised approach became Swarm. The team declines
lucrative services work that does not advance strategic goals. All from company interviews summarised
by ZenML. (Sections 05.3, 06.1.)

**Q7. What did the AI-era FDE add that a Delta did not need?**

Three things, none of them research. Evals first: a golden set built with the customer's experts
before serious development, and the rule that no LLM-based code is done until verification exists.
Deterministic code around the model for the rules the model must not override. Verification in the
interface: a review queue, confidence routing, a human decision the auditor can see. A deterministic
platform either works or does not; a model's "works" has to be defined per customer and measured.
(Section 05.4.)

**Q8. Name three adopters other than OpenAI and what each changed.**

Anthropic: the Forward Deployed Engineer, Applied AI posting (closed June 2026) embeds the engineer
with strategic customers, has them deliver MCP servers, sub-agents and agent skills, and asks them to
codify repeatable deployment patterns back to Product and Engineering; the engineer also carries the
relationship, which is the Echo's half. Atlassian: the October 2026 playbook describes FDEs as senior
engineers combining AI engineering and applied AI, starting from a business outcome, and sets about
twelve weeks to a self-sufficient customer team, a time box Palantir never had. Ramp: remote, five to
six customers per FDE, inside the core codebase, measured on enterprise revenue divided by FDE
salaries. (Section 06.2.)

## The edges

**Q9. How is this not consulting?**

By where the work ends up and how it is paid for. A consultant's work ends in the customer's codebase
and is paid for once by the hour; every project starts from zero. An FDE's work ends in the vendor's
product and is paid for by every subsequent subscription; each engagement makes the next one cheaper.
The first-hand Palantir account puts the difference in margin terms: 80 percent gross margin in 2023
against 32 percent at Accenture, both companies that send people into customers. The test is the loop:
if nothing from the engagement will ever improve the product, it is consulting, whatever the title.
(Sections 03.3, 07.2.)

**Q10. How is this not a solutions engineer?**

Timing, pay and the finish line. The SE lives in the pre-sales cycle, builds the demo, is paid on
deals closed, and hands off at signature. The FDE picks up where the SE left off, builds in production
in the customer's environment, and is finished when the customer's people use the system without
them. The recruiter source dated April 2026 says it in one line: the FDE "picks up where the SE left
off". (Section 07.1.)

**Q11. Why do you want this role?**

Because I want to own whether the customer's people actually use the thing, not whether the demo
worked or the recommendation was accepted, and because I want what I learn in one company to go back
into a product so the next company needs less of me. At a lender in Hyderabad that means the forty
analysts closing their Excel tracker, and the completeness rules and review queue I build for them
becoming the platform's feature for the next lender. (Sections 06.4, 09.5.)

**Q12. What would you refuse to build for a customer?**

Anything only that customer would ever use and that the product cannot absorb: the lender's branch
CRM, a bespoke reporting tool, a fork of the platform to get around a missing feature. Not because the
customer is wrong to want it, but because the model only works if every engagement improves the
product, and the published failure is the one where field engineers built around the product. I
would take the need to the product team as a pattern request and tell the customer what we will do
instead. (Sections 04.3, 04.4.)

**Q13. The India figure: what is it and what does it not tell you?**

Indeed's data, reported by Analytics India Magazine in October 2026, shows FDE postings in India up
nearly 19 times between June 2025 and June 2026, in Bengaluru, Hyderabad, Chennai, Delhi, Mumbai and
remote. It tells you direction from a small base. It does not tell you pay (Indeed says the sample is
too small for a reliable median; Glassdoor's January 2026 average of about 12 lakh rests on 28
submissions) and it does not tell you which postings are the real role and which are services jobs
relabelled; the postings run from a 5 to 10 lakh tier to 70 to 90 lakh for founding roles. (Section
06.3; Day 3.)

## Quick-fire round

- **Delta, Echo, Dev?** FDSE on site; deployment strategist owning the problem and relationship;
  product engineer generalising field work.
- **The arrow that makes it a software business?** Outcome at one customer back into the product for
  the next.
- **The dark ages in one line?** Field teams built parallel systems; nothing came back; the model
  became services.
- **Three AI-era fixes?** Rotation (Nominal); custom work inside the core codebase (Ramp); refusing
  services work (OpenAI).
- **Why AI widened the gap?** General model, specific problem; probabilistic output; demo is easy.
- **OpenAI's growth?** 2 in January 2024 to 90+ by 2026; about ten engagements at a time.
- **Atlassian's number?** About 12 weeks to a self-sufficient team (October 2026).
- **What has not changed since 2005?** The engineer owns the outcome, not the recommendation.
- **Two-clause test?** Could you do it without their data, systems and people? Will anything go back
  to the product?
- **The India figure?** Nearly 19 times, June 2025 to June 2026, Indeed, small base.
