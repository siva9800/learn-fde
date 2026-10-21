# 06 · Titles, Neighbours and Three Employers: Reading What a Posting Means

> Day 2 · Section 6 of 12 · [Chapter overview](README.md) · Previous: [05 · Two weeks at Godavari](05-two-weeks-at-godavari.md) · Next: [07 · Production concerns](07-production-concerns.md)

---

## 6.1 The six title variants and what each emphasises

The June 2026 posting analysis (section 02) groups 2026 titles into six variants; Day 3 adds that about
a third of the market hires under adjacent titles, and prices each. Here the question is only: which
bucket is the title over-weighting?

| Title | Who uses it (as listed in the analysis) | What it emphasises | Bucket weighting to expect |
|---|---|---|---|
| **Forward Deployed Engineer** | Palantir, OpenAI, Anthropic | full-cycle build and deploy inside the customer | all three, close to 60/30/10 |
| **Forward Deployed AI Engineer** | Google, Scale AI, Cohere | LLM integration into customer workflows | bucket 2 heavier; bucket 1 assumed |
| **Applied AI Engineer** | Anthropic, Mistral | prototype-to-production for named accounts | bucket 2 heaviest, evals especially; the account is already won |
| **Deployment or Solutions Engineer** | Databricks, Snowflake | implementation of a more-shipped product | bucket 1 heavier; a mature product leaves less bucket 2 judgement |
| **Forward Deployed Software Engineer (FDSE)** | Palantir, Hebbia | heavy coding, embedded on site | bucket 1 heaviest, on site; the Palantir original |
| **FDE / Solutions Architect (hybrid)** | mid-market AI startups | pre-sale and post-sale blended | bucket 3 heaviest and starts before the deal; read most carefully (Day 3) |

Read the title, then the first five bullets against the three buckets. A "Forward Deployed AI
Engineer" posting whose bullets are all bucket 2 is honest. A "Forward Deployed Engineer" posting whose
bullets are all bucket 1 and whose team is called "delivery" is probably a services role; Day 3 teaches
the other signs.

## 6.2 The three neighbours

| | Solutions engineer | Consultant | Applied AI engineer | Forward deployed engineer |
|---|---|---|---|---|
| **When you arrive** | before the deal | with a contract for a defined project | after the deal, on a named account | after the deal, in the customer's environment |
| **What you build** | the demo, the proof of concept | a recommendation, or a one-off build | the production AI system for that account | the production system, in their environment, that becomes product patterns |
| **How you are paid** | variable pay tied to deals closed | billed hours or a project fee | salary, on the outcome | salary, on the outcome; the team measured on recurring revenue per FDE (Day 3) |
| **When you leave** | when the deal closes | when the project ends | when the system is stable | when the customer's team runs it without you (about twelve weeks at Atlassian) |
| **What you owe your own company** | the pipeline | nothing beyond the invoice | the account | the patterns that make the next customer cheaper |
| **Bucket weighting** | 3 heavy, 1 and 2 shallow | 3 heavy, 1 variable, 2 shallow | 2 heaviest, 1 solid, 3 present | 60/30/10 across all three |

The April 2026 Paraform comparison puts it in one line worth memorising for "how is this not a solutions
engineer": **"The SE sells the vision. The FDE builds it. The CE maintains it."** It adds that an SE's
pay "leans heavily on variable pay tied to deals closed" and that "an FDE writes production code, but
not for the core product". Day 0 gave one test (if you could do it without seeing the customer's data,
systems or people, it is not the FDE job); the table adds the second: **if you are paid on the deal or on
the hours, it is not the FDE job either.**

The applied AI engineer is the nearest neighbour, and postings often use the two titles for the same
work. The difference is weight, not kind: more evals, more model behaviour, usually an account already
won, a team that may sit in product rather than the field. If you are strong in bucket 2 and weak in
bucket 3, it is the better first title; the course is the same.

## 6.3 A day at three employers

