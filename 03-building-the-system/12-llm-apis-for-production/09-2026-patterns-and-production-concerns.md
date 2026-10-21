# 09 · 2026 Patterns and Production Concerns

> Day 12 · Section 9 of 14 · [Chapter overview](README.md) · Previous: [08 · Caching, batch APIs and model choice](08-caching-batch-and-model-choice.md) · Next: [10 · Project: the Godavari client](10-project-the-godavari-client.md)

---

## 9.1 What practitioners use in October 2026

| Pattern | What it is | Where it lands in this course |
|---|---|---|
| structured outputs by default | every major API constrains output to a schema; free-text JSON parsing is legacy | section 03; the contract here |
| reasoning effort as a dial | current models think before answering, and an effort setting trades depth for tokens (Anthropic's `output_config.effort`; thinking tokens are billed as output) | section 07: output is 70 percent of a page's cost; set effort per route |
| refusal handling as a first-class path | a refusal is a 200 with a stop reason; some providers offer server-side fallbacks to another model | the repair ladder returns `None` on refusal; the page goes to a person |
| a model gateway in front of every call | one internal endpoint that holds keys, enforces allowlists, logs, and routes to providers | Day 25 owns it; this chapter's client is the code-side half |
| OpenTelemetry generative-AI conventions | standard span attributes for model, tokens and latency, so traces land in the customer's existing backend | Day 19 turns the ledger row into a span |

## 9.2 What is hype

- **"A million-token context means send the whole bundle in one call."** Anthropic prices its 1M
  context at the standard rate on current models (October 2026), so it is affordable. It is still worse
  engineering for intake: one failure redoes forty pages, one truncation loses the co-applicant on page
  38 (Day 13's trap), and per-page evidence checks need per-page answers.
- **"The agent framework handles retries."** Frameworks run loops. They do not know which of your
  errors are safe to repeat, what your budget is, or that a timeout was billed. Keep the client.
- **"Temperature zero makes it deterministic, so cache by file number."** Several current models no
  longer accept sampling parameters at all (Anthropic's documentation lists non-default `temperature` as
  a 400 on some current models), and determinism was never the condition for safe caching; identical
  inputs were.
- **"Structured outputs solved hallucination."** They solved parsing. Section 3.5's wrong-line answer
  is schema-valid, grounded and wrong.

## 9.3 Production concerns

| Concern | What to do | Owner |
|---|---|---|
| **API keys** | never in code or `.env` files in the repo; from the customer's secrets manager or KMS; one key per environment; rotate | Day 25 |
| **PII in logs** | the ledger holds keys and numbers only; prompts and answers are logged, if at all, through a redacting boundary with agreed retention | Day 19, with the compliance head |
| **Residency of the response store** | it holds model answers about customer documents: same boundary, same retention as the documents | Day 24 |
| **Model versions** | pin exact model IDs in the adapter; a vendor deprecation is a scheduled change with an eval run, not a surprise | Days 13, 14 |
| **Schema and prompt versions** | both in every idempotency key and every ledger row | Day 13 |
| **Spend limits** | set a workspace or project limit below the provider's cap; alert on Rs per file, not only per month | Day 19 |
| **Capacity** | size the concurrency pool from the provider's RPM and token-per-minute limits; ramp gradually after a launch to avoid acceleration limits; request higher tiers before the Hyderabad wave (6 January 2027), not on the day | Day 27 |
| **Monitoring** | per night: 429 rate, timeout rate, breaker transitions, store-hit rate, cache-read share, Rs per file p95, s per file p95, wrong-but-valid catches | Day 19 |
| **Untrusted input** | a scanned page can contain text that reads like an instruction; the model's answer is data checked by code, never an instruction to the system | Day 41 |

## 9.4 The failure the customer notices first

Not an outage: the breaker turns that into a later finish. It is a confident wrong value that passed
every check, in front of a branch manager. Every pattern here shrinks that set; none empties it. Hence
evidence and a page on every field, withholding rather than guessing, and Day 18's crop beside the field.
