# Part 3 · Building the System Around the Model

> The engineering that makes an LLM reliable inside a real company: deterministic rules, production API use, prompts as code, evals first, enterprise retrieval, legacy integration, agents as state machines, trust in the interface and observability, ending with a shipped walking skeleton · Days 11 to 20 · 10 episodes · ~122 min

*Why this Part exists in 2026: the model is one component, and the system around it decides
whether the customer trusts the output. The teams that invented the role say the same thing in
different words: keep hard business rules in code the model cannot override, build the golden set
with the customer's experts before serious development, and treat any LLM work without
verification as unfinished. Library and API specifics here have a six-month shelf life and are
named cautiously; the method is stable. Every Day moves the Godavari engagement from a signed
discovery document to a thin end-to-end slice running by week three.*

---

### Day 11 · The system around the model: what the LLM does, what deterministic code does, and why (~12 min)
- **Status:** new
- **What you learn:** how to draw an enterprise AI system so that the model is one box among eight, and how to decide which rules live in code and which judgements go to the model. This Day owns the deterministic-versus-LLM split. It matters because the systems that fail in production are the ones where a hard constraint was left to a prompt.
- **Topics:**
  - The eight boxes: ingestion, retrieval, model, rules, verification, interface, integration, observability
  - Deterministic code enforces hard constraints 100 percent of the time; the LLM handles nuance and explanation
  - OpenAI's automotive example: "at least two suppliers for every critical part" lives in code; the model explains the options
  - Sorting the customer's rules: regulatory (code), policy (code with an override log), judgement (model with review)
  - Validation after the model: schema, ranges, cross-field consistency, reference-data lookups
  - Failure modes per box, and which the customer notices first
  - Where the humans sit in the diagram, by design
- **Real-time example:** you sort Godavari's rules. Into code: the mandatory KYC document list, PAN and Aadhaar format checks, loan amount against product limits, date logic (sanction before disbursement), the branch-visibility rule. To the model: reading a scanned, stamped, hand-annotated application form, deciding which of three bank statements is the salary account, and writing the plain-language note that explains a discrepancy to the analyst. The one-page architecture goes into the engagement folder beside the discovery document.
- **Analogy (Telugu audience):** DRS in cricket. Ball-tracking is deterministic and nobody argues with it. The umpire's soft signal handles the nuance. Trust comes from knowing which is which.
- **Shorts:**
  - "The LLM is one box. The other seven decide if anyone trusts it."
  - "Two suppliers per critical part: a rule you never leave to a prompt."
- **Callbacks:** builds on D7 (the walking skeleton), D10 (the signed scope). Sets up D12 (the model box), D17 and D41 (applying the split in agents and red-teaming), D18 (where verification sits).

### Day 12 · LLM APIs for production: structured outputs, tool use, streaming, retries, cost and latency budgets (~13 min)
- **Status:** new
- **What you learn:** how to call a model from production code so that the output is typed, failures are handled and the bill is predictable. It matters because an FDE's code runs in the customer's account on the customer's budget, and the difference between a demo and a system is everything around the request.
- **Topics:**
  - Structured outputs: a JSON schema or typed model as the contract, and what to do when the output is still invalid
  - Tool use: declaring functions, the request-response loop, parallel calls, small schemas
  - Streaming for the interface, non-streaming for the pipeline
  - Retries with backoff, timeouts, rate limits, and calls that are safe to repeat
  - A thin client layer that isolates the vendor SDK (as of October 2026 every major vendor offers structured outputs and tool calling; the shapes differ)
  - Budgets per unit of work: rupees per loan file, p95 seconds per page
  - Model tiering: a small model for classification and routing, a large one for the hard pages
  - Prompt caching and batch endpoints where offered; log request, response and cost on every call
- **Real-time example:** the extraction contract for a Godavari loan application: a typed schema with applicant, co-applicant, product, requested amount, income evidence and the documents present, each field with a confidence and a page reference. You set a budget, a fixed rupee amount per file and a p95 under two minutes for a forty-page bundle, and measure twenty files against it before anyone sees a demo.
- **Analogy (Telugu audience):** UPI. Every bank agrees the field format (structured outputs), a failed payment never debits you twice (safe retries), and the app shows "processing" while the banks talk (streaming).
- **Shorts:**
  - "Your demo called the model once. Production calls it 40,000 times a month. Budget it."
  - "Structured outputs: the model fills a form, not a page."
