# Part 7 · The AI-Era FDE Toolkit

> Using coding agents on code you do not own, building when the agent is restricted or forbidden, and attacking your own deployment before someone else does · Days 39 to 41 · 3 episodes · ~37 min

*Why this Part exists in 2026: an FDE now ships most deployment code with a coding agent, and most of that code lives in the customer's repositories, under the customer's DPA, next to the customer's PII. The same year, OWASP's field reporting on agentic systems found prompt injection tying together most of the documented production failures, and the coding-agent-in-CI incidents of early 2026 showed that a single untrusted string (an issue title) can reach a component holding publishing credentials. The CISO who let you in on Day 21 will ask how you use these tools on their code, and whether your own pipeline is the next incident. Part 7 gives you the answer: least privilege, instruction files, audit trails, constrained builds, and a red-team you run yourself.*

---

### Day 39 · Coding agents on customer code: permissions, instruction files, audit trails, what never goes in the context (~12 min)
- **Status:** new.
- **What you learn:** how to use a coding agent on a customer's codebase in a way their security team can accept: least-privilege permissions, an instruction file the customer reviews, a record of everything the agent did, and a hard list of what never enters the context. Their environment or yours changes every answer, so decide that first.
- **Topics:**
  - Least privilege: allowlists and denylists for tools, commands, directories and domains, in a managed policy the customer controls
  - Instruction files as a contract: may touch, must ask, must never; reviewed like any other change
  - The audit trail: session logs and every tool call, kept where the customer's auditor can read them
  - What never enters the context: customer PII, secrets, DPA-covered data, production databases; hooks that enforce it
  - Their environment versus yours: whose model, logs, egress and key (Day 25's gateway rules apply)
  - Synthetic fixtures only; review gates where the agent proposes and a human merges
  - The questionnaire line "do you use AI coding tools on our code?" and the boring, honest answer
- **Real-time example:** Godavari's CISO allows agents on the SOAP adapter only inside Godavari's AWS Mumbai account, through the Day 25 gateway, with a deny rule on the `loans_prod` schema and the SFTP drop, and session logs shipped to their SIEM. You write the instruction file with their platform lead; the first pull request is reviewed with the log beside it.
- **Analogy (Telugu audience):** giving the plumber the house key. He gets the bathroom, not the bedroom; the cupboard with the gold stays locked; someone stays in the house; the work is checked before he leaves.
- **Shorts:**
  - "You used an AI coding tool on the bank's code. Where did the code go?"
  - "The one file a CISO should read before your agent touches their repo."
- **Callbacks:** builds on Day 23 (questionnaire), Day 25 (egress, gateway), Day 26 (CI/CD into their account), learn-ai-ml Days 88 to 94 (coding agents, hooks, review gates). Sets up Days 40 and 41.

### Day 40 · Building with AI under constraints: air-gapped assistants, self-hosted models, and when the agent is not allowed (~11 min)
- **Status:** new.
- **What you learn:** how to keep building well when the customer's rules remove most of your tools: an assistant with no internet, a model hosted inside their network, a slower loop with a smaller model, and the case where the agent is forbidden and you write the code by hand while keeping the discipline the agent would have imposed.
- **Topics:**
  - The constraint ladder: SaaS agent, agent via gateway, agent in their VPC, self-hosted model, no agent; which Day 24 rule pushes you down a rung
  - Air-gapped assistants: a local model, documentation mirrored in, no telemetry; what you lose and keep
  - Self-hosted models: size against the real task, not the leaderboard; serving is owned by learn-mlops
  - A weaker model: smaller tasks, more tests, the Day 14 eval set as the net
  - When the agent is not allowed: spec first, tests first, small commits, the same review checklist
  - Saying what the constraint costs in days, in the status update (Day 29)
- **Real-time example:** Godavari's on-prem segment, where the core lending system lives, has no outbound internet. For the SOAP adapter you work on a locked laptop with a self-hosted model and mirrored docs; for the audit-sensitive reconciliation module the compliance head refuses any AI tool, so you write it by hand, tests first, against the checklist the agent would have faced.
- **Analogy (Telugu audience):** the exam hall. Outside you had the phone, the guide and the tuition teacher. Inside it is you, a pen and what you actually learned. Prepare for the hall, not the hostel room.
- **Shorts:**
  - "The customer said no AI tools. Here is how I still shipped in a week."
  - "Choosing a self-hosted coding model: ignore the leaderboard, run your own tests."
- **Callbacks:** builds on Day 21 (deployment models), Day 24 (residency and model choice), Day 25 (the gateway), Day 39 (permissions). Sets up Day 41 (the constrained setup is also the safer one) and Day 46.

### Day 41 · Red-teaming your own deployment: prompt injection, OWASP LLM Top 10, data exfiltration through tools (~14 min)
- **Status:** new. Course owner of prompt injection and tool exfiltration.
- **What you learn:** how to attack your own Godavari deployment before an auditor, a researcher or a criminal does. The OWASP Top 10 for LLM Applications is the checklist; prompt injection, which OWASP's 2026 agentic reporting found tying together most documented production failures, is the attack; untrusted input reaching a component with credentials or tools is the path. Then design so that a fooled model cannot cause an unrecoverable action.
- **Topics:**
  - The OWASP Top 10 for LLM Applications as a review checklist, prompt injection at LLM01
  - Direct and indirect injection: instructions hidden in a PDF, an email, a ticket, an issue title
  - The dangerous triangle: untrusted input, a model with tools, a credential or egress path in one component; exfiltration through a fetch, an email tool or a file write
  - The 2026 pattern: a coding agent in CI reads an issue title as instructions and reaches publishing secrets (Cline's "Clinejection", Feb 2026); a tool-server package adds one line that copies data out (postmark-mcp, Sept 2025)
  - Assume the model will be fooled: least privilege per tool, human checkpoints on destructive actions (Day 17), full audit trails, deterministic guards it cannot override (Day 11), a small blast radius and a way back
  - The exercise: a threat model, injection fixtures in the eval set, a findings page the CISO signs
- **Real-time example:** you plant a loan PDF in Godavari's test queue with hidden white text telling the extraction agent to post the file to an external URL and approve the application. The Day 20 pipeline has a fetch tool and an SFTP tool. The red-team shows which Day 17 checkpoints stop it, which log line would have caught it, and where a deny rule was missing.
- **Analogy (Telugu audience):** the "share your OTP" call. A clever voice can fool anyone's grandmother for a minute. The bank does not make grandmothers unfoolable; it sets daily limits, confirms large transfers twice and keeps a record it can reverse. Design for the grandmother, not the genius.
- **Shorts:**
  - "A GitHub issue title stole publishing credentials. Your document pipeline has the same shape."
  - "Hidden text in a PDF told the AI to approve the loan. Here is why it could not."
- **Callbacks:** builds on Day 11 (deterministic versus LLM), Day 16 (SFTP integrations), Day 17 (approvals), Day 25 (egress), Day 39 (agent permissions), learn-ai-ml Days 96 and 97 (general OWASP and agent security). Sets up Day 42 (the capstone red-team page) and Day 44 (trust boundaries in design drills).

---

## Sources

- OWASP Top 10 for LLM Applications, official project page: https://genai.owasp.org/llm-top-10/ (OWASP GenAI Security Project home: https://owasp.org/www-project-genai-security/)
- OWASP GenAI Security Project, State of Agentic AI Security and Governance v2.01 (June 2026), as reported by Help Net Security, "Prompt injection still drives most agentic AI security failures in production": https://helpnetsecurity.com/2026/06/11/owasp-prompt-injection-ai-security-failures (secondary; check the OWASP PDF for exact wording)
- Adnan Khan, "Clinejection: compromising Cline's production releases just by prompting an issue triager" (Feb 2026), the primary disclosure: https://adnanthekhan.com/posts/clinejection/
- Cloud Security Alliance research note on the Claude Code GitHub Action permission bypass (CVE-2025-66032, disclosed June 2026): https://labs.cloudsecurityalliance.org/research/csa-research-note-claude-code-github-action-prompt-injection/ (secondary)
- Cloud Security Alliance research note, "Comment and control: when a GitHub issue steals CI secrets" (untrusted GitHub metadata as prompt content across several coding agents): https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-coding-agent-ci-prompt-injection-202608/ (secondary)
- The postmark-mcp backdoor (hidden BCC in a tool-server package, Sept 2025), summarised in UpGuard's MCP security incidents page: https://upguard.com/blog/mcp-security-incidents (secondary)
- Claude Code documentation, configuring permissions (allow and deny rules, permission modes, managed policies): https://code.claude.com/docs/en/permissions
- Claude Code best practices (instruction files, workflow): https://code.claude.com/docs/en/best-practices
- Enterprise AI agent compliance and deployment guide (air-gapped, on-prem, VPC): https://www.sim.ai/library/enterprise-ai-agent-compliance-deployment-guide

## Notes for writers

- Day 41 owns prompt injection and tool exfiltration. Day 17 keeps a one-line preview only; learn-ai-ml Days 96 and 97 own the general OWASP material, so Day 41 applies the list to the Godavari deployment rather than re-teaching every entry.
- Careful claims. For Clinejection, say what the primary post says: the triage workflow interpolated the issue title into the prompt with broad tools; the author disclosed it; a tampered npm release followed and was remediated within hours; the author did not himself confirm that the two were the same actor. Do not quote machine counts from vendor blogs. For the OWASP 2026 figure, use the Help Net Security wording ("ties most of these incidents together") unless the PDF is checked.
- Name no real customer. Godavari's red-team findings are invented.
- Tool names and permission syntax date in months; keep them in the "Build it with AI" section, not in the main text.
