# Part 6 · From One Customer to a Product

> Back at Kaagaz AI after the Godavari handoff: which of the things you built are patterns, how evals and examples feed product and research, how to measure value without gaming it, and how an FDE function scales without becoming a consultancy · Days 35 to 38 · 4 episodes · ~47 min

*Why this Part exists in 2026: the difference between an FDE and a consultant is what happens
after the engagement. Reusable components come from solving one customer's specific problem well,
not from designing general solutions first; Klarna's customer-service policies became OpenAI's
Swarm, then the Agents SDK, then AgentKit. The companies that measure enterprise revenue per FDE
and recurring value scale from a handful of engineers to many; the ones that take every bespoke
build end up in what Palantir's own people called the dark ages. These are the judgement calls a
senior FDE and an FDE manager make, and a vendor's leadership will ask about them in the
interview.*

---

### Day 35 · Patterns across customers: when a custom fix is a product feature, and how to tell (~11 min)
- **Status:** new.
- **What you learn:** how to tell which of the things you built for one customer are patterns worth productising, which stay custom, and how to make that case to a product team with evidence. Reusable components emerge from solving a specific customer's problem, not from designing general solutions first.
- **Topics:**
  - The ladder: custom fix, internal library, configurable feature, product, and the cost of climbing too early
  - The pattern test: does a second customer hit the same blocker, ask the same question, need the same adapter
  - Ramp's rule: prefer features that help several customers, and check whether a blocker recurs before building for it
  - The engagement log as evidence: blockers, security questions, workarounds
  - From Godavari: the redaction gateway, group-ACL retrieval, the residency annex and the review queue generalise; the SOAP adapter stays custom
  - Premature generality: the configurable framework nobody configures
- **Real-time example:** the week after handoff you tag every component in Godavari's repository custom or candidate. A Chennai housing-finance prospect asks the same three questions in its first security call: the residency map, the no-training clause, AD group sync. The redaction gateway and the residency annex become Kaagaz AI features; the SOAP adapter stays with Godavari.
- **Analogy (Telugu audience):** biryani. A home cook makes it one way for one family. The restaurant that scaled did not design a universal recipe first; it standardised the masala after a hundred weddings.
- **Shorts:**
  - "Build it for one customer first. The product is what survives the second."
  - "Three customers, same question in the security call. That is a feature, not a fix."
- **Callbacks:** builds on D22, D24, D25, D28. Sets up D36, D38 (the pattern loop as the scaling engine), D42.

### Day 36 · Feeding product and research: evals as the currency, the Klarna-to-Agent-SDK path (~12 min)
- **Status:** new.
- **What you learn:** what an FDE owes the product and research teams after an engagement, and why eval sets are the currency. The anchor is Klarna: parameterised instructions and tools, each intent wrapped with eval sets to scale past 400 policies, which became Swarm (open-sourced October 2024), then the Agents SDK (March 2025), then AgentKit (October 2025).
- **Topics:**
  - Evals as the currency: anonymised, synthetic where needed, consented, with a failure taxonomy
  - The Klarna path: per-intent instructions, tools and eval sets
  - OpenAI's FDEs send domain examples and evals to post-training teams; two product tracks (regulatory document authoring, workflow automation) came from repeated patterns
  - The feedback contract: what goes back, in what form, how often, who owns it
  - What never goes back: customer documents or anything the DPA and DPDP Act forbid (Day 24), even inside "examples"
  - The research ask: the one capability gap no prompt fixed, written as a reproducible case
- **Real-time example:** Godavari's eval set, 1,200 labelled loan documents regenerated synthetically so no real PII remains, goes to Kaagaz AI's model team with the failure taxonomy: handwritten income proofs, stamped multi-page bank statements, Telugu-and-English sale deeds. The Chennai pilot starts from that set, not from zero.
- **Analogy (Telugu audience):** the family doctor who writes up the unusual case for the medical journal. The next doctor in the next town benefits, and the patient's name is never in it.
- **Shorts:**
  - "Klarna's 400 policies became Swarm, then the Agents SDK. The eval set made the trip."
  - "What you send back to product: evals and failures, never the customer's documents."
- **Callbacks:** builds on D14 (the golden set), D24 (what may not leave), D35. Sets up D37, D38, D40 (self-hosted models chosen from the evals).

### Day 37 · Measuring value honestly: hours, rupees, MTTR, adoption, and the numbers that get gamed (~12 min)
- **Status:** new.
- **What you learn:** how to measure what the engagement was worth in numbers that survive a sceptical CFO, and how to recognise the numbers that are easy to inflate. Atlassian's published cases are the reference: mean time to resolution from 18 days to 10 minutes, about 50 percent less triage effort, 6,700 hours a year saved.
- **Topics:**
  - The baseline measured before, from the customer's system of record, not your app
  - Hours: the shadow method and time-and-motion samples, versus self-reported "time saved"
  - Rupees: hours times loaded cost, plus risk reduced, revenue brought forward, audit findings avoided
  - MTTR and turnaround: end-to-end timestamps, and which cases count
  - The gamed numbers: documents processed, accuracy on the easy set, time saved by survey, logins as adoption (Day 33)
  - Attribution: what the model did, what the process change did, and saying so