- **Callbacks:** builds on D11, and learn-ai-ml Stage 1 for API basics. Sets up D13 (the prompt inside the call), D16 (tools wrap the legacy system), D17 (tool loops become agents), D19 (cost per call is traced).

### Day 13 · Prompts as code: versioning, templates, rollbacks, and the prompt that works on page 1 and fails on page 40 (~11 min)
- **Status:** new
- **What you learn:** how to treat prompts like source: templated, versioned, reviewed, tied to an eval score and rolled back when a change makes things worse. It matters because the prompt is where most production changes happen after launch, and an untracked prompt edit is the commonest cause of a quiet regression.
- **Topics:**
  - Prompt files in the repository, not strings in the code; templates with typed variables
  - Versioning: every change has a diff, an author and the eval score it was measured against
  - Environment-specific prompts (dev, pilot, production) and promotion between them
  - Rollback in one step, and the alert that triggers it
  - Why the prompt that works on page one fails on page forty: context position, repeated headers, scanned noise, tables split across pages
  - Splitting work by page type instead of one prompt for the whole bundle
  - Few-shot examples from the golden set, kept out of the test split
  - A review checklist for prompt changes, including what the coding agent gets wrong
- **Real-time example:** extraction prompt v1 reads the first three pages of a Godavari application well and silently drops the co-applicant on page 38 of a sanction-letter bundle. You add a page classifier, route each page type to its own prompt, bump the version, and the Day 14 harness shows the co-applicant field going from 71 to 96 percent on the sample. The old version stays in the repository with its score beside it.
- **Analogy (Telugu audience):** the family biryani recipe card. Grandmother's version is written down with the date. Change one spice without noting it, and the next wedding's biryani is wrong and nobody knows why.
- **Shorts:**
  - "Your prompt is code. Version it or lose a weekend finding the regression."
  - "Works on page 1, fails on page 40: the long-document trap."
- **Callbacks:** builds on D12. Sets up D14 (every version gets a score), D15 (chunking and page types), D20 (the skeleton ships with versioned prompts).

### Day 14 · Evals first: the golden set with the customer's experts, judges, regression, and "LLM work without verification is unfinished" (~13 min)
- **Status:** new
- **What you learn:** how to build the evaluation set with the customer's experts before serious development, run it on every change, and reuse it as models improve. This Day owns evals and golden sets. It matters because the eval set is the only evidence the customer and your product team both accept, and OpenAI's FDE team treats LLM work without verification as incomplete.
- **Topics:**
  - The golden set: 100 to 200 real examples covering the hard cases, labelled by the people who do the work
  - Recording expert trajectories: the steps an analyst took, not only the answer
  - Labelling rules, inter-annotator agreement, adjudication with the experts
  - Metrics that match the job: per-field accuracy, completeness-check precision and recall, cost and latency per file
  - LLM-as-judge for open-ended outputs, calibrated against human labels before it is trusted
  - Regression in CI: the eval runs on every prompt, model, chunking or retrieval change
  - Reusing the set as new models arrive, to argue for or against switching
  - Masked or synthetic examples where the real ones cannot leave the customer's environment
- **Real-time example:** three senior analysts at Godavari label 150 loan files (synthetic in the repository, real in the engagement) over four afternoons: what they extracted, which documents were missing, what they would have sent back. Disagreements go to the ops lead. The harness scores extraction per field and the completeness check as precision and recall against the analysts' send-back decisions. From now on no pull request merges without this number.
- **Analogy (Telugu audience):** exam prep with previous years' papers and the official answer key. A tutor who never tests you is guessing. The golden set is the answer key the customer's own toppers wrote.
- **Shorts:**
  - "No eval, no merge. The one rule that makes AI work ship."
  - "150 files labelled by the customer's best analysts beat any benchmark."
- **Callbacks:** builds on D9 (the metrics), D13 (versions to score). Sets up D18 (thresholds from the eval), D19 (quality dashboards), D27 (the eval as a production check), D36 (evals as currency with product and research).