The composite days below are built from the published sources in section 12 (the OpenAI and Ramp
interviews, Atlassian's playbook, the July 2026 India market report) and the posting analysis. **They
describe no single employer's schedule.** They show which bucket each kind of employer over-weights, so
you can read a posting against the company that wrote it.

### A frontier lab (an OpenAI or Anthropic-shaped team)

| Hour | What | Bucket |
|---|---|---|
| 09:00 | engagement stand-up: ten major engagements across the team; yours is a semiconductor manufacturer's yield-analysis problem the post-training team is interested in | I |
| 10:00 | call with the customer's process engineers through last night's eval failures case by case; they explain why the model was wrong on a particular wafer map | C |
| 12:00 | writing those cases into the golden set; the customer's expert signs each | C, then D |
| 14:00 | building the tool the model needs to query the customer's historian database; their data engineer on the call | D |
| 16:00 | pattern note to the research team: this class of failure appears in three engagements; what a capability change would need | I |

Over-weighted: the **internal** slice, because feeding product and research is half the reason the team
exists; OpenAI describes exactly two kinds of engagement, repeatable ones that become products and hard
ones worked with post-training. Under-weighted relative to Godavari: bucket 1 plumbing, which the lab's
product and coding agents absorb. The risk: the customer becomes a research subject rather than an
operator, and adoption (Day 33) is nobody's job.

### A vertical-AI startup (a Harvey, Sierra or Decagon-shaped team)

| Hour | What | Bucket |
|---|---|---|
| 09:00 | three customer calls back to back, Ramp-style: five to six accounts each, mostly remote; each call a configuration or integration question on the same product | C |
| 11:30 | the fourth account's integration: their ticketing system's API, a webhook that fires twice | D |
| 14:00 | workshop with the fifth account's operations team on which conversations the agent may handle and which it must hand to a human (Day 32) | C |
| 16:00 | the sixth account's weekly metrics: deflection, escalations, the operator who will not switch | C |
| 17:00 | one message to product: the "fires twice" webhook is the third account with the same problem; one product fix, not three custom ones (Day 35) | I |

Over-weighted: **customer-facing hours spread thin** across many accounts, and bucket 1 as integration
and configuration of one product rather than bespoke pipelines; bucket 2 judgement is mostly already in
the product. The risk: six accounts at an hour each is support, not forward deployment, unless the
patterns go back to product. Ramp's measure (enterprise revenue over FDE salaries) is what keeps it
honest; Day 3 explains why.

### An Indian IT services firm (a BCG X, QuantumBlack or large-SI-shaped team)

| Hour | What | Bucket |
|---|---|---|
| 09:00 | on the client's premises in Mumbai, badge and client laptop; the engagement is staffed against a statement of work with a named deliverable and an end date | C |
| 10:00 | the client's steering meeting; the partner presents, you answer the technical questions | C |
| 11:30 | building the agentic workflow on the client's cloud account per the SOW, in their tooling | D |
| 15:00 | the client's security team wants a change; it is out of scope; the engagement manager raises a change request | C |
| 17:00 | timesheet | neither |

Over-weighted: **buckets 1 and 3 in service of a deliverable**, with the consultancy, not you, owning the
outcome; the July 2026 India report says it in those words for the services tier. Missing: the
**internal slice is near zero**, because there is no product to feed; what you learn goes into the next
SOW. This is the day most Indian FDE postings in 2026 describe, under the FDE title (Day 3 names the
employers and the tier). It can be excellent training in buckets 1 and 3. It is not the FDE model, and
the tell is the missing 10 percent. Godavari, at such a firm, would be a six-month SOW with a change
request for the tracker.

## 6.4 Key takeaways

- Six title variants; read the title for which bucket is over-weighted, then the bullets against all
  three.
- SE sells the vision, FDE builds it, CE maintains it. Paid on the deal or the hours means not the FDE
  job.
- The applied AI engineer is the nearest neighbour: same work, heavier on bucket 2, usually a won
  account.
- Lab days over-weight internal; vertical-AI days spread customer-facing thin; services days have no
  internal slice, and that missing 10 percent is the tell.