- **Real-time example:** Godavari's quarter-end review. Turnaround is 4.2 days from 9, measured application-received to decision from the core system's timestamps. Analyst hours come from a two-day shadow sample, the error rate from the review queue. The readout says plainly that about two of the five days saved came from the COO's process change, and the CFO renews because of that line.
- **Analogy (Telugu audience):** the coaching institute that advertises "100 percent results" and counts only the students it allowed to sit the exam.
- **Shorts:**
  - "Documents processed is not value. Days to decision from their system is."
  - "Two of the five days saved were the COO's process change. Say so. That is why they renew."
- **Callbacks:** builds on D9 (the business case this Day pays), D27 (MTTR), D28, D33. Sets up D38 (recurring value per FDE), D43 (the "how did you measure impact" question), D46.

### Day 38 · Scaling an FDE function: ratios, rotation, the dark-ages failure, and the services drug (~12 min)
- **Status:** new.
- **What you learn:** what the published numbers say about how FDE teams scale (OpenAI from 2 to more than 90; Ramp at five to six customers per FDE; Dataland at millions of ARR per head; Nominal's rotation), what went wrong in Palantir's dark ages, and why services revenue is a drug consultancies cannot quit.
- **Topics:**
  - Ratios: customers per FDE and ARR per FDE as the health metrics
  - Rotation: moving FDEs between customers and back to product, so patterns spread
  - Palantir's dark ages: bespoke builds everywhere, a lagging product, and the platform as the way out
  - The services drug: why it feels good, why it compounds the wrong way, the signs a company is hooked
  - Refusing the systems-integrator role: say no, or price it as product-funded scope
  - The FDE-to-product loop as the function's real metric
- **Real-time example:** Kaagaz AI now has four FDEs and eleven customers. A bank asks for a six-month bespoke build with no overlap with the platform. The chapter works the decision: ARR, the Day 35 pattern test, the ratio. The answer is no as asked, and yes if scoped to a product-funded feature with a defined handoff.
- **Analogy (Telugu audience):** the auto driver who buys ten autos and still drives one himself has not scaled. The one who scaled trained drivers, set rules and stopped driving.
- **Shorts:**
  - "Five to six customers per FDE. If one customer takes a whole engineer forever, you sold consulting."
  - "Services revenue is a drug. Here is how a product company says no to it."
- **Callbacks:** builds on D1 (Palantir's Delta model), D3 (ARR per FDE and the services trap), D28, D35 to D37. Sets up D43, D46.

---

## Research sources

- ZenML LLMOps database, OpenAI forward deployed engineering (two interviews): the Klarna path to Swarm and the Agents SDK, examples and evals sent to post-training teams, the two product tracks, OpenAI from 2 to 90 or more FDEs, Ramp's customers per FDE and recurrence test, Nominal's rotation, Dataland's ARR per head, and "services revenue is a drug". https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production and https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption
- OpenAI Swarm (experimental framework, open-sourced October 2024; README now points to the Agents SDK): https://github.com/openai/swarm
- OpenAI Agents SDK (March 2025): https://openai.github.io/openai-agents-python/
- OpenAI, Introducing AgentKit (October 2025): https://openai.com/index/introducing-agentkit/
- Atlassian, Forward Deployed Engineering: published case results (MTTR from 18 days to 10 minutes, about 50 percent less triage effort, hours saved per year) and the twelve-week value bar. https://www.atlassian.com/enterprise/success/fde and https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook
- Palantir's FDE playbook, as read by others (Delta and Echo, the dark ages, the platform turn): https://getperspective.ai/blog/palantir-forward-deployed-engineering-playbook-anthropic-openai-copying
- The FDE playbook: a practitioner's field manual (the systems-integrator trap, ratios, scaling an FDE function): https://conikeec.substack.com/p/the-forward-deployed-engineer-playbook
- Paraform, OpenAI's forward deployed engineer (team growth and scope): https://www.paraform.com/blog/openai-forward-deployed-engineer
- 2026 FDE hiring trends: what 1,000 job posts reveal (pay and title data for Day 38's career section): https://getperspective.ai/blog/2026-fde-hiring-trends-what-1000-job-posts-reveal

## Notes for writers

- Day 9 owns the business case; Day 37 owns measured value. Day 37 must open by quoting the Day 9 promise and closing it.
- Day 3 owns ARR per FDE and the services trap as economics; Day 38 applies them to a scaling decision and must not re-teach them.
- Real-company figures (Atlassian's case results, OpenAI's team size, Ramp's ratio) are quoted exactly as published, with the source and the date in the text, and never rounded up. Atlassian's cases are vendor-published and are labelled as such.
- The Klarna account comes from OpenAI's own interviews as summarised in the ZenML database; the Swarm, Agents SDK and AgentKit dates are from OpenAI's repositories and announcements. Do not add policy counts or usage numbers beyond "past 400 policies".
- All Kaagaz AI and Godavari numbers (1,200 eval documents, 4.2 days, four FDEs, eleven customers) are synthetic.
- Day 36 must show, in code, how an eval set is regenerated synthetically before it leaves the customer, since Day 24's rules apply to examples too.