### Day 15 · Retrieval for enterprise documents: chunking real PDFs, hybrid search, metadata, and permission-aware retrieval (~13 min)
- **Status:** new
- **What you learn:** how to get the right passage from a pile of scanned, stamped, mixed-language PDFs, and how to make sure a user only retrieves what they are allowed to see. This Day owns permission-aware retrieval with Day 22. It matters because enterprise retrieval fails on document quality and permissions long before it fails on embeddings.
- **Topics:**
  - Real PDFs: OCR quality, rotated stamps, tables split across pages, Telugu and English on one form
  - Layout-aware chunking by page and section, with the page reference on every chunk
  - Hybrid search: keyword plus vector, fused, then re-ranked; keyword still wins on loan IDs and PAN numbers
  - Metadata on every chunk: loan ID, branch, document type, date, source system, sensitivity
  - Permission-aware retrieval: filter by the caller's groups inside the query, never only after results return
  - Keeping group membership in sync with the directory, and what happens when someone changes branch
  - Evaluating retrieval alone: recall at k on the golden set, before the model sees anything
  - Vendor-neutral storage: a database with vector support or a search engine the customer already runs
- **Real-time example:** the branch-visibility rule from Day 6 becomes code. Every chunk carries a branch ID; every query carries the analyst's Active Directory groups, synced nightly; the filter runs inside the search, so a Vijayawada analyst never sees a Hyderabad file even in a debugging log. The 2009-era scanned PAN cards push you to keyword search on the PAN pattern fused with vector search on the form text, and recall at 5 on the golden set goes above 95 percent.
- **Analogy (Telugu audience):** the wedding gift register. You find a guest by name and by village (hybrid search), and only the family may open the register (permissions). A stranger reading it afterwards is the breach.
- **Shorts:**
  - "Vector search cannot find a PAN number. Keyword search can. Use both."
  - "Permission-aware retrieval: filter inside the query, or you have already leaked."
- **Callbacks:** builds on D6 (the permissions finding), D13 (page types), D14 (recall on the golden set). Sets up D16 (where documents come from), D22 (identity and groups), D24 (residency decides where the index lives), D41 (retrieval as an injection surface).

### Day 16 · Integrating with what exists: SOAP, SQL, files, SFTP, the metadata translation layer, and the data you are not allowed to copy (~12 min)
- **Status:** new
- **What you learn:** how to connect an AI system to a core system older than the engineers running it, describe the customer's data in language a model can use, and work with data you may read but not move. It matters because every engagement has a legacy system in it, and the integration is usually where the schedule goes.
- **Topics:**
  - SOAP in 2026: reading a WSDL, generating a client, envelopes, faults, and the sandbox that does not match production
  - SQL against a read replica, with query limits and the data owner's sign-off per table
  - Files and SFTP: batch drops, naming conventions, the nightly window, partial uploads, duplicates
  - The metadata translation layer: a maintained description of tables, fields and codes in business language, so the model sees "is salaried" rather than "CUST_FLG_3"
  - Data you may not copy: query in place, minimise fields, mask at the boundary, keep the index inside the customer's environment
  - Schema drift and contract tests against the sandbox on every build
  - Idempotent writes into the core system, previewed for D17
  - The customer's engineer paired from day one, so the integration has an owner after you leave
- **Real-time example:** Godavari's core lending system exposes CreateApplication and UpdateKYCStatus over SOAP, and scanned bundles arrive by SFTP at 2 a.m. You generate a client from the WSDL, write contract tests against the sandbox, and build the metadata layer mapping forty cryptic fields to their meaning, reviewed by the system owner. Customer PII stays on the on-prem read replica; only masked fields and document hashes travel to the pipeline, the first concrete form of "nothing leaves India".
- **Analogy (Telugu audience):** the auto driver. Your new car (the model) still cannot reach the house with no street name. The auto driver who knows every lane in the old city is the integration layer, and he charges for it.
- **Shorts:**
  - "The core system is from 2009 and it is not going anywhere. Integrate."
  - "CUST_FLG_3 means salaried. The model will never guess that. Write it down."
- **Callbacks:** builds on D6 (the real workflow), D12 (tool use wraps these calls). Sets up D17 (writes behind approval), D24 (residency), D25 (network paths to the replica), D28 (the customer owns the integration at handoff).

### Day 17 · Agents and workflows: tool calling, state machines, human approval on risky actions, idempotency (~13 min)
- **Status:** new
- **What you learn:** how to build a multi-step AI workflow as an explicit state machine with persisted state, bounded loops, approval gates on anything irreversible, and writes that are safe to repeat. It matters because an agent in a customer's production touches their systems of record, and trust rests on it never doing the same thing twice or the wrong thing once.
- **Topics:**
  - Workflows versus agents: fixed sequence, model-chosen sequence, and when each is right
  - The state machine: named states, allowed transitions, persisted after every step, resumable after a crash
  - Tool-calling loops with bounded iterations, timeouts and a budget per run
  - Risk classes for actions: read, propose, write-reversible, write-irreversible
  - Human approval on risky actions: the gate, the approver, the audit record
  - Idempotency keys on every write, retries with compensation, duplicate detection
  - Agent frameworks as of October 2026: useful for the loop, never a substitute for the state machine
  - One line only: a tool that reads untrusted documents is an injection surface (owned by D41)
