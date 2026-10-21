# Gap plan from ai-draft-rubric-priya.md

```text
== ai-draft-rubric-priya.md: 20 rows read ==
warnings (read these first):
  - E1: scored 3 with thin evidence ('Strong Python skills'); counted as 1 until you can name the system and the result
  - E2: scored 3 with thin evidence ('Advanced SQL'); counted as 1 until you can name the system and the result
  - E3: scored 3 with thin evidence ('AWS certified'); counted as 1 until you can name the system and the result
  - E4: scored 3 with thin evidence ('Docker and Kubernetes experience'); counted as 1 until you can name the system and the result
  - E5: scored 3 with thin evidence ('REST APIs'); counted as 1 until you can name the system and the result
  - E6: scored 3 with thin evidence ('Built Spark pipelines'); counted as 1 until you can name the system and the result
  - A2: scored 2 with thin evidence ('Prompt engineering'); counted as 1 until you can name the system and the result
  - A3: scored 2 with thin evidence ('Evaluated model accuracy'); counted as 1 until you can name the system and the result
  - A5: scored 2 with thin evidence ('LangChain agents'); counted as 1 until you can name the system and the result
  - A6: scored 2 with thin evidence ('Monitoring dashboards'); counted as 1 until you can name the system and the result
  - C1: scored 2 with thin evidence ('Good problem-solving skills'); counted as 1 until you can name the system and the result
  - C2: scored 2 with thin evidence ('Worked with stakeholders'); counted as 1 until you can name the system and the result
  - C3: scored 2 with thin evidence ('Requirements gathering'); counted as 1 until you can name the system and the result
  - C4: scored 3 with thin evidence ('Agile sprint planning'); counted as 1 until you can name the system and the result
  - C5: scored 2 with thin evidence ('Presented ROI to management'); counted as 1 until you can name the system and the result
  - C6: scored 2 with thin evidence ('Excellent communication skills'); counted as 1 until you can name the system and the result
  - C7: scored 2 with thin evidence ('Aware of GDPR'); counted as 1 until you can name the system and the result
  - C8: scored 2 with thin evidence ('Documentation'); counted as 1 until you can name the system and the result

bucket                    mean  rows at 0/1  rows at 3
core engineering           1.0       6           0    
applied AI                 1.7       4           2    
customer-facing discovery  1.0       8           0    

weakest bucket: core engineering; spend longest there (Part 3 Days 15 to 16 and Part 4)

the gap plan, in the order to work it (weakest bucket first, lowest score first):
core engineering (mean 1.0): 6 gap(s)
  E1 score 1  Python or TypeScript at production level: types, tests, packaging, a codebase you did not write
      learn it in: Days 12 and 20 (production code in the engagement) and the DevOps Masterclass
  E2 score 1  SQL against a schema you did not design, including the joins that fail
      learn it in: Day 16 (integrating with what exists)
  E3 score 1  A cloud account you do not own: IAM, VPC, deploying into someone else's environment
      learn it in: Day 26 (shipping into infrastructure you do not own)
  E4 score 1  Containers and CI/CD into a pipeline that belongs to the customer
      learn it in: Day 26 (CI/CD into the customer's account)
  E5 score 1  Integration with what exists: SOAP, REST, SFTP, files, batch jobs, a system from 2009
      learn it in: Day 16 (SOAP, SQL, files, SFTP, the translation layer)
  E6 score 1  Data pipelines that survive bad input: scanned PDFs, mixed languages, missing pages
      learn it in: Day 15 (chunking real PDFs) and Day 16
customer-facing discovery (mean 1.0): 8 gap(s)
  C1 score 1  Picking the right problem: frequent, painful, measurable, worth it; refusing the demo-shaped one
      learn it in: Day 4 (picking the right problem)
  C2 score 1  The stakeholder map: sponsor, operators, blockers, and whose version of the problem is true
      learn it in: Day 5 (the stakeholder map)
  C3 score 1  Discovery interviews and shadowing the people who do the work
      learn it in: Day 6 (discovery interviews)
  C4 score 1  Decomposing and scoping: workstreams by risk, a thin first slice, what you will not do
      learn it in: Day 7 (decomposition) and Day 8 (scoping the first 90 days)
  C5 score 1  The business case: from "faster" to hours, rupees and risk a COO signs
      learn it in: Day 9 (success metrics and the business case)
  C6 score 1  Writing and speaking for executives: the readout, bad news, pushback, saying no
      learn it in: Day 10, Day 29, Day 30 and Day 32 (the document, the readout, bad news, pushback)
  C7 score 1  The security and procurement conversation: the questionnaire, residency, "does it train on our data"
      learn it in: Day 23 (the security review) and Day 24 (data residency)
  C8 score 1  Handoff: runbooks, enablement, leaving a team that runs it without you
      learn it in: Day 28 (handoff and self-sufficiency)
applied AI (mean 1.7): 4 gap(s)
  A2 score 1  Prompts as code: versioned, templated, regression-tested, rolled back
      learn it in: Day 13 (prompts as code)
  A3 score 1  Evals: a golden set built with domain experts, a judge, a regression run before every change
      learn it in: Day 14 (evals first)
  A5 score 1  Agents and workflows: tool calling, state machines, human approval on risky actions, guardrails
      learn it in: Day 17 (agents and workflows)
  A6 score 1  Observability for an AI system: traces, token cost, a quality dashboard, feedback capture
      learn it in: Day 19 (observability for AI systems)

strengths to lead with in interviews (a 3 with evidence is a story; Day 45 turns it into one):
  A1  Familiar with OpenAI and Anthropic APIs
  A4  Built a RAG chatbot over company docs
```
