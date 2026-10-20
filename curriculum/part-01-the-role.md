# Part 1 · The Role and the Market

> Where the forward deployed engineer came from, what the job consists of week to week, and the economics, titles and pay that separate it from consulting · Days 1 to 3 · 3 episodes · ~36 min

*Why this Part exists in 2026: the FDE title is the fastest-growing engineering title in AI, and
most people applying for it cannot say what it is. Palantir ran the model for fifteen years, OpenAI
grew an FDE team from 2 to over 90 people, and Indian FDE postings rose nearly 19 times in a year.
Interviewers ask "why FDE" and "how is this not consulting" in the first ten minutes. This Part
gives you the lineage, the three buckets, the economics and the pay bands, every figure dated, so
that you can answer those questions and judge an offer.*

---

### Day 1 · Where the role came from: Palantir's Delta and Echo, and why AI made it everyone's model (~12 min)
- **Status:** new
- **What you learn:** how Palantir invented the role, what a forward deployed engineer did inside a customer, and why generative AI made every vendor copy the model after 2023. It matters because the managers who built these teams read the same playbooks, and the interview's "why this role" question is really "do you know what you are signing up for".
- **Topics:**
  - Palantir's pairing: Delta (the FDE) and Echo (the customer-facing technical specialist who owned the relationship)
  - What a Delta did: live in the customer's data, build what the product lacked, send the pattern back
  - The "dark ages": field teams building separate systems the product could not absorb (Nominal's rotation answer is in D38)
  - Why generative AI revived the model: a general model, a specific problem, and a gap only an engineer on site can close
  - OpenAI's team as a published case: 2 to 90+ people, about ten major engagements at a time, split between product-hypothesis engagements and research-interesting industries, pure services work declined
  - The 2026 adopters: Anthropic, Atlassian, Databricks, Scale, vertical AI (Harvey, Sierra, Decagon, Hebbia), the Indian IT majors
  - What has not changed: the engineer owns the outcome, not the recommendation
- **Real-time example:** day one at Kaagaz AI. The CEO forwards a one-line introduction from Godavari Finance's COO: "loan turnaround is nine days, we want three, can your AI do it". Before anyone replies you write a one-page note: what a forward deployed engagement looks like here (an engineer in Hyderabad, their data, their rules, a product that improves) versus a services proposal (a quote, a team, a custom build). It is the first artifact in the engagement folder.
- **Analogy (Telugu audience):** the family doctor versus the city specialist. The specialist knows the disease; the family doctor knows the family, the kitchen and what the patient will actually do. The FDE is the family doctor the vendor sends.
- **Shorts:**
  - "Palantir called them Deltas. Now every AI company wants one."
  - "Why OpenAI put 90 engineers inside other companies instead of just selling an API."
- **Callbacks:** builds on D0 (the course map). Sets up D2 (the three buckets), D3 (economics and pay), D38 (dark ages and rotation).

### Day 2 · The three buckets and the 60/30/10 week: what the job actually consists of (~11 min)
- **Status:** new
- **What you learn:** what the job is made of, measured from postings rather than titles: core engineering, applied AI and customer-facing discovery, and how a real week splits between them. It matters because you need to know which bucket you are missing before you apply, and every interview round scores one of the three.
- **Topics:**
  - The 2026 analysis of 1,000 postings: core engineering 95 percent or more, applied AI 80 percent or more, customer-facing 70 percent or more and rising fastest
  - Core engineering: Python or TypeScript, SQL, cloud, containers, APIs, pipelines, in a codebase you did not write
  - Applied AI: LLM applications, retrieval, evals, agents, guardrails; not model training
  - Customer-facing discovery: finding the problem, scoping, winning trust, saying no, handing off
  - The 60/30/10 week (customer-facing, deployment code, internal) as a sample calendar
  - Pace from published teams: Ramp's FDEs handle 5 to 6 customers each, remotely; Atlassian reports about 12 weeks to a self-sufficient customer team
  - FDE versus solutions engineer (pre-sale, paid on deals), consultant (recommends, then leaves) and applied AI engineer (the same job with more weight on evals)
  - Self-assessment: score yourself per bucket and choose where to spend longest
- **Real-time example:** you draft the first two weeks of the Godavari engagement as a calendar: Monday to Wednesday on site in Hyderabad shadowing credit-ops analysts and meeting the CISO, Thursday on an integration spike against the 2009 core system's sandbox, Friday writing patterns up for the Kaagaz product team. Count the hours per bucket. It lands near 60/30/10 without trying, which is the point.
- **Analogy (Telugu audience):** the cricket all-rounder. A specialist batsman is picked for one thing. The all-rounder bats (code), bowls (AI) and fields at point (the customer), and the selectors test all three.
- **Shorts:**
  - "60 percent talking, 30 percent coding, 10 percent internal. Still an engineering job."
  - "FDE vs solutions engineer: one is paid on the deal, the other on the outcome."
- **Callbacks:** builds on D1. Sets up D3 (pay by title), D4 (bucket 3 begins), D11 (bucket 2 begins), D43 (how the interview rounds map to the buckets).

### Day 3 · The economics: why FDE is not consulting, ARR per FDE, the services trap, titles and pay (India and global) (~13 min)
- **Status:** new
- **What you learn:** how the teams that run FDE well measure themselves, why the role collapses into a systems-integrator business if nobody watches that number, and what the title pays in the US and India as of 2026. It matters because you will be offered engagements that are secretly services work, and you will negotiate against a very wide pay band.
- **Topics:**
  - Consulting economics (hours billed, every project from zero) versus FDE economics (recurring product revenue per engineer, every engagement improves the product)
  - Published metrics: Ramp tracks enterprise revenue divided by FDE salaries; Dataland reports multiple millions of ARR per FDE head; OpenAI declines pure services work
  - The services trap: the custom build that never generalises (full treatment in D38)
  - Six title variants in 2026 postings (FDE, Forward Deployed AI Engineer, Applied AI Engineer, Deployment or Solutions Engineer, FDSE, FDE/Solutions Architect hybrid); about a third of the market under adjacent titles
  - US total compensation in 2026 postings: mid 300 to 450k USD, senior 450 to 550k, staff at frontier labs 600k to 1.2M with equity 55 to 70 percent; Palantir's median lower, about 215k
  - India: Indeed postings up nearly 19 times from June 2025 to June 2026; Glassdoor January 2026 average base about 12 lakh (range 9 to 16 lakh, 28 submissions); postings from a 5 to 10 lakh services tier to 70 to 90 lakh for a founding role
  - Who hires in India: Infosys, Tech Mahindra, BCG X, QuantumBlack, the Databricks and Google Cloud GCCs, Peakflo, Cartesia
  - Reading a posting: the signs of a consulting job wearing the FDE title; refresh every figure yearly
- **Real-time example:** Kaagaz AI's CEO asks whether Godavari is worth an FDE. You build a two-column model with invented numbers: platform subscription plus a bounded deployment fee against a custom-build quote, compute the ARR per FDE Kaagaz needs, and write the first "we will not build this" line: Godavari's branch CRM, which would never become product.
- **Analogy (Telugu audience):** biryani. The caterer who invents a recipe for every wedding is the consultant. The restaurant that perfected one recipe and sends a chef to run a counter at the wedding is the FDE model: the chef adapts to the hall, and the recipe improves with every function.
- **Shorts:**
  - "FDE salary in India: 5 lakh to 90 lakh for the same title. Here is why."
  - "ARR per FDE: the one number that decides whether your team survives."
- **Callbacks:** builds on D1, D2. Sets up D9 (the business case), D35 and D37 (patterns and measured value), D38 (scaling the function), D46 (offers and the 30/60/90 plan).

---

## Sources

- OpenAI forward deployed engineering, two interviews summarised in the ZenML LLMOps database (team growth, engagement selection, Ramp, Nominal and Dataland figures): https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production and https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption
- Atlassian, Forward Deployed Engineering Playbook (the 12-week self-sufficiency bar): https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook
- Palantir, A day in the life of a Palantir forward deployed software engineer: https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1
- Nabeel S. Qureshi, Reflections on Palantir (the Delta and Echo roles, from a former employee): https://nabeelqu.co/reflections-on-palantir
- Palantir's FDE playbook, as read by others: https://getperspective.ai/blog/palantir-forward-deployed-engineering-playbook-anthropic-openai-copying
- 2026 FDE hiring trends: what 1,000 job posts reveal (skills shares, title variants, US pay bands): https://getperspective.ai/blog/2026-fde-hiring-trends-what-1000-job-posts-reveal
- Analytics India Magazine, FDE job postings in India grew nearly 19x in a year (Indeed data, June 2025 to June 2026): https://analyticsindiamag.com/ai-news/forward-deployed-engineer-job-postings-in-india-grew-nearly-19x-in-a-year-report
- fde.directory, FDE jobs in India 2026 (employers, pay spread, Glassdoor January 2026): https://fde.directory/articles/fde-jobs-india-2026/
- Paraform, OpenAI's forward deployed engineer: https://www.paraform.com/blog/openai-forward-deployed-engineer
- Paraform, FDE vs solutions engineer vs customer engineer: https://www.paraform.com/insights/forward-deployed-engineer-vs-solutions-engineer-vs-customer-engineer
- Anthropic careers, Forward Deployed Engineer and Applied AI postings (mirrored at General Catalyst and Built In): https://jobs.generalcatalyst.com/companies/anthropic/jobs/69674588-forward-deployed-engineer-applied-ai and https://builtin.com/job/forward-deployed-engineer/7698230

Most market and pay sources are recruiter, career-prep or vendor content. Every figure is quoted
as published, with its date in the text, and should be refreshed yearly.