- **Real-time example:** the Godavari file workflow as a state machine: RECEIVED, EXTRACTED, CHECKED, NEEDS_REVIEW, APPROVED, PUSHED_TO_CORE, FAILED. Only an analyst's approval moves a file to PUSHED_TO_CORE, and the SOAP call carries an idempotency key built from the loan ID and the bundle hash, so an SFTP re-upload or a retried call never creates a second application. A run that exceeds its tool budget stops in FAILED with its trace attached.
- **Analogy (Telugu audience):** the wedding event manager with a checklist. Every item has a state, the muhurtham is the gate nobody passes without the priest, and no guest is served the same plate twice. Idempotency is the serving staff remembering who has eaten.
- **Shorts:**
  - "An agent in production is a state machine with a model inside."
  - "Idempotency key: the reason a retry never creates two loans."
- **Callbacks:** builds on D11 (which actions are deterministic), D12 (tool use), D16 (the write). Sets up D18 (the review queue is the gate's interface), D19 (traces per state), D27 (incidents in their production), D41 (prompt injection through tools).

### Day 18 · Verification and trust in the interface: showing reasoning, confidence routing, the review queue (~12 min)
- **Status:** new
- **What you learn:** how to design the screens and the routing so an operator can check the system's work in seconds, risky cases go to a human, and every correction feeds the evals. It matters because adoption is won in the interface, and the published pattern is that building takes weeks and earning trust takes months.
- **Topics:**
  - Trust through transparency: show the reasoning and the evidence before the action
  - Verification widgets: the extracted field beside the cropped source image, click-through to the page
  - Exposed tables for manual checks: operators can see and sort the underlying data
  - Confidence routing: thresholds from the eval set send each file to auto-accept, review or reject
  - The review queue: sorted by risk and age, with the reason each item is there
  - Corrections captured as labelled data, straight into the golden set
  - The Morgan Stanley pattern as published by OpenAI: pipeline ready in 6 to 8 weeks, four more months of pilots and eval refinement, 98 percent adoption
  - Designing for the sceptic who wants to see it be wrong once before trusting it
- **Real-time example:** the Godavari analyst screen. Each extracted field sits beside the crop of the page it came from; fields under the threshold are highlighted; the completeness check lists each missing document with the rule that requires it. Files with every field above threshold go straight to approval; the rest wait in a queue sorted by loan amount and age. Every correction is written back as a labelled example, and the first pilot week adds forty of them to the golden set.
- **Analogy (Telugu audience):** the family doctor who shows you the report and explains the number, versus the one who just hands over a prescription. You trust the one who shows the working.
- **Shorts:**
  - "Show the crop next to the field, and the analyst checks it in two seconds."
  - "Eight weeks to build, four months to be trusted. Plan for the four months."
- **Callbacks:** builds on D11 (where verification sits), D14 (thresholds), D17 (the approval gate). Sets up D19 (feedback becomes a dashboard), D31 (demos and workshops that build trust), D33 (adoption).

### Day 19 · Observability for AI systems: traces, token cost, quality dashboards, feedback capture (~11 min)
- **Status:** new
- **What you learn:** how to see what the system does per request, what it costs per unit of work and whether quality is drifting, using the customer's existing tooling where possible. Observability fundamentals belong to the DevOps Masterclass; this Day covers what is specific to AI systems. It matters because the customer's first production question is "why did this one cost that much" and the second is "is it getting worse".
- **Topics:**
  - A trace per request with spans for retrieval, each model call, each tool call and each state transition
  - Token and cost attribution per file, per branch, per prompt version
  - Latency by stage, and the p95 the interface promise depends on
  - Quality signals in production: eval scores on a sampled stream, review-queue rate, correction rate, confidence distribution
  - Feedback as a first-class event, linked to the trace that produced the output
  - Drift signals: new document types, new branches, a vendor model update
  - PII in logs: redaction at the logging boundary, retention agreed with compliance
  - As of October 2026, OpenTelemetry's generative-AI semantic conventions, so traces land in whatever backend the customer runs
- **Real-time example:** the cost-per-loan-file dashboard for Godavari. In pilot week two the cost per file doubles; the trace shows a new branch uploading sixty-page bank statements where the pilot branches sent four-page summaries. The fix is a page filter before extraction, and a "pages per file" line is added so the next surprise is caught the same day.
- **Analogy (Telugu audience):** cricket. The scorecard is the dashboard; the ball-by-ball commentary is the trace. When the run rate drops you go to the ball-by-ball to see which over did it.
- **Shorts:**
  - "Cost per file doubled overnight. The trace found it in one query."
  - "Every thumbs-down is a labelled example. Capture it."
- **Callbacks:** builds on D12 (cost per call), D14 (eval scores), D17 (spans per state), D18 (feedback events). Sets up D27 (SLOs and incidents), D37 (measured value); the tooling underneath is the DevOps Masterclass.

### Day 20 · The walking skeleton, shipped: Godavari's first end-to-end slice in week 3 (~12 min)
- **Status:** new
- **What you learn:** how to assemble Days 11 to 19 into one thin end-to-end slice, demonstrate it to the sponsor and the operators, and write down honestly what is stubbed and what is not done. It matters because the week-three checkpoint is where the customer decides whether to keep investing, and the skeleton is what you deploy into their environment in Part 4.
- **Topics:**
  - The slice: one loan product, one branch, PDF in, fields and completeness check out, analyst approval, a record in the core-system sandbox
  - What is real and what is stubbed, on the first slide
  - The golden set run against the skeleton, reported beside the baseline
  - Demo discipline: files chosen by the analysts, not by you; show a failure on purpose
  - The operators' first corrections, fed to the evals
  - The "not done" list: production deployment, SSO, the security review, the second loan product
  - Agreeing the pilot branches, and what the CISO needs before this runs in their account
- **Real-time example:** week three. The skeleton runs in a Kaagaz sandbox on masked files approved by the compliance head, with the core-system sandbox at the other end of the SOAP call. The demo to the COO, the ops lead and six analysts processes ten files the analysts picked: eight pass straight through, two land in the review queue for the right reason, and one extraction error is shown and corrected live. The eval score, the cost per file and the "not done" list go into the engagement folder, and the COO agrees the two pilot branches.
- **Analogy (Telugu audience):** the tasting plate at a wedding kitchen. Before a thousand plates are served, the cook sends one plate out to the family: not the full feast, every item on it, judged honestly.
- **Shorts:**
  - "Week three: one branch, one loan type, end to end. That is the demo."
  - "Show the failure on purpose. The analysts trust you more, not less."
- **Callbacks:** builds on D7 (the skeleton defined), D8 (the week-3 checkpoint), D11 to D19 (every box in the diagram). Sets up D21 (the deployment model with the CISO), D23 (the security review), D26 (shipping into their account), D29 (the readout that reports it).

---

## Sources

- OpenAI forward deployed engineering, ZenML LLMOps database summaries (eval-driven development, deterministic constraints, the automotive two-supplier rule, trust through transparency, the metadata translation layer): https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production and https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption
- OpenAI, Morgan Stanley customer story (the eval framework and the 98 percent adoption figure): https://openai.com/index/morgan-stanley/
- Atlassian, Forward Deployed Engineering Playbook: https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook
- The FDE playbook: a practitioner's field manual: https://conikeec.substack.com/p/the-forward-deployed-engineer-playbook
- FDE first 90 days (the golden set of 100 to 200 examples before model choice): https://cloudsoftsol.com/blog/fde-first-90-days
- OpenAI, Structured outputs guide: https://platform.openai.com/docs/guides/structured-outputs
- Anthropic, Tool use overview: https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview
- Anthropic, Building effective agents (workflows versus agents): https://www.anthropic.com/research/building-effective-agents
- OpenTelemetry, Semantic conventions for generative AI systems: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Stripe API reference, Idempotent requests (the idempotency-key pattern): https://docs.stripe.com/api/idempotent_requests
- pgvector, vector similarity search for Postgres (one vendor-neutral storage option): https://github.com/pgvector/pgvector
- Zeep, a Python SOAP client (WSDL-driven client generation): https://docs.python-zeep.org/
- OWASP Top 10 for LLM Applications (previewed in Day 17, owned by Day 41): https://genai.owasp.org/llm-top-10/

Tool and API names are current as of October 2026 and will date; the method does not. Godavari
Finance, its core system and its documents are invented and generated by code in the repository.
