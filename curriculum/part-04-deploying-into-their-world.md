# Part 4 · Deploying Into the Customer's World

> Taking the Day 20 walking skeleton into Godavari Finance's own AWS account: deployment model, identity, the security review, Indian data law, network, CI/CD into infrastructure you do not own, reliability across two companies, and the handoff · Days 21 to 28 · 8 episodes · ~96 min

*Why this Part exists in 2026: the model is the easy part. What separates an FDE from an
application engineer is that the system has to run inside someone else's company, in a VPC or
data centre you do not own, behind their SSO, past the CISO's 200-question spreadsheet, under the
DPDP Act and RBI's outsourcing rules, and keep running after you leave. Buyers in regulated
sectors treat "SaaS only, no self-hosted path" as a red flag, and "no customer PII leaves India"
decides which models you may even call. Every chapter here is a gate the Godavari engagement must
pass before go-live on Day 26 and handoff on Day 28. Mechanics owned elsewhere (Terraform, CI/CD,
Kubernetes, SLOs) are linked, not re-taught.*

---

### Day 21 · Deployment models: SaaS, VPC, on-prem, air-gapped, and how to choose with a CISO in the room (~12 min)
- **Status:** new.
- **What you learn:** the four ways a vendor's system can run (multi-tenant SaaS, single-tenant VPC, on-prem, air-gapped) and how one codebase switches between them by configuration. Regulated buyers treat SaaS-only with no self-hosted path as a red flag, and the choice is made in the first security call.
- **Topics:**
  - The four models: who holds the data, the keys, the uptime and the upgrade burden
  - Single-tenant in the customer's account versus the vendor's: who pays, who patches, who sees logs
  - On-prem and air-gapped: no outbound internet, weights and images shipped as artifacts
  - One codebase, four targets: configuration-driven adapters for storage, secrets, model endpoint, identity
  - The trade-off table a CISO reads: control versus update speed versus cost
  - Why SaaS-only loses regulated deals, and the self-hosted path as a sales requirement (questionnaire preview; Day 23 owns it)
- **Real-time example:** Godavari's CISO opens with "where does the PDF go?". The compliance head rejects multi-tenant SaaS; the COO wants weekly updates, so air-gapped is out; you converge on single-tenant in Godavari's AWS Mumbai account, and write the decision record Day 23 will quote.
- **Analogy (Telugu audience):** catering a wedding. The caterer can cook in his own kitchen and deliver (SaaS), cook in your pandal on your gas (VPC), or hand over the recipe and leave (on-prem).
- **Shorts:**
  - "SaaS-only with no self-hosted option? In banking that is a red flag, not a feature."
  - "One codebase, four deployment models. The switch is a config file, not a rewrite."
- **Callbacks:** builds on D5 (the blockers), D16 (data you may not copy), D20 (the skeleton). Sets up D22, D23, D24, D26, D40.

### Day 22 · Identity in someone else's company: SSO (Okta, Entra, AD), RBAC, service accounts, and permission-aware everything (~12 min)
- **Status:** new.
- **What you learn:** how to plug into the customer's identity provider instead of keeping your own user table, how directory groups flow into app roles and into retrieval, and how service accounts are issued and rotated. The first production bug an FDE sees is usually an analyst seeing a document they should not.
- **Topics:**
  - SSO in practice: OIDC and SAML against Okta, Microsoft Entra ID, or on-prem Active Directory via federation
  - Groups from the directory, not your app: synced on login or by SCIM
  - RBAC mapping directory groups to app roles (analyst, reviewer, branch manager, auditor read-only)
  - Service accounts and workload identity: least privilege, no shared passwords, rotation
  - What groups mean for retrieval: ACLs on every chunk, filtered at query time (Day 15 owns the retrieval half)
  - Audit logs the auditor can read: who saw which document, when, through which query
- **Real-time example:** Godavari runs on-prem Active Directory with a cautious Entra ID sync. You wire the app to Entra, map AD groups (credit-ops-hyd, credit-ops-vja, branch-managers, audit-readonly) to roles, and put group ACLs on the index so a Vijayawada analyst never sees a Hyderabad loan file.
- **Analogy (Telugu audience):** the wedding hall gate. The family hands the gatekeeper one guest list; he does not keep his own.
- **Shorts:**
  - "Your app should not have a users table. Their directory is the users table."
  - "Permission-aware retrieval: the search index must know who is asking."
- **Callbacks:** builds on D15 (permission-aware retrieval), D21. Sets up D23, D24, D25 (workload identity for the gateway), D41 (exfiltration through tools).

