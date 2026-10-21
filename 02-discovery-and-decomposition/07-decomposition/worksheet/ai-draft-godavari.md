# Decomposition worksheet · Godavari Finance (AI draft, for exercise 3.1)

> This worksheet was produced by a coding agent from the one-line prompt "Decompose: an NBFC wants loan
> turnaround from 9 days to 3; fill the Day 7 worksheet." It is kept as written so that you can review it.
> It reads well. It is wrong in at least eight places. Find them before you read the solution in
> section 15. Run `python code/plan_from_worksheet.py worksheet/ai-draft-godavari.md` to see which ones
> the script catches and which ones only a human can.

**Customer:** Godavari Finance Ltd · **Sponsor:** CTO · **Date:** · **Author:** agent

## Step 1 · Clarify the goal and the trade-off

| Question | Answer |
|---|---|
| The goal in the sponsor's words | Reduce loan turnaround from 9 days to 3. |
| The goal rewritten as an outcome with a number and a date | 3-day turnaround for all loans within 6 weeks. |
| What is being optimised | Speed and accuracy. |
| What is being traded away, and who decides how much | Nothing significant; the LLM will improve both. |
| The constraint that cannot move | Budget. |
| What the sponsor would accept as "done" | The RAG chatbot deployed to all 300 branches. |
| Assumptions I am making (to revisit) | Loan data is available in a structured database. |

## Step 2 · Stakeholders and the metric each accepts

| Stakeholder | Role | What they want | The metric they would accept | What they fear |
|---|---|---|---|---|
| CTO | sponsor | modern AI stack | turnaround | vendor lock-in |
| Loan officers | operators | faster approvals | turnaround | job loss |
| IT team | blocker | minimal integration work | uptime | downtime |

## Step 3 · Map the inputs

| Input | Shape | Owner | Freshness | Access today | What is missing or untrustworthy | Architecture risk |
|---|---|---|---|---|---|---|
| Loan applications database | PostgreSQL table with 50,000 historical applications and approval labels | IT | real time | REST API | none | none |
| Customer documents | PDFs in an S3 bucket | IT | real time | S3 | some scans are low quality | OCR quality |
| Credit bureau API | JSON | CIBIL | real time | API key | rate limits | latency |

**Data that does not exist yet (and who will create it):** none; everything needed is available.

## Step 4 · Workstreams, sequenced by risk and value

| # | Workstream | Value (1 to 5) | Risk (1 to 5) | Depends on | Weeks | Owner | Why this score |
|---|---|---|---|---|---|---|---|
| W1 | Build RAG pipeline over loan documents (vector DB, embeddings, LLM) | 5 | 2 | | 2 | agent | core feature |
| W2 | Fine-tune the LLM on the 50,000 historical approvals | 5 | 3 | W1 | 3 | agent | improves accuracy |
| W3 | Chatbot UI for loan officers | 4 | 1 | W2 | 1 | agent | user-facing |
| W4 | Integration with the core system via REST | 3 | 2 | W3 | 1 | IT | plumbing |
| W5 | Evaluation on held-out approvals | 2 | 1 | W2 | 1 | agent | standard ML practice |

**Out of scope for now (each with a reason):** none.

## Step 5 · The walking skeleton

| Layer | What the thin version does | What is stubbed or manual | What it proves |
|---|---|---|---|
| Input | all loan documents indexed into the vector DB | | retrieval works |
| Processing | GPT-class model answers questions about any loan | | the LLM is accurate |
| Checks | the LLM checks completeness | | automation works |
| Human in the loop | not needed after week 2 | | |
| Output / system of record | the chatbot writes approvals to the core system | | end to end |
| Measurement | user satisfaction survey | | adoption |

**Scope of the skeleton (one product, one site, one path):** all products, all branches, in week 2.

**What the skeleton must prove by the end of week 3:** that the chatbot can approve loans.

**Failure modes I expect, and what each would change:** hallucination, mitigated by RAG.
