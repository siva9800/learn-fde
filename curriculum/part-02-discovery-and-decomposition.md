# Part 2 · Discovery and Decomposition

> Finding the problem worth solving inside someone else's company, mapping who owns it, interviewing the people who do it by hand, and breaking it into a 90-day plan you can defend · Days 4 to 10 · 7 episodes · ~82 min

*Why this Part exists in 2026: the open-ended decomposition round has the lowest pass rate of any
FDE interview stage, and the most common rejection reason is jumping to a solution before scoping.
On the job the failure looks the same: a prototype built for the sponsor's version of the problem
that the operators never use. The teams that invented the role say it plainly: pick problems that
are frequent, painful and measurable, interview the people who do the work before writing
production code, and agree how success is measured before choosing a model. This Part teaches that
as a method, drilled on one customer until it is a reflex.*

---

### Day 4 · Picking the right problem: frequent, painful, measurable, and worth it (~11 min)
- **Status:** new
- **What you learn:** how to choose the one problem an engagement should attack when the customer arrives with seven, and why "what can the model do" is the wrong first question. It matters because the first week decides whether the next twelve produce a product feature or a demo nobody runs on a Tuesday.
- **Topics:**
  - Atlassian's filter: frequent, painful, measurable, then work backwards to the AI
  - OpenAI's filter: problems worth tens of millions to the customer, and interesting to product or research
  - Start from the workflow, not the model: where do people wait, re-key or rework
  - A scoring sheet: frequency, pain, measurability, data availability, risk, strategic fit
  - The demo trap (impressive, happens twice a month) and the chatbot trap (a solution wearing a problem's clothes)
  - Problems to decline on Day 4: no data owner, no baseline, no operator who wants it
  - The one-sentence problem statement the sponsor and the operators both sign
- **Real-time example:** the first meeting with Godavari's COO produces seven candidates: KYC document checks, income verification from bank statements, title-deed review, a branch chatbot, collections call summaries, credit-memo drafting and loan-file completeness. You score them. Loan-file intake wins: 60 percent of files arrive as paper or PDF, analysts re-key them into the 2009 core system, and 31 percent go back to the branch for a missing document. Frequent, painful, and already measured.
- **Analogy (Telugu audience):** exam prep. You do not revise the chapter you enjoy; you revise the chapter with the most marks that you keep failing.
- **Shorts:**
  - "The customer brought seven problems. Here is how you pick one."
  - "A chatbot over your documents is not a problem. It is a solution looking for one."
- **Callbacks:** builds on D2 (bucket 3), D3 (what will never become product). Sets up D5 (who owns the problem), D9 (the baseline becomes the business case), D42 (the capstone repeats this step).

### Day 5 · The stakeholder map: sponsor, operators, blockers, and whose version of the problem is true (~11 min)
- **Status:** new
- **What you learn:** how to map everyone who can fund, use, veto or quietly ignore the system, and why the sponsor's version of the problem and the operators' version almost never match. It matters because engagements are lost to people who were not in the first meeting.
- **Topics:**
  - Four roles: sponsor (pays, wants a number), operators (whose day changes), blockers (security, compliance, legal, IT), ghost stakeholders (the regulator, the auditor)
  - Power and interest: who signs, who can veto, who will actually open the tool
  - The sponsor's version versus the operators' version, and why both are true from where each sits
  - The system owner: the engineer who runs the legacy core and has watched three vendors fail
  - The champion: one operator who wants this and becomes your first user
  - Blockers as early partners: the CISO in week one, not week ten
  - The customer's calendar: audit month, quarter end, release freeze
- **Real-time example:** the COO says "the analysts are slow". The analysts in Vijayawada say "we wait three days for the branch to resend a missing document, then the core system batch runs overnight". Both are true. Your map puts the COO as sponsor, the forty analysts as operators, the CISO and compliance head as blockers, the core-system owner as the person whose goodwill decides the integration, and the RBI auditor as the ghost in every room. The compliance head's first sentence, "no customer PII leaves India", goes into the constraints list.
- **Analogy (Telugu audience):** a wedding. The father pays and wants it on time (sponsor). The couple lives with every decision (operators). The priest will not move the muhurtham (blocker). The village elder nobody invited to the planning can still stop the function (ghost stakeholder).
- **Shorts:**
  - "The COO said slow. The analysts said waiting. Both were right."
  - "Meet the CISO in week one. In week ten she will say no."
- **Callbacks:** builds on D4. Sets up D6 (interviewing each group), D10 (who is in the readout), D21 and D23 (the CISO's constraints), D33 (the operator who will not switch).

### Day 6 · Discovery interviews: shadowing operators, the situational map, the questions that change the architecture (~12 min)
- **Status:** new
- **What you learn:** how to spend the first days on site: getting real access, watching people do the work by hand, interviewing 8 to 10 end users before writing production code, and mapping the workflow as it really runs rather than as it is documented. It matters because one answer in one interview can change the retrieval architecture, and finding it in week eight costs a rewrite.
- **Topics:**
  - Days 1 to 2 are access and reality: SSO, repositories, the warehouse as it actually is
  - Shadowing: sit beside an operator for a full cycle and record every click, wait and workaround
  - The interview plan: 8 to 10 end users across roles and locations, before any production code
  - The question bank: "show me the last one you did", "what do you do when it is wrong", "what is in the Excel sheet"
  - The situational map: inputs, tools, handoffs, waits, exceptions, unofficial channels
  - The questions that change the architecture: who may see what, how access is granted, how fresh the data must be, what must never be automated
  - The week-one deliverable: the real workflow map, reviewed with the operators who gave it to you
- **Real-time example:** two days with analysts in Vijayawada. The SOP has twelve steps; reality has nineteen, including WhatsApp photos of documents from branch staff and an Excel tracker that is the true source of file status. One answer changes the design: branch managers must not see other branches' files, and that access comes from Active Directory groups synced from HR. Retrieval will have to filter by the caller's groups at query time, now a requirement for Days 15 and 22 rather than a surprise in month three.
- **Analogy (Telugu audience):** Google Maps versus the auto driver. The sponsor hands you the map. The auto driver knows the lane that floods, the one-way nobody follows and the gate locked after eight. Interview the auto drivers.
- **Shorts:**
  - "The SOP said 12 steps. I counted 19. Step 14 was WhatsApp."
  - "One interview answer, one month of rework saved: ask who is allowed to see what."
- **Callbacks:** builds on D4, D5. Sets up D7 (the map feeds decomposition), D15 and D22 (permission-aware retrieval and identity), D16 (the tracker and the core system are the integration surface), D34 (the frustrated-operator role-play).

### Day 7 · Decomposition: the five-step method and the walking skeleton (~13 min)
- **Status:** new
- **What you learn:** the method for turning a vague goal into workstreams you can build and a thin end-to-end slice you can ship in weeks, without naming a solution before step five. This Day owns the method for the course. It matters because the decomposition interview scores exactly this, and the most common rejection is jumping to a solution before scoping.
- **Topics:**
  - Step 1: clarify the goal and the trade-off being optimised (speed against error rate, cost against coverage)
  - Step 2: identify the stakeholders and the success metric each would accept
  - Step 3: map the inputs: data shape, owner, freshness, access, what is missing
  - Step 4: decompose into workstreams, sequenced by risk and value
  - Step 5: propose a walking-skeleton MVP, every layer present and each one thin
  - Why a skeleton beats a polished component: integration risk surfaces first
  - The anti-pattern: "an LLM with RAG" in the first minute
  - Running the method out loud in 25 minutes, the way the interview does
- **Real-time example:** apply the five steps to "nine days to three". The trade-off is speed against the error rate the RBI auditor will accept. Metrics: turnaround, analyst hours per file, send-back rate, field-level accuracy. Inputs: scanned PDFs on SFTP, the SOAP API, the Excel tracker, the AD groups. Workstreams: extraction, completeness checks, evals, integration, security review, enablement. The skeleton: one loan product, one branch, PDF in, fields and a completeness check out, an analyst approves, a record lands in the core system.
- **Analogy (Telugu audience):** chasing 300 in a one-day match. Nobody says "hit sixes". The captain sets a required rate per ten overs, wickets to keep in hand, which bowler to attack, and a plan for the first ten overs that proves the chase is on. Those ten overs are the walking skeleton.
- **Shorts:**
  - "Five steps before you say the word LLM."
  - "Walking skeleton: every layer, each one thin, shipped in week three."
- **Callbacks:** builds on D4, D5, D6. Sets up D8 (workstreams become the 90-day plan), D20 (the skeleton shipped), D42 and D44 (the capstone and timed drills apply the method).

### Day 8 · Scoping the first 90 days: workstreams, sequencing by risk and value, what you will not do (~12 min)
- **Status:** new
- **What you learn:** how to turn the decomposition into a dated plan with overlapping phases, put the riskiest unknowns first, and write the list of things you will not build. It matters because day 90 is where most engagements are judged, and an unscoped engagement becomes the services trap from Day 3.
- **Topics:**
  - The published shape: discovery weeks 1 to 4, prototype weeks 3 to 6, productised and in daily use by day 90
  - Overlap on purpose: the prototype starts before discovery ends
  - Sequencing by risk: integration spikes and the security review start in week two
  - Sequencing by value: the slice that saves the most analyst hours ships first
  - Dependencies you do not control: access tickets, release freezes, audit month
  - The "will not do" list, each line with a reason and the person who agreed
  - What the customer's engineers own from day one, so that handoff is possible
  - Checkpoints at weeks 2, 4, 6 and 12, each with a question the customer answers
- **Real-time example:** the Godavari 90-day plan. Discovery in weeks 1 to 4; walking skeleton at week 3; security questionnaire from week 2 so the VPC can land by week 8; pilot in two branches in weeks 7 to 10; forty analysts by day 90. The "will not do" list has four lines: the branch CRM, collections summaries, any change to the core system's data model, and anything that sends customer PII outside India. The COO signs it.
- **Analogy (Telugu audience):** planning a wedding. The hall is booked first because it is scarce and risky, the caterer next, the invitations last because they are easy. Nobody prints invitations before the hall is confirmed.
- **Shorts:**
  - "Discovery weeks 1 to 4, prototype weeks 3 to 6. Yes, they overlap."
  - "The most important page of the plan is the list of what you will not build."
- **Callbacks:** builds on D3 (the services trap), D7. Sets up D9 (each workstream needs a number), D20 (the week-3 checkpoint), D23 (the review starts early), D28 (the 12-week handoff bar), D32 (defending the list).

### Day 9 · Success metrics and the business case: from "faster" to rupees, hours and risk (~11 min)
- **Status:** new
- **What you learn:** how to turn the sponsor's adjective into numbers, measure the baseline before building, and write a business case that survives a CFO. This Day owns the business case; Day 37 owns measuring the result. It matters because "it feels faster" does not renew a contract, and the golden eval set is agreed against these numbers.
- **Topics:**
  - From "faster" to metrics: turnaround days, analyst hours per file, send-back rate, audit findings, capital waiting to be disbursed
  - Leading indicators (files through the tool, review-queue size) versus lagging (turnaround, renewal)
  - Measure the baseline first: a two-week sample, counted the way the operators agree
  - Hours into rupees: loaded cost per analyst hour, disbursement pulled forward, the cost of a compliance finding
  - The golden set as a contract: 100 to 200 real examples, labelled by the customer's experts, agreed before a model is chosen (built in D14)
  - Targets as ranges, and what each stakeholder is promised
  - The numbers that get gamed, previewed (owned by D37)
- **Real-time example:** the Godavari baseline from a two-week sample: median turnaround 9.2 days, 4.5 analyst hours per file, 31 percent of files sent back at least once. The case: cutting intake and completeness checking from four days to one pulls disbursement forward on every loan, saves a measured share of analyst hours and catches missing documents on day one. Every number carries its method, and the COO's "three days" becomes "three to four days in the pilot branches by day 90".
- **Analogy (Telugu audience):** UPI. Nobody funded "convenient payments". They funded transactions per day, failure rate and seconds per payment. The number is what moved.
- **Shorts:**
  - "Faster is not a metric. 9.2 days to 3.5 is."
  - "Measure the baseline before you build, or you will never prove you helped."
- **Callbacks:** builds on D3 (ARR per FDE), D4 (measurable), D7 (step 2). Sets up D14 (the golden set), D19 (the quality dashboard), D29 (the weekly readout), D37 (measuring value honestly).

### Day 10 · The discovery document: writing it, defending it, and saying no (~12 min)
- **Status:** new
- **What you learn:** how to write the document that closes discovery, present it to a room that includes the people who can veto it, and say no to requests that would sink the engagement while keeping the relationship. It matters because interviewers ask you to describe this artifact, and the readout is the first time the customer sees you as a peer rather than a vendor.
- **Topics:**
  - The structure: problem statement, stakeholder map, real workflow, metrics and baseline, decomposition, 90-day plan, "will not do", risks, asks of the customer
  - Writing for a COO: one page first, appendices after, numbers with methods, no model names
  - The readout: who presents what, who must be in the room, what gets signed
  - Saying no with a reason and an alternative: "not now, because, and instead"
  - Role-plays: the COO who wants a chatbot added, the CISO who wants on-prem before any prototype, the VP who wants 100 percent accuracy
  - Turning objections into plan changes without reopening the scope
  - Versioning: updated at every checkpoint, never rewritten
- **Real-time example:** the Godavari readout, with the COO, the CISO, the compliance head, the ops lead and two senior analysts. The COO asks for the chatbot; you say not now, because it has no baseline, and offer to revisit after the pilot. The CISO asks for on-prem; you commit to a VPC in AWS Mumbai with no PII leaving India and to starting the security questionnaire in week two. The document is signed with four changes.
- **Analogy (Telugu audience):** the village panchayat. You lay out the case, every elder may object, the decision is made with everyone present, and it is written down so nobody reopens it next month.
- **Shorts:**
  - "The three words that keep a customer: not now, because."
  - "A discovery document the CISO signs beats a demo the COO loves."
- **Callbacks:** builds on D5 (who is in the room), D8, D9. Sets up D11 (building begins), D21 and D23 (the CISO's conditions), D29 and D30 (status and bad news), D32 (the governance line), D34 (the full drills).

---

## Sources

- Atlassian, Forward Deployed Engineering Playbook (frequent, painful, measurable; working backwards to the AI; the 12-week bar): https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook
- OpenAI forward deployed engineering, ZenML LLMOps database summaries (problems worth tens of millions, experts involved before building): https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production and https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption
- How FDEs run customer discovery in 2026 (8 to 10 end-user interviews, the real-workflow map): https://getperspective.ai/blog/how-forward-deployed-engineers-run-customer-discovery-2026
- The FDE discovery playbook: validating requirements before you build: https://getperspective.ai/blog/fde-discovery-playbook-validating-requirements-before-you-build-2026
- FDE first 90 days (days 1 to 2 access and reality, discovery weeks 1 to 4, prototype weeks 3 to 6, productised by day 90, the golden set before model choice): https://cloudsoftsol.com/blog/fde-first-90-days
- Harvard FAS Career Services, the FDE interview, 2026 guide (the decomposition framework and failure reasons): https://careerservices.fas.harvard.edu/blog/2026/08/01/forward-deployed-engineer-interview-the-definitive-2026-guide-fde/
- The Palantir decomposition interview, explained: https://fdeinterviews.com/guide/palantir-decomposition-interview
- The FDE playbook: a practitioner's field manual: https://conikeec.substack.com/p/the-forward-deployed-engineer-playbook
- Reserve Bank of India, Master Direction on Know Your Customer (KYC), 2016, as amended (the mandatory documents behind the completeness check): https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566

The interview and discovery sources are career-prep or vendor content; the method is quoted as
they describe it. Godavari Finance, its numbers and its people are invented.