### Day 23 · The security review and procurement: SOC 2 Type 2, DPA, subprocessors, training-use policy, retention, the questionnaire (~13 min)
- **Status:** new.
- **What you learn:** how to read your company's SOC 2 Type 2 report the way a customer's security team does, what a DPA commits you to, and how to answer the questionnaire that decides whether procurement issues the order. This chapter owns the questionnaire.
- **Topics:**
  - SOC 2 Type 2: scope, auditor, period, exceptions
  - The DPA: fiduciary versus processor, purpose limitation, sub-processing, audit rights, deletion on exit
  - The subprocessor list: every vendor that touches customer data, including the model provider and the error tracker
  - The training-use policy: "no model trains on our data" as a contract term, and how to prove it
  - Retention and deletion by data type, encryption and customer-managed keys, breach notification timelines
  - The questionnaire: answering honestly without saying "no", the evidence folder, the cover note
- **Real-time example:** the 212-question spreadsheet arrives. You and Kaagaz AI's one-person security function answer it in a week: the SOC 2 report with two exceptions explained, the DPA with the no-training clause, the subprocessor list, 30-day retention for raw documents, a customer-managed KMS key. The compliance head signs; procurement issues the order.
- **Analogy (Telugu audience):** the family doctor opening a new clinic. The inspector does not ask whether she is a good doctor; he asks for the registration, the waste contract and the fridge log.
- **Shorts:**
  - "SOC 2 Type 2 is not a badge. Read the period and the exceptions."
  - "The subprocessor list is where the error tracker in Virginia gets caught."
- **Callbacks:** builds on D10, D21, D22. Sets up D24 (residency annex), D25, D32 (handling a refusal), D42.

### Day 24 · Data residency and Indian law: DPDP Act, RBI guidance, "nothing leaves India", and what that means for model choice (~13 min)
- **Status:** new.
- **What you learn:** what the DPDP Act 2023 and its 2025 Rules make a lender and its vendor responsible for, which RBI directions bind an NBFC's vendor, and how to map every place data goes. "No customer PII leaves India" decides which models you may call.
- **Topics:**
  - DPDP Act 2023: fiduciary (Godavari) and processor (Kaagaz AI), consent, retention and erasure, breach reporting, cross-border transfer by restriction list
  - DPDP Rules 2025 (G.S.R. 846(E), 13 November 2025): most business obligations commence 18 months after publication
  - RBI Master Direction on Outsourcing of IT Services (effective 1 October 2023): board policy, due diligence, audit access, data location, exit
  - RBI KYC Master Direction: the PDFs you chunk are KYC records with record-keeping periods retention must respect
  - Residency as contract plus map: stores, backups, logs, model endpoints, subprocessors
  - What "nothing leaves India" forces: India-region endpoints, self-hosted models in the VPC, or redaction before any call
- **Real-time example:** you draw Godavari's residency map: S3 and RDS in ap-south-1, backups in ap-south-2, the model provider's Mumbai endpoint, and one monitoring vendor storing in the United States, which the compliance head spots. You swap in a self-hosted stack; the map becomes the DPA's residency annex.
- **Analogy (Telugu audience):** the village elders' rule for land papers: originals never leave the village. Copies are made in the panchayat office.
- **Shorts:**
  - "No PII leaves India. That sentence chooses your model for you."
  - "Residency is not a region setting. It is a map of every place a byte can go."
- **Callbacks:** builds on D16, D22, D23. Sets up D25 (region pinning, the gateway), D40 (self-hosted models), D42.

### Day 25 · Network, secrets and egress: private endpoints, allowlists, KMS, and the model gateway (~11 min)
- **Status:** new.
- **What you learn:** how to make the system reachable only from inside the customer's network, able to reach only an agreed list of destinations, with keys the customer controls, and with every model call passing through one gateway you can audit, meter and switch off.
- **Topics:**
  - No public IPs: private subnets, an internal load balancer, VPN or Direct Connect for branches
  - Private endpoints for storage, KMS, secrets and the model provider where offered
  - Egress allowlists through a proxy: the exact outbound list, and the alert when something new appears
  - Secrets in the customer's secrets manager, injected at runtime, never in images or environment files
  - KMS with customer-managed keys: rotation, and what happens when the customer revokes the key
  - The model gateway: authentication, provider allowlist, redaction of PAN and Aadhaar, logging, cost metering, rate limits, a kill switch
