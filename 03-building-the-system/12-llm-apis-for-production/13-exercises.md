# 13 · Exercises

> Day 12 · Section 13 of 14 · [Chapter overview](README.md) · Previous: [12 · Interview questions](12-interview-questions.md) · Next: [14 · Further reading](14-further-reading.md)

---

Eight exercises in three levels. Solutions are folded under each one. Exercises marked **(tested)** use the
chapter's code, run on Python 3.14.3 with the pinned versions on 21 October 2026; the outputs shown are
real. Learning mode: write the code and the reasoning yourself; use an AI assistant as a tutor or a
sceptical reviewer, not as the author. Try first, then open.

## Level 1: warm-up

**1.1 Retry or not?** For each, say retry (with what wait) or not, and whether it should count against
the circuit breaker: (a) 429 with `retry-after: 7`; (b) 429 whose body says
`enforced_spend_limit_reached`; (c) 529 overloaded; (d) 400 "Schema is too complex for compilation";
(e) our 30-second timeout; (f) a 200 with `stop_reason: "refusal"`; (g) a 200 whose amount does not match
its evidence.

<details><summary>Solution</summary>

(a) retry after at least 7 s; not the breaker. (b) no: a monthly cap; alert a person; not the breaker.
(c) retry with jittered backoff; counts. (d) no: fix the schema (simplify it, or split it); not the
breaker. (e) retry inside the deadline, and remember it may have been billed; counts. (f) no: route the
page to a person. (g) no blind retry: one re-ask naming the failed check, then withhold. (Sections 6.1,
3.5.)

</details>

**1.2 Predict the output (tested).** What does `lenient_json` return for each input?

```python
'{"a": 1}'
'Sure! {"a": 1} Hope this helps.'
'```json\n{"a": [1, 2]}\n```'
'{"a": 1'
'{"a": 1} {"b": 2}'
```

<details><summary>Solution</summary>

```text
'{"a": 1}' -> ({'a': 1}, 'clean')
'Sure! {"a": 1} Hope this helps.' -> ({'a': 1}, 'wrapper_stripped')
'```json\n{"a": [1, 2]}\n```' -> ({'a': [1, 2]}, 'wrapper_stripped')
'{"a": 1' -> (None, 'invalid')
'{"a": 1} {"b": 2}' -> (None, 'invalid')
```

The last one surprises people: two objects are not one, and the function will not choose between them.
That is correct behaviour; a model that returns two objects has not followed the schema. (Section 3.4.)

</details>

## Level 2: build and measure

**2.1 Price a page by hand.** A classification on the small tier: 330 fresh prefix tokens (too short to
cache), 30 text, 450 thumbnail, 40 output, 1.10 uplift, Rs 95 per dollar. Then a classification
escalated to the large tier: same input, 40 output plus 220 thinking. What is the ratio?

<details><summary>Solution</summary>

Small: input 810 x 0.10 + output 40 x 0.50 = 81 + 20 = 101 micro-dollars, x 1.10 = 111, x 95 = about
Rs 0.011. Large: input 810 x 2.00 + output 260 x 10.00 = 1,620 + 2,600 = 4,220 micro-dollars, x 1.10 =
4,642, x 95 = about Rs 0.44. Forty times more, and 62 percent of it is thinking-plus-output. That is why
65 escalations cost more than 1,282 small classifications in the night (section 7.8).

</details>

**2.2 Size the pool (tested).** Change `CONCURRENCY` in `code/run_nightly_batch.py` to 4, then to 48, and
predict, before running, what happens to 429s, the 40-page p95 and the batch end time.

<details><summary>Solution</summary>

```text
== CONCURRENCY 4
  attempt outcomes: circuit_open 3062, ok 1835, overloaded 7, server_error 16, store_hit 81, timeout 11
  whole file p50 28.8, p95 49.9; 36-40 page files p95 40.5 (n=5, budget 120): PASS
  batch: 02:00:00 to 02:24:17, deadline 08:00:00, slack 5.6 h
== CONCURRENCY 48
  attempt outcomes: ok 1836, rate_limited 214, server_error 15, store_hit 56, timeout 11
  36-40 page files max 11.17
  whole file p50 19.6, p95 48.2; 36-40 page files p95 49.7 (n=5, budget 120): PASS
  batch: 02:00:00 to 02:03:09, deadline 08:00:00, slack 5.9 h
```

At 4, no 429s, but the night stretches past the outage, so far more calls hit the open breaker. At 48,
the night finishes before the outage starts, but 429s jump from 40 to 214, the 40-page p95 gets worse
(more waiting on `retry-after`), and the worst file's cost rises to Rs 11.17 because retries and re-asks
pile up. More concurrency past the provider's limits buys nothing. (Section 6.5.)

