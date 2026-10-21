# 11 · Common Mistakes and Debugging

> Day 12 · Section 11 of 14 · [Chapter overview](README.md) · Previous: [10 · Project: the Godavari client](10-project-the-godavari-client.md) · Next: [12 · Interview questions](12-interview-questions.md)

---

Each row is **symptom, cause, fix**, with the section that explains it.

## 11.1 Shape and content

| Symptom | Likely cause | Fix |
|---|---|---|
| `json.JSONDecodeError` at random pages | JSON asked for in the prompt, no constrained decoding; or a truncated response | structured outputs; check `stop_reason` before parsing; strip wrappers only (3.4) |
| 400 "schema" error on the first call of the night | an unsupported keyword (`minimum`, `maxLength`) or `additionalProperties` missing | `provider_schema()`: move limits to descriptions, validate them locally (3.3) |
| amounts parse but are ten times too large | valid shape, wrong content | value must match its evidence; re-ask once, then withhold (3.5) |
| "requested amount" equals the dealer's ex-showroom price | the wrong line on the right page; no cheap check catches it | Day 14 measures it per field; Day 18 shows the crop; do not "fix" it by taking the largest amount (3.5) |

## 11.2 Retries, rate limits and time

| Symptom | Likely cause | Fix |
|---|---|---|
| attempts in the provider's console are three times the ledger's | the SDK's default retries under your own | `max_retries=0` in the adapter (6.7) |
| bursts of 429s at the same second, again and again | retries without jitter, or `retry-after` ignored | full jitter, `retry-after` as a floor (6.2) |
| 429s that never clear, no `retry-after` | a monthly spend cap, not a rate limit | not retryable; alert a person (6.1) |
| a nightly run that hangs for ten minutes on one page | the SDK default timeout | per-stage timeouts from the budget (2.4, 6.3) |
| the night finishes at 05:40 after a short outage | every page retried into the outage | circuit breaker; defer and re-queue (6.6) |

## 11.3 Cost

| Symptom | Likely cause | Fix |
|---|---|---|
| the bill doubled and nothing changed in the code | the job ran twice, or a re-run used fresh keys | content-built idempotency keys; check the store-hit count (6.4) |
| `cache_read` tokens are zero every night | a timestamp, a UUID or unsorted JSON in the system prompt | stable prefix first, variable text last (8.2) |
| the ledger is lower than the invoice | billed timeouts, abandoned streams | estimated rows; reconcile weekly (6.4) |
| escalations are most of the classification bill | the escalation threshold | measure the threshold's cost and accuracy on the golden set (7.8) |
| a file costs four times the median | many retries and re-asks on one bundle | its ledger rows by stage and purpose; often a bad scan (10.5) |

## 11.4 A debugging routine for "the night went wrong"

1. **Outcome counts first.** Count ledger rows by outcome and by hour (`ledger.outcomes()` gives the totals). A wall of `overloaded` is the provider; a wall
   of `rate_limited` is your concurrency; `bad_request` is your request.
2. **Breaker transitions.** If it never opened during an outage, its threshold counts the wrong errors.
3. **Store hits.** A re-run with zero store hits means the key changed: diff the key inputs (page hash,
   prompt version, schema version, model).
4. **Cost by stage and purpose.** `repair` and `bigger_budget` rows growing means a prompt or schema
   regression, not traffic.
5. **One file end to end.** Pick the worst file in `night-per-file.csv` and read every ledger row for it
   in time order. The story is always there.