- **Real-time example:** Godavari's CISO asks for every outbound destination. The allowlist has four entries, provable from proxy logs. The gateway becomes the home of the "redact PAN and Aadhaar before any model call" rule, so it holds for the next workflow Godavari builds without you.
- **Analogy (Telugu audience):** a house warming. One door, one uncle at it who knows who comes in and what goes out, instead of every room having its own exit.
- **Shorts:**
  - "Four outbound destinations. If you cannot list them, you do not know your system."
  - "Every model call goes through one door. That door is where governance lives."
- **Callbacks:** builds on D12 (retries and budgets, now metered), D22, D23, D24. Sets up D26 (IaC keeps the diagram true), D27 (kill switch, fallback provider), D41.

### Day 26 · Shipping into infrastructure you do not own: CI/CD into the customer's account, IaC for a customer VPC, environments and rollback (~12 min)
- **Status:** new.
- **What you learn:** how to deploy from your pipeline into an AWS account the customer owns, with a role they can revoke in one line, Terraform state they hold, environments they approve, and a rehearsed rollback. The DevOps Masterclass owns the mechanics; this chapter covers what changes when the account is not yours.
- **Topics:**
  - The trust boundary: an IAM role in their account trusting your CI provider through OIDC, scoped to one repository, no long-lived keys
  - Terraform for the customer VPC: state and locks in their account, modules you maintain, variables they own
  - Environments: dev in your account on synthetic data, UAT and prod in theirs
  - Their change management: ticket, window, and the engineer who reviews the plan
  - Rollback: signed images, reversible migrations, prompt and eval versions pinned per release (Day 13)
  - Mechanics linked: learn-cicd Days 3 and 4, learn-terraform Days 11 and 14, learn-aws, snapvault
- **Real-time example:** go-live week. Godavari's cloud team creates a role trusting Kaagaz AI's GitHub organisation through OIDC. UAT runs with ten analysts for two weeks; prod cutover is on a Saturday, rollback rehearsed the day before. They can delete the trust policy in one line, which is the point.
- **Analogy (Telugu audience):** driving a hired auto. The owner keeps the RC book and can take the keys back any day.
- **Shorts:**
  - "No access keys in their account. OIDC, one role, revocable in one line."
  - "Terraform state lives in the customer's account. It is their infrastructure."
- **Callbacks:** builds on D13, D20, D25. Sets up D27, D28 (they deploy without you).

### Day 27 · Reliability in their production: SLOs for an AI system, on-call across two companies, incidents and postmortems with a customer (~12 min)
- **Status:** new.
- **What you learn:** how to define "working" for an AI system in numbers the COO and CISO accept, who gets paged when the fault could be yours, theirs or the model provider's, and how to run an incident and postmortem with your customer in the room. Fundamentals are owned by learn-sre.
- **Topics:**
  - Four SLOs: availability, p95 latency, a quality SLO from sampled outputs scored against the Day 14 eval set, cost per document
  - Who owns what, and who gets paged: vendor the application, customer network and identity, provider the model; the shared channel
  - Error budgets both companies sign
  - Degradation by design: queue and route to human review, never silent failure
  - Incident communication with a customer: first message within minutes, updates on a cadence
  - The joint postmortem: blameless inside a contract, one owner per action, readable by the RBI auditor (learn-sre Days 2, 4, 5)
- **Real-time example:** two weeks after go-live, the model provider's Mumbai endpoint slows four times over. The fallback routes documents to the review queue; you post on the shared channel within 15 minutes; the postmortem's one action is a second provider behind the Day 25 gateway.
- **Analogy (Telugu audience):** the family doctor and the hospital. The doctor knows the patient, the hospital has the ICU, and the referral note says who does what at 2 a.m.
- **Shorts:**
  - "An AI system needs a quality SLO. 99.9 percent available and wrong is an outage."
  - "The model provider is down. Who gets paged, you or the customer? Decide before go-live."
- **Callbacks:** builds on D14 (evals as the quality SLO), D19, D25, learn-sre. Sets up D28, D30 (the outage conversation), D37 (MTTR as value).

### Day 28 · Handoff and self-sufficiency: runbooks, enablement, the 12-week bar, and knowing when you are done (~11 min)
- **Status:** new.
- **What you learn:** how to leave: the handoff pack, training the customer's engineers and operator champions until they run a change end to end without you, and the bar Atlassian's playbook describes, roughly twelve weeks to measurable value. An FDE who cannot leave has become a contractor.
- **Topics:**
  - Definition of done: their team deploys, debugs, updates a prompt, reruns evals and reads dashboards without you
  - The handoff pack: runbooks per alert, architecture and residency map, the eval set, decision records, contacts
  - Enablement that works: pairing on real changes, not slide decks; two engineers and one operator champion
  - Governance as architecture: permissions, security and auditability from day one, autonomy increased as trust grows
  - The 12-week bar: Discover, Build, Adopt, Value
  - Signs you are not done: every change still routes through you, the champion has left
