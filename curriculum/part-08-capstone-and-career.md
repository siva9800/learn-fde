# Part 8 · Capstone, Interviews and Career

> A second customer to prove the method transfers, the eight-round FDE interview loop drilled, and the first 90 days of the job · Days 42 to 46 · 5 episodes · ~63 min

*Why this Part exists in 2026: the decomposition round has the lowest pass rate of any FDE interview stage, and the most common rejection reason is solving before scoping. The engineer who has run one engagement end to end has an advantage in every round, but only if they can show it in 45 minutes, in the first person, against a sceptical interviewer. Part 8 gives you a second customer (a hospital network, a different regulator, the same method) so that the skills are provably yours, then drills the loop as it is actually run at startups, Palantir and the AI labs, and finishes with the engagement folder as a portfolio and a plan for the first 90 days.*

---

### Day 42 · Capstone brief: Krishna District Hospital, discharge summaries and pre-authorisation (~12 min)
- **Status:** new.
- **What you learn:** the capstone brief and how to run it. Krishna District Hospital Network, Vijayawada, wants discharge summaries written faster and insurance pre-authorisation answered the same day. Different data, a different regulator, a different blocker, the same method. You run discovery, decomposition, an eval set, a walking skeleton, a security questionnaire, a deployment plan and a handoff pack, and defend it live on Day 46.
- **Topics:**
  - The brief: 6 hospitals, a medical superintendent as sponsor, doctors and billing staff as operators, the IT head and the insurer TPA as blockers
  - What transfers from Godavari and what does not: a clinical note is not a salary slip
  - Discovery in a hospital: shadow a discharge, find the questions that change the architecture (Day 6)
  - Decomposition with the Day 7 method, the walking skeleton, the eval set with doctors as experts (Day 14)
  - Deterministic rules the model cannot override: dosage fields, insurer codes, consent (Day 11)
  - The questionnaire, residency and consent for health data under DPDP (Days 23, 24)
  - The deployment plan, the handoff pack and how each deliverable is scored (Days 26, 28)
- **Real-time example:** your first shadowing shift. The summary is dictated at 7 pm, typed at 9 pm by a junior doctor, and the pre-auth is rejected two days later because an insurer code was missing. Godavari's analysts had the same shape of problem with a different document. You write the first page of the discovery document that night.
- **Analogy (Telugu audience):** a batsman who learned on the Uppal pitch now plays in Visakhapatnam. Same technique; read the new pitch, respect the new bowlers, do not pretend it is Hyderabad.
- **Shorts:**
  - "Same method, new customer: the test of whether you actually learned FDE."
  - "Why a discharge summary is harder than a loan file."
- **Callbacks:** builds on Day 7 (decomposition), Day 14 (evals), Day 20 (walking skeleton), Days 23 and 24 (security, residency), Day 28 (handoff), Day 41 (the red-team page). Sets up Day 46.

### Day 43 · The interview loop: all eight rounds, what each scores, the ten failure reasons (~14 min)
- **Status:** new.
- **What you learn:** the FDE loop as it is run in 2026, round by round: what each interviewer scores, how long it takes, how the big employers differ, and the ten reasons candidates fail. You leave with a preparation plan matched to the rounds you will actually face.
- **Topics:**
  - Recruiter and hiring-manager screens: motivation, ownership, one or two projects probed deeply
  - Practical coding: messy CSV parsing, a rate limiter, streaming with backpressure, a small retrieval pipeline; narrate, test, catch your own bugs
  - Enterprise system design: a VPC-deployed HIPAA retrieval system, a Fortune 500 deployment with Okta SSO and Snowflake; scored on data flow, trust boundaries, auth, observability, failure modes and rollback
  - The decomposition case, the biggest filter (Day 44); client simulation and behavioural with STAR stories (Day 45); the 4 to 8 hour take-home at AI labs
  - Timelines: 3 to 4 weeks at startups, 4 to 6 at Palantir and the labs
  - Company notes: Palantir's open-ended round and serious culture screen; OpenAI's roughly 5-hour take-home where evaluation design differentiates; Anthropic's applied-AI loop with a mission screen
  - The ten failure reasons, each with its fix
