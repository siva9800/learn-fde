# learn-fde: Curriculum (2026 edition, v1)

> The planning index for the Forward Deployed Engineer course. **One Day = one chapter** of deep
> notes (and, for the video series, one episode of 10 to 14 minutes plus 1 to 2 Shorts). Full
> per-Day detail lives in [`curriculum/`](curriculum/), one file per Part.

**At a glance:** **47 chapters** (Day 0 to Day 46) · **9 Parts** in **3 Stages** · one simulated
customer engagement that runs through the whole course · researched against 2026 job postings,
interview loops and the published playbooks of the teams that invented the role (sources at the end).

---

## The promise: the engineer who makes AI work inside someone else's company

A forward deployed engineer (FDE) is the engineer a vendor sends into a customer to turn a model, a
platform or an API into a system that the customer's people actually use, in the customer's own
environment, with the customer's own data, under the customer's own rules. The title was invented
at Palantir (internally "Delta"); in 2026 it is the fastest-growing engineering title in AI,
adopted by OpenAI, Anthropic, Atlassian, Databricks, Scale, the vertical-AI companies (Harvey,
Sierra, Decagon, Hebbia) and the Indian IT majors. Indeed's data shows FDE postings in India up
nearly 19 times between June 2025 and June 2026, in Bengaluru, Hyderabad, Chennai, Delhi, Mumbai
and remote.

The job has three parts, and the market weights them like this (share of 1,000 FDE postings
analysed in 2026):

| Bucket | In postings | What it means in practice |
|---|---|---|
| Core engineering | 95 percent or more | Python or TypeScript, SQL, cloud, containers, APIs, data pipelines. Production-grade, in a codebase you did not write. |
| Applied AI | 80 percent or more | LLM application development, retrieval, evals, agents and guardrails. Not training models. |
| Customer-facing discovery | 70 percent or more, rising fastest | Finding the right problem, decomposing it, scoping, winning trust, saying no, handing off. |

An FDE's time splits roughly 60 percent customer-facing, 30 percent deployment code, 10 percent
internal. Most engineers have only the first two buckets. Most courses teach only the middle one.
**This course teaches all three, by running one engagement from first meeting to handoff.**

### What makes this course different

- **One engagement, end to end.** You are an FDE at a small AI vendor. Your customer is a mid-sized
  Indian lender with a document-heavy loan-operations workflow, a legacy core system, an RBI
  auditor and a nervous security team. You meet them on Day 4 and hand off on Day 28, then prove the method transfers in the Day 42 capstone. Every chapter
  moves that engagement forward. The capstone gives you a second, different customer to prove the
  skills transfer.
- **Discovery and decomposition are taught as engineering.** The open-ended "decomposition" round
  has the lowest pass rate of any FDE interview stage, and the most common rejection reason is
  jumping to a solution before scoping. Part 2 drills the method until it is a reflex.
- **Evals first, deterministic where it matters.** The practice OpenAI's FDE team calls
  eval-driven development: build the golden set with the customer's experts before serious
  development, keep hard business rules in code the model cannot override, and treat any LLM work
  without verification as unfinished.
- **Deployment means their environment, not yours.** VPC and on-prem deployment, SSO and
  permission-aware retrieval, security review and procurement, data residency and India's DPDP
  Act, CI/CD into infrastructure you do not own.
- **The commercial judgement that keeps the role from becoming consulting.** Why the best teams
  measure enterprise revenue per FDE and recurring value, how a customer-specific fix becomes a
  product feature (Klarna's policies became OpenAI's Agent SDK), and how to refuse the
  systems-integrator trap.
- **The interview loop, drilled.** Decomposition, client simulation, practical coding, enterprise
  system design, the take-home and the eight story types the behavioural round expects.

### Who it is for, and what you need first

For engineers with two or more years of real work (backend, data, DevOps, ML or solutions roles)
who want the FDE or applied-AI engineer title, and for engineers already in solutions or
consulting roles who want to move from recommending to building. You need:

- Python at a working level, SQL, Git, and comfort with APIs. (The [DevOps Masterclass](../DevOps/README.md)
  Parts 0 to 5 or equivalent.)
- Docker and basic cloud. Kubernetes helps in Part 4 but is not required.
- Some exposure to LLM APIs. [learn-ai-ml](../learn-ai-ml/README.md) Stage 1 (Days 1 to 19) is the
  ideal on-ramp; Part 3 here goes deeper on the parts an FDE needs.

No machine learning theory is needed. An FDE deploys models; the maths is in learn-ai-ml Stage 2
for those who want it.

### How the course teaches

