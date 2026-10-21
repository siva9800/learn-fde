# Gap plan from sample-rubric-ravi.md

```text
== sample-rubric-ravi.md: 20 rows read ==

bucket                    mean  rows at 0/1  rows at 3
core engineering           2.0       2           2    
applied AI                 1.0       4           0    
customer-facing discovery  0.8       7           0    

weakest bucket: customer-facing discovery; spend longest there (Part 2 and Part 5)

the gap plan, in the order to work it (weakest bucket first, lowest score first):
customer-facing discovery (mean 0.8): 7 gap(s)
  C1 score 0  Picking the right problem: frequent, painful, measurable, worth it; refusing the demo-shaped one
      learn it in: Day 4 (picking the right problem)
  C5 score 0  The business case: from "faster" to hours, rupees and risk a COO signs
      learn it in: Day 9 (success metrics and the business case)
  C7 score 0  The security and procurement conversation: the questionnaire, residency, "does it train on our data"
      learn it in: Day 23 (the security review) and Day 24 (data residency)
  C2 score 1  The stakeholder map: sponsor, operators, blockers, and whose version of the problem is true
      learn it in: Day 5 (the stakeholder map)
  C3 score 1  Discovery interviews and shadowing the people who do the work
      learn it in: Day 6 (discovery interviews)
  C4 score 1  Decomposing and scoping: workstreams by risk, a thin first slice, what you will not do
      learn it in: Day 7 (decomposition) and Day 8 (scoping the first 90 days)
  C6 score 1  Writing and speaking for executives: the readout, bad news, pushback, saying no
      learn it in: Day 10, Day 29, Day 30 and Day 32 (the document, the readout, bad news, pushback)
applied AI (mean 1.0): 4 gap(s)
  A3 score 0  Evals: a golden set built with domain experts, a judge, a regression run before every change
      learn it in: Day 14 (evals first)
  A5 score 0  Agents and workflows: tool calling, state machines, human approval on risky actions, guardrails
      learn it in: Day 17 (agents and workflows)
  A2 score 1  Prompts as code: versioned, templated, regression-tested, rolled back
      learn it in: Day 13 (prompts as code)
  A4 score 1  Retrieval over enterprise documents: chunking real PDFs, hybrid search, permission-aware results
      learn it in: Day 15 (retrieval for enterprise documents)
core engineering (mean 2.0): 2 gap(s)
  E3 score 1  A cloud account you do not own: IAM, VPC, deploying into someone else's environment
      learn it in: Day 26 (shipping into infrastructure you do not own)
  E6 score 1  Data pipelines that survive bad input: scanned PDFs, mixed languages, missing pages
      learn it in: Day 15 (chunking real PDFs) and Day 16

strengths to lead with in interviews (a 3 with evidence is a story; Day 45 turns it into one):
  E1  Own the settlement service (FastAPI, 40k lines I inherited); typed, 80 percent test coverage, on call for it since 2024
  E2  Rewrote the reconciliation queries against the bank's mirror schema; found the merchant-ID join that dropped 2 percent of rows
```