- **Real-time example:** a candidate who ran the Godavari engagement is asked for a HIPAA-compliant retrieval system in a customer VPC. She draws the Day 25 gateway, Day 22 permission-aware retrieval and the Day 26 rollback path before being asked, then says where it fails. That is "scored on trust boundaries" in practice.
- **Analogy (Telugu audience):** EAMCET. Eight papers, each with its own marking scheme. The student who knows the scheme scores; the one who studies everything equally runs out of time.
- **Shorts:**
  - "The ten reasons FDE candidates fail, and the one that costs the most."
  - "Why your OpenAI take-home is really an evals exam."
- **Callbacks:** builds on Day 2 (the buckets map to the rounds), Day 7 (decomposition), Days 21 to 26 (design material), Day 34 (client simulation). Sets up Days 44, 45 and 46.

### Day 44 · Decomposition and system-design drills: ten timed problems with worked answers (~14 min)
- **Status:** new.
- **What you learn:** ten timed problems, five from published FDE interview guides and five set in Indian institutions, each with a worked answer in the Day 7 method: clarify, stakeholders and metrics, map the inputs, decompose, walking skeleton. You learn to spend the first ten minutes asking, to sequence by risk and value, to name failure modes unprompted and to commit under uncertainty.
- **Topics:**
  - The clock: 45 to 60 minutes, questions first, a thin slice by minute 30
  - Drill 1: faster 911 response times from call, traffic and ambulance GPS data
  - Drill 2: fraud detection across three acquired banking systems with inconsistent labels; scope the first 90 days
  - Drill 3: a pharma compound assistant under legal, IP and compliance constraints
  - Drill 4: an insurer summarising 30 million claims under state-by-state regulation
  - Drill 5: a rerouting agent across SAP data, weather APIs and 500 warehouse managers
  - Drills 6 to 10, Indian settings: a discom's complaint backlog, an NBFC's KYC re-verification across 300 branches, a district hospital's bed allocation, a UPI merchant's dispute queue, a sugar factory's cane scheduling
  - The five failure patterns: architecture before scope, ML before a baseline, technology lists, ignoring adoption, refusing to commit
- **Real-time example:** drill 2 beside Godavari. Three systems, three definitions of "fraud"; the worked answer spends the first 90 days on a shared label and a visibility tool, not a model, exactly as Day 8 sequenced Godavari's workstreams.
- **Analogy (Telugu audience):** net practice with the bowling machine at 140. Nobody is scoring; you build the reflex so that on match day the feet move before you think.
- **Shorts:**
  - "911 response times in 45 minutes: the worked answer."
  - "Three banks, three meanings of fraud: why the model comes last."
- **Callbacks:** builds on Day 7 (the method), Day 8 (sequencing), Day 9 (metrics), Day 41 (trust boundaries). Sets up Day 46 (the defence runs on the same clock).

### Day 45 · Behavioural and client-simulation prep: the eight story types, "I" not "we", why FDE (~11 min)
- **Status:** new.
- **What you learn:** how to prepare the eight stories the behavioural round expects, each 60 to 90 seconds in STAR shape, drawn from Godavari and your own work; why hiring managers screen for "I" and assume a "we" candidate was carried; and how to answer "why FDE" and "why this company" with specifics from the last few months.
- **Topics:**
  - The eight story types: end-to-end ownership, a difficult stakeholder, reversing a bad decision, alignment without authority, shipping under deadline, a failure, spotting a cross-customer pattern, saying no to a customer
  - Mining the engagement: Day 10 the no, Day 30 the bad news, Day 32 the governance line, Day 35 the pattern
  - The "I not we" rule: your contribution, without erasing the team; STAR without padding, result in numbers
  - "Why FDE": the three buckets in your own words and the moment you chose them
  - "Why this company": something shipped recently, a customer story, a published playbook; mission screens at the labs
  - Client simulation refresher with the Day 34 model answers; no overpromising
- **Real-time example:** the "saying no" story. On Day 10 Godavari's COO asked for 100 percent extraction accuracy before go-live. You tell it in the first person: what you measured, what you offered instead (confidence routing and the Day 18 review queue), what the COO said, and the number that proved you right. Ninety seconds, no "we".
- **Analogy (Telugu audience):** the village elder meeting the groom's family asks the boy himself, not his uncle, what he has built. "Our family has a business" is not an answer.
- **Shorts:**
  - "Say 'we' in an FDE interview and they assume you were carried."
  - "Eight stories, ninety seconds each: the whole behavioural round."