**Build first, judge always.** Every chapter has a hands-on project that moves the engagement, a
"Build it with AI" section showing how an FDE uses a coding agent for that work today (with the
mistakes the agent typically makes for that task), and a "How do you know it's right?" section
with a review checklist. Learning mode and building mode are the same two modes as learn-ai-ml:
AI as tutor when learning a concept, AI as pair when building, and the engineer owns the result
either way.

**Practice the conversations, not just the code.** Parts 2, 5 and 8 include scripted role-plays
(a frustrated CTO, a security team refusing credentials, a VP who wants 100 percent accuracy) with
model answers and the patterns interviewers score.

**Real companies, careful claims.** The running customer is fictional and all its data is
synthetic. Real companies (Palantir, OpenAI, Anthropic, Atlassian, Ramp, Morgan Stanley, Klarna)
appear only where a published source describes what they did, cited in the Part file.

---

## The 9 Parts

| Stage | Part | Playlist | Days | Chapters | Who can start here |
|---|---|---|---|---|---|
| - | 0 | **Start here:** The engineer in the room | 0 | 1 | Everyone |
| **1 · Understand the job** | 1 | [The Role and the Market](curriculum/part-01-the-role.md) | 1 to 3 | 3 | Everyone |
| | 2 | [Discovery and Decomposition](curriculum/part-02-discovery-and-decomposition.md) | 4 to 10 | 7 | Engineers moving from solutions or consulting |
| **2 · Build and deploy** | 3 | [Building the System Around the Model](curriculum/part-03-building-the-system.md) | 11 to 20 | 10 | Engineers who know Python and APIs |
| | 4 | [Deploying Into the Customer's World](curriculum/part-04-deploying-into-their-world.md) | 21 to 28 | 8 | DevOps and platform engineers |
| | 5 | [Working With the Customer](curriculum/part-05-working-with-the-customer.md) | 29 to 34 | 6 | |
| **3 · Own the outcome** | 6 | [From One Customer to a Product](curriculum/part-06-from-customer-to-product.md) | 35 to 38 | 4 | Engineers at AI vendors |
| | 7 | [The AI-Era FDE Toolkit](curriculum/part-07-ai-era-toolkit.md) | 39 to 41 | 3 | Anyone using coding agents on client code |
| | 8 | [Capstone, Interviews and Career](curriculum/part-08-capstone-and-career.md) | 42 to 46 | 5 | Interview preparers (Days 43 to 45) |

### The running engagement

| Role | Who | Notes |
|---|---|---|
| You | FDE at **Kaagaz AI**, a 40-person vendor selling a document-and-workflow AI platform | You own the engagement outcome, and you also owe the product team patterns that generalise. |
| Customer | **Godavari Finance Ltd**, a mid-sized NBFC (non-banking lender) headquartered in Hyderabad | 1,200 staff, 300 branches, a loan-origination process that is 60 percent paper and PDF, a 2009 core lending system with a SOAP API, an on-prem data centre plus a cautious move to AWS Mumbai, an RBI audit every year. |
| Sponsor | the Chief Operating Officer | Wants loan turnaround from 9 days to 3. |
| Operators | 40 credit-ops analysts in Hyderabad and Vijayawada | The people whose Tuesday you are changing. |
| Blockers | the CISO and the compliance head | SOC 2, data residency, DPDP Act, "no customer PII leaves India", "no model trains on our data". |
| Capstone customer | **Krishna District Hospital Network**, Vijayawada | Discharge summaries and insurance pre-authorisation: different data, different regulator, same method. |

All names, data and documents are invented and generated by code in the repo. Where a chapter
describes how a real Indian institution works (RBI's KYC rules, NPCI, DPDP), it cites the public
source.

<details>
<summary><b>All 47 chapters</b></summary>

| Day | Part | Chapter |
|---|---|---|
| 0 | 0 | The engineer in the room: what an FDE is, and the course map |
| 1 | 1 | Where the role came from: Palantir's Delta and Echo, and why AI made it everyone's model |
| 2 | 1 | The three buckets and the 60/30/10 week: what the job actually consists of |
| 3 | 1 | The economics: why FDE is not consulting, ARR per FDE, the services trap, titles and pay (India and global) |
| 4 | 2 | Picking the right problem: frequent, painful, measurable, and worth it |
| 5 | 2 | The stakeholder map: sponsor, operators, blockers, and whose version of the problem is true |
| 6 | 2 | Discovery interviews: shadowing operators, the situational map, the questions that change the architecture |
| 7 | 2 | Decomposition: the five-step method and the walking skeleton |
| 8 | 2 | Scoping the first 90 days: workstreams, sequencing by risk and value, what you will not do |
| 9 | 2 | Success metrics and the business case: from "faster" to rupees, hours and risk |
| 10 | 2 | The discovery document: writing it, defending it, and saying no |
| 11 | 3 | The system around the model: what the LLM does, what deterministic code does, and why |
| 12 | 3 | LLM APIs for production: structured outputs, tool use, streaming, retries, cost and latency budgets |
| 13 | 3 | Prompts as code: versioning, templates, rollbacks, and the prompt that works on page 1 and fails on page 40 |
| 14 | 3 | Evals first: the golden set with the customer's experts, judges, regression, and "LLM work without verification is unfinished" |
| 15 | 3 | Retrieval for enterprise documents: chunking real PDFs, hybrid search, metadata, and permission-aware retrieval |
| 16 | 3 | Integrating with what exists: SOAP, SQL, files, SFTP, the metadata translation layer, and the data you are not allowed to copy |
| 17 | 3 | Agents and workflows: tool calling, state machines, human approval on risky actions, idempotency |
| 18 | 3 | Verification and trust in the interface: showing reasoning, confidence routing, the review queue |
| 19 | 3 | Observability for AI systems: traces, token cost, quality dashboards, feedback capture |
| 20 | 3 | The walking skeleton, shipped: Godavari's first end-to-end slice in week 3 |
| 21 | 4 | Deployment models: SaaS, VPC, on-prem, air-gapped, and how to choose with a CISO in the room |
| 22 | 4 | Identity in someone else's company: SSO (Okta, Entra, AD), RBAC, service accounts, and permission-aware everything |
| 23 | 4 | The security review and procurement: SOC 2 Type 2, DPA, subprocessors, training-use policy, retention, the questionnaire |
| 24 | 4 | Data residency and Indian law: DPDP Act, RBI guidance, "nothing leaves India", and what that means for model choice |
| 25 | 4 | Network, secrets and egress: private endpoints, allowlists, KMS, and the model gateway |
| 26 | 4 | Shipping into infrastructure you do not own: CI/CD into the customer's account, IaC for a customer VPC, environments and rollback |
| 27 | 4 | Reliability in their production: SLOs for an AI system, on-call across two companies, incidents and postmortems with a customer |
| 28 | 4 | Handoff and self-sufficiency: runbooks, enablement, the 12-week bar, and knowing when you are done |
| 29 | 5 | Communication for engineers: status updates, the weekly readout, writing for a COO |
| 30 | 5 | Delivering bad news: the slip, the outage, the result that is worse than the demo |
| 31 | 5 | Demos and workshops that build trust: the Morgan Stanley lesson (8 weeks to build, 4 months to trust) |
| 32 | 5 | Scope, pushback and the governance line: when the customer asks for the thing you must refuse |
| 33 | 5 | Adoption: why curiosity starts use and value sustains it, and the operator who will not switch |
| 34 | 5 | Client simulation drills: six scripted scenarios with model responses |
| 35 | 6 | Patterns across customers: when a custom fix is a product feature, and how to tell |
| 36 | 6 | Feeding product and research: evals as the currency, the Klarna-to-Agent-SDK path |
| 37 | 6 | Measuring value honestly: hours, rupees, MTTR, adoption, and the numbers that get gamed |
| 38 | 6 | Scaling an FDE function: ratios, rotation, the dark-ages failure, and the services drug |
| 39 | 7 | Coding agents on customer code: permissions, instruction files, audit trails, what never goes in the context |
| 40 | 7 | Building with AI under constraints: air-gapped assistants, self-hosted models, and when the agent is not allowed |
| 41 | 7 | Red-teaming your own deployment: prompt injection, OWASP LLM Top 10, data exfiltration through tools |
| 42 | 8 | Capstone brief: Krishna District Hospital, discharge summaries and pre-authorisation |
| 43 | 8 | The interview loop: all eight rounds, what each scores, the ten failure reasons |
| 44 | 8 | Decomposition and system-design drills: ten timed problems with worked answers |
| 45 | 8 | Behavioural and client-simulation prep: the eight story types, "I" not "we", why FDE |
| 46 | 8 | Capstone defence, portfolio and the 30/60/90 plan |

</details>

---

## Single-owner rules

Each concept is taught in one chapter and called back everywhere else.

| Concept | Owner | Everyone else |
|---|---|---|
| The decomposition method | Day 7 | Days 8, 20, 42, 44 apply it |
| Evals and golden sets | Day 14 | Days 18, 19, 27, 36 use them |
| Permission-aware retrieval | Day 15 (retrieval) and Day 22 (identity) | Day 24 adds residency |
| Deterministic versus LLM | Day 11 | Days 17, 41 apply it |
| The security questionnaire | Day 23 | Day 21 previews, Day 32 handles the refusal |
| Status communication | Day 29 | Days 30, 31 extend |
| Value measurement | Day 9 (business case) and Day 37 (measured) | |
| Prompt injection and tool exfiltration | Day 41 | Day 17 previews with a one-line callback |

Owned **outside** this course, link only: Docker, Kubernetes, Terraform, CI/CD and observability
fundamentals (DevOps Masterclass), SLOs and incident command (learn-sre), model serving and GPUs
(learn-mlops), how LLMs and RAG work underneath (learn-ai-ml).

---

## What dates fastest

Part 3's library and API specifics (structured-output APIs, agent SDKs, judge models) have a
six-month shelf life; the method (evals first, deterministic constraints, verification in the
interface) is stable. Part 4's compliance detail (DPDP rules, RBI circulars) changes by
notification; the chapters cite the rule and the date. Part 1's market numbers are dated in the
text and should be refreshed yearly. Parts 2, 5 and 6 are about people and judgement and should
barely move.

---

## Sources

The design rests on these. Each Part file cites the ones it uses.

**Primary and company-published**
- OpenAI, forward deployed engineering, two interviews summarised in the ZenML LLMOps database: [Bringing enterprise LLM applications to production](https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production) and [FDE for enterprise LLM adoption (OpenAI, Ramp, Nominal, Dataland)](https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption)
- Atlassian, [Forward Deployed Engineering Playbook](https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook) (summary page; the PDF has the full playbook)
- Anthropic careers, Forward Deployed Engineer and Applied AI postings (mirrored at [General Catalyst](https://jobs.generalcatalyst.com/companies/anthropic/jobs/69674588-forward-deployed-engineer-applied-ai) and [Built In](https://builtin.com/job/forward-deployed-engineer/7698230))

**Market data**
- [2026 FDE hiring trends: what 1,000 job posts reveal](https://getperspective.ai/blog/2026-fde-hiring-trends-what-1000-job-posts-reveal) (skills shares, title variants, pay)
- Indeed India data as reported by [Analytics India Magazine](https://analyticsindiamag.com/ai-news/forward-deployed-engineer-job-postings-in-india-grew-nearly-19x-in-a-year-report) and [fde.directory](https://fde.directory/articles/fde-jobs-india-2026/) (India postings, employers, pay spread)
- [Paraform: OpenAI's forward deployed engineer](https://www.paraform.com/blog/openai-forward-deployed-engineer) and [FDE vs solutions engineer vs customer engineer](https://www.paraform.com/insights/forward-deployed-engineer-vs-solutions-engineer-vs-customer-engineer)

**Interview loop**
- [Harvard FAS Career Services: the FDE interview, 2026 guide](https://careerservices.fas.harvard.edu/blog/2026/08/01/forward-deployed-engineer-interview-the-definitive-2026-guide-fde/) (rounds, decomposition framework, failure reasons)
- [The Palantir decomposition interview, explained](https://fdeinterviews.com/guide/palantir-decomposition-interview)

**Playbooks and practice**
- [The FDE playbook: a practitioner's field manual](https://conikeec.substack.com/p/the-forward-deployed-engineer-playbook)
- [How FDEs run customer discovery in 2026](https://getperspective.ai/blog/how-forward-deployed-engineers-run-customer-discovery-2026) and [the FDE discovery playbook](https://getperspective.ai/blog/fde-discovery-playbook-validating-requirements-before-you-build-2026)
- [FDE first 90 days](https://cloudsoftsol.com/blog/fde-first-90-days)
- [Palantir's FDE playbook, as read by others](https://getperspective.ai/blog/palantir-forward-deployed-engineering-playbook-anthropic-openai-copying)

**Security and compliance**
- [Enterprise AI agent compliance and deployment guide: HIPAA, GDPR, residency, on-prem, VPC](https://www.sim.ai/library/enterprise-ai-agent-compliance-deployment-guide)
- [Enterprise AI vendor evaluation: a security and compliance checklist](https://tejasraundal.github.io/Teclops-AI/blog/enterprise-ai-vendor-security-compliance-checklist/)
- Official texts cited in Part 4: the Digital Personal Data Protection Act 2023 and its rules, RBI master directions on KYC and outsourcing, OWASP Top 10 for LLM Applications.

Most market and interview sources are recruiter, career-prep or vendor content. Figures are quoted
as published, dated in the text, and never rounded up to make a point.
