# Skills self-assessment · Ravi Teja

> Day 2 sample. A filled rubric for an invented student, used to show the script's output in section 08.
> Copy `skills-rubric-template.md` for your own; do not edit this one.

**Name:** Ravi Teja · **Current role:** backend engineer at a Hyderabad payments startup · **Years of real work:** 4 · **Date:** 2026-10-21

Scores: **0** never done it · **1** read about it or did a tutorial · **2** did it once or under someone else's
ownership · **3** owned it in production, more than once, and could explain the failures.

## Bucket 1 · Core engineering

| # | Skill | Score (0 to 3) | Evidence (one line, a thing you did) |
|---|---|---|---|
| E1 | Python or TypeScript at production level: types, tests, packaging, a codebase you did not write | 3 | Own the settlement service (FastAPI, 40k lines I inherited); typed, 80 percent test coverage, on call for it since 2024 |
| E2 | SQL against a schema you did not design, including the joins that fail | 3 | Rewrote the reconciliation queries against the bank's mirror schema; found the merchant-ID join that dropped 2 percent of rows |
| E3 | A cloud account you do not own: IAM, VPC, deploying into someone else's environment | 1 | Only our own AWS account; have read about cross-account roles |
| E4 | Containers and CI/CD into a pipeline that belongs to the customer | 2 | Added a Docker build and a GitHub Actions deploy to our platform team's pipeline, with their review |
| E5 | Integration with what exists: SOAP, REST, SFTP, files, batch jobs, a system from 2009 | 2 | Built the SFTP pull and parser for a bank's nightly settlement file (fixed-width, 2 am) |
| E6 | Data pipelines that survive bad input: scanned PDFs, mixed languages, missing pages | 1 | Parsed CSVs with bad rows; never touched scanned documents |

## Bucket 2 · Applied AI

| # | Skill | Score (0 to 3) | Evidence (one line, a thing you did) |
|---|---|---|---|
| A1 | LLM APIs in production: structured outputs, tool use, retries, a cost and latency budget | 2 | Hackathon: a support-ticket classifier with structured output and retries; never had a cost budget |
| A2 | Prompts as code: versioned, templated, regression-tested, rolled back | 1 | Prompts lived in a notebook |
| A3 | Evals: a golden set built with domain experts, a judge, a regression run before every change | 0 | |
| A4 | Retrieval over enterprise documents: chunking real PDFs, hybrid search, permission-aware results | 1 | Followed a RAG tutorial on my own notes |
| A5 | Agents and workflows: tool calling, state machines, human approval on risky actions, guardrails | 0 | |
| A6 | Observability for an AI system: traces, token cost, a quality dashboard, feedback capture | 2 | Own the Grafana dashboards for the settlement service; logged token counts per call in the hackathon, once |

## Bucket 3 · Customer-facing discovery

| # | Skill | Score (0 to 3) | Evidence (one line, a thing you did) |
|---|---|---|---|
| C1 | Picking the right problem: frequent, painful, measurable, worth it; refusing the demo-shaped one | 0 | |
| C2 | The stakeholder map: sponsor, operators, blockers, and whose version of the problem is true | 1 | Read the Day 0 story; never drawn one |
| C3 | Discovery interviews and shadowing the people who do the work | 1 | Sat with ops for an afternoon once, informally |
| C4 | Decomposing and scoping: workstreams by risk, a thin first slice, what you will not do | 1 | Sat in while my lead scoped the settlement rewrite into three phases; the order and the "not now" list were his |
| C5 | The business case: from "faster" to hours, rupees and risk a COO signs | 0 | |
| C6 | Writing and speaking for executives: the readout, bad news, pushback, saying no | 1 | Wrote incident summaries for the CTO |
| C7 | The security and procurement conversation: the questionnaire, residency, "does it train on our data" | 0 | |
| C8 | Handoff: runbooks, enablement, leaving a team that runs it without you | 2 | Wrote the runbook for the settlement service and trained two juniors before my leave |

## Where I will spend longest (fill after running the script)

- Weakest bucket: customer-facing discovery
- The three rows I will fix first, and the chapter for each: C1 (Day 4), C5 (Day 9), C7 (Day 23); then C4 (Day 7), A3 (Day 14) and A5 (Day 17)
- The strength I will lead with in interviews, and the story behind it: E2, the merchant-ID join that dropped 2 percent of rows; it is already a Day 7 step-3 story