- **Callbacks:** builds on Day 10 (saying no), Day 30 (bad news), Day 32 (the governance line), Day 34 (client simulation), Day 35 (patterns). Sets up Day 46 (a behavioural round with a whiteboard).

### Day 46 · Capstone defence, portfolio and the 30/60/90 plan (~12 min)
- **Status:** new.
- **What you learn:** how to defend the hospital capstone live while the instructor plays a sceptical hospital CIO and changes the requirements halfway; how to turn two engagement folders into a portfolio an interviewer reads in ten minutes; and what to do in the first 30, 60 and 90 days of a first FDE job.
- **Topics:**
  - The defence: ten minutes to present, twenty of questions, one injected change of requirements
  - What the CIO probes: the eval set, the questionnaire, the rollback path, the handoff, what you would cut first
  - The engagement folder as portfolio: discovery document, decomposition, eval set, walking skeleton, questionnaire, deployment plan, handoff pack, red-team page; synthetic data, and say so
  - Presenting it: a one-page summary per engagement, the numbers, the decision you reversed
  - The 30/60/90: learn the product, customer and codebase and ship one small thing; own a workstream and run the readout; hand something off and bring the product team a pattern
  - Measuring yourself honestly (Day 37), the services trap in your own calendar (Day 38), and what in this course dates fastest
- **Real-time example:** twelve minutes in, the CIO says the insurer TPA has a new pre-auth form and the IT head now refuses any cloud. You return to the Day 21 ladder, the Day 40 self-hosted option and the eval set, and give a revised plan with what slips. The recovery, not the deck, is what is scored.
- **Analogy (Telugu audience):** the viva voce with an external examiner. The report got you into the room; the examiner wants to see whether you still understand it when the question changes.
- **Shorts:**
  - "The hospital CIO changed the requirements mid-defence. Here is the move."
  - "Your first 90 days as an FDE: ship one small thing by day 30."
- **Callbacks:** builds on Day 21 (deployment ladder), Day 28 (handoff), Day 37 (measuring value), Day 38 (the services drug), Day 40 (constrained builds), Day 42 (the brief), Days 43 to 45 (the loop). Closes the course; the engagement folder is the artefact the student keeps.

---

## Sources

- Harvard FAS Career Services, "The forward deployed engineer interview: the definitive 2026 guide" (rounds, coding and design examples, timelines, company notes, the ten failure reasons, the eight story types, the five drill cases): https://careerservices.fas.harvard.edu/blog/2026/08/01/forward-deployed-engineer-interview-the-definitive-2026-guide-fde/
- The Palantir decomposition interview, explained (how the round runs, what is scored, failure patterns): https://fdeinterviews.com/guide/palantir-decomposition-interview
- Anthropic careers, Forward Deployed Engineer and Applied AI postings (mirrored at General Catalyst and Built In): https://jobs.generalcatalyst.com/companies/anthropic/jobs/69674588-forward-deployed-engineer-applied-ai and https://builtin.com/job/forward-deployed-engineer/7698230
- Paraform, OpenAI's forward deployed engineer: https://www.paraform.com/blog/openai-forward-deployed-engineer
- OpenAI forward deployed engineering, summarised in the ZenML LLMOps database (eval-driven development, the practice the take-home tests): https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production
- FDE first 90 days: https://cloudsoftsol.com/blog/fde-first-90-days
- The FDE playbook: a practitioner's field manual: https://conikeec.substack.com/p/the-forward-deployed-engineer-playbook
- Enterprise AI agent compliance and deployment guide (HIPAA, residency, on-prem, VPC; context for the hospital capstone and the design round): https://www.sim.ai/library/enterprise-ai-agent-compliance-deployment-guide

## Notes for writers

- Krishna District Hospital Network, its staff and its data are invented; generate every document with code in the repo. Where the chapter describes how Indian health insurance pre-authorisation or DPDP consent for health data actually works, cite the public source.
- Day 43's company notes are candidate-reported and recruiter content as published in August 2026. Quote them with the date and refresh yearly. Take-home lengths vary by team; say "roughly" and "reported".
- Drills 1 to 5 on Day 44 are the published cases from the Harvard guide; drills 6 to 10 are ours. Worked answers must follow the Day 7 method exactly, so a reader can see the same five steps ten times.
- Day 45 reuses the Day 34 scenarios; do not write new client-simulation scripts here.
- The 30/60/90 is advice, not a company's policy. Do not attribute it to a named employer.