- **Real-time example:** Godavari's two cloud engineers and a credit-ops lead take a prompt change through evals, UAT and prod with you silent. The COO's readout shows turnaround at 4.2 days from 9. You hand over the pack, agree a 30-day warranty and a monthly check-in, and go home.
- **Analogy (Telugu audience):** the exam tutor whose job is finished when the student solves the paper alone. A tutor who has to sit in the exam hall has failed.
- **Shorts:**
  - "You are done when they ship a change without you on the call."
  - "Governance from day one, autonomy as trust grows. That is how an FDE leaves."
- **Callbacks:** builds on D3 (the services trap), D8, D26, D27. Sets up D29, D33 (adoption after you leave), D35, D38.

---

## Research sources

- Atlassian, Forward Deployed Engineering: the four phases over roughly twelve weeks (Discover, Build, Adopt, Value), governance and playbooks in the Adopt phase, and the published case results. https://www.atlassian.com/enterprise/success/fde and the playbook summary https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook
- ZenML LLMOps database, OpenAI forward deployed engineering (two interviews): enterprise deployment, governance as architecture, autonomy increased as trust grows. https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production and https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption
- The Digital Personal Data Protection Act, 2023 (official text, MeitY): https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf and MeitY's data protection framework page https://www.meity.gov.in/data-protection-framework
- The Digital Personal Data Protection Rules, 2025, G.S.R. 846(E), notified 13 November 2025, with phased commencement (most obligations 18 months after publication). Official text via the Gazette of India and MeitY; a dated summary: https://www.mondaq.com/india/data-protection/1708164/digital-personal-data-protection-rules-2025-notified
- RBI, Master Direction on Outsourcing of Information Technology Services (10 April 2023, effective 1 October 2023), applicable to banks and NBFCs: https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12486
- RBI, Master Direction, Know Your Customer (KYC) Direction, 2016 (as updated): https://www.rbi.org.in/Scripts/BS_ViewMasterDirections.aspx?id=11566
- RBI, Storage of Payment System Data (circular of 6 April 2018), the localisation precedent: https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11244
- Enterprise AI agent compliance and deployment guide (residency, on-prem, VPC): https://www.sim.ai/library/enterprise-ai-agent-compliance-deployment-guide
- Enterprise AI vendor evaluation: a security and compliance checklist (SOC 2, DPA, subprocessors, training use): https://tejasraundal.github.io/Teclops-AI/blog/enterprise-ai-vendor-security-compliance-checklist/
- The FDE playbook: a practitioner's field manual (deployment models, the self-hosted path as a buying requirement): https://conikeec.substack.com/p/the-forward-deployed-engineer-playbook
- Mechanics owned elsewhere: DevOps Masterclass [learn-cicd](../../DevOps/learn-cicd/README.md) (Days 3 and 4: secrets, OIDC, continuous deployment), [learn-terraform](../../DevOps/learn-terraform/README.md) (Days 11 and 14), [learn-aws](../../DevOps/learn-aws/README.md), [learn-sre](../../DevOps/learn-sre/README.md) (Days 2, 4, 5), [learn-observability](../../DevOps/learn-observability/README.md) (capstone on snapvault)

## Notes for writers

- Day 23 owns the security questionnaire. Day 21 may preview it in one line; Day 32 handles the refusal case only.
- Day 15 owns the retrieval half of permission-aware retrieval and Day 22 the identity half. Day 24 adds residency and must not re-teach either.
- Do not re-teach Terraform, GitHub Actions, OIDC, Kubernetes, SLO maths or incident command. Link the DevOps Masterclass and learn-sre chapters by Day.
- Compliance detail dates fast. Every DPDP and RBI statement names the instrument and its date, and the chapter says "check the current text" where a number (retention periods, commencement dates) could move. The 2018 payment-data localisation circular may be cited in Day 24 as the precedent the compliance head has in mind.
- All Godavari numbers (212 questions, 4.2 days, four outbound destinations) are synthetic and must be presented as the course's invented engagement, never as a real company's results.
- The Atlassian case figures and "roughly twelve weeks" are vendor-published and are quoted as such.