</details>

**2.3 Move the escalation threshold (tested).** Set `ESCALATE_BELOW = 0.70` in `extractor.py` and rerun.
What changed in cost, and what can you conclude about accuracy?

<details><summary>Solution</summary>

```text
  structured output: content_check_failed 15, content_fixed_on_reask 13, content_withheld 2, escalated_to_large 87, refusal 6, truncated 10
file-level fields vs synthetic truth: correct 299, withheld for review 0, wrong and accepted 1
cost per file, model calls (Rs): p50 6.40, p95 8.41, max 12.09 (KKP-26-00049, 37 pages); 36-40 page files max 12.09
  by stage (Rs): classify 12.18, escalate 69.89, extract 302.53, repair 12.37
```

Escalations rose from 65 to 87 and their cost from Rs 51.87 to Rs 69.89, and one file now breaks the
Rs 12 ceiling. You can conclude almost nothing about accuracy: changing one threshold changed the random
path of the whole night, so the field line is not a paired comparison. That is the argument for Day 14:
the same golden files, scored under both settings.

</details>

**2.4 Break it, then fix it (tested).** In `retry.py`, replace the body of `backoff_delay` with
`return policy.base_delay_s * 2 ** (attempt - 1)`. Run the tests. Which fail, and what production
failure does each one stand for? Then restore it.

<details><summary>Solution</summary>

```text
FAILED tests/test_retry.py::test_backoff_is_full_jitter_under_a_growing_cap
FAILED tests/test_retry.py::test_retry_after_is_a_floor - assert False
FAILED tests/test_retry.py::test_429_then_success_is_one_logical_call - asser...
3 failed, 33 passed in 0.12s
```

The first is the thundering herd: every draw identical, so workers that failed together retry together.
The second and third are the ignored `retry-after`: a fixed 1 s wait against a server that said 7 (or
3), so the retry is guaranteed to be refused again. The other 33 pass, which is the lesson: one bad line
in the right place, and only the tests written for it notice.

</details>

## Level 3: judgement

**3.1 Review this AI-written client.** `worksheet/ai-draft-client.py` was written by a coding agent from
the prompt at its top. It looks finished. Find at least twelve problems, and for each say what it would
cost Godavari.

<details><summary>Solution</summary>

1. `anthropic.Anthropic()` keeps the SDK's two default retries under a loop of five: up to 15 attempts, none logged.
2. No timeout: the SDK default is 10 minutes; one hung page stalls the night.
3. `except Exception` retries 400s five times, paying for nothing.
4. `time.sleep(2 ** attempt)`: no jitter, ignores `retry-after`, sleeps after the last attempt.
5. The "idempotency key" is a fresh UUID and is never used: every re-run pays again.
6. `temperature=0`: some current models reject non-default sampling with a 400 (Anthropic, October 2026), and determinism was never the condition for caching.
7. The current time in the system prompt: prompt caching never hits.
8. `output_format=` is the deprecated parameter (now `output_config.format`); a schema with defaults and no `additionalProperties: false` is not strict.
9. `response.content[0].text` assumes the first block is text and never checks `stop_reason`.
10. Appending `"}` to truncated JSON invents content.
11. Cost from `max_tokens` and characters at one undated price: no usage, no cache, no image tokens, no uplift, no rupees, no per-file sum.
12. Prompts and responses logged at INFO: names and PANs in the logs.
13. A validation failure returns `LoanFields()` (amount 0) as if read; `extra="ignore"` hides drift.
14. Pages called one by one, every page extracted: latency and cost.
15. "The largest amount is the request" is the wrong-line trap exactly.
16. `APPROVED_FOR_CORE` decided by model output, with no rules and no analyst (Days 11, 17).
17. Three blind re-asks with the identical request, results discarded.
18. A model name hard-coded at the call site.

</details>

**3.2 The CFO's question.** The CFO sees "about Rs 8,900 a month" for model calls and asks why the cloud
line in the business case is 26 lakh a year. Write the three-sentence answer.

<details><summary>Solution</summary>

"Model calls are about 1.1 lakh of the 26 lakh, measured on a simulated night at today's list prices;
the rest is the compute, storage, logging and private network that run in your AWS account whether or
not a model is called (Day 21 sizes it). We set a ceiling of Rs 12 per file for model calls and alert on
any file above it, so the part that can change overnight is watched every night. The number to watch for
the case is not this one; it is field accuracy on the golden set, because that sets the hours saved
(Day 9)."

</details>
