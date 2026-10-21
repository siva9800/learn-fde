# 10 · Project: The Godavari Extraction Client, One Night of the SFTP Drop

> Day 12 · Section 10 of 14 · [Chapter overview](README.md) · Previous: [09 · 2026 patterns and production concerns](09-2026-patterns-and-production-concerns.md) · Next: [11 · Mistakes and debugging](11-mistakes-and-debugging.md)

---

## 10.1 The brief

Before anyone at Godavari sees the extraction demo, the engagement folder needs three things from you:

1. **the extraction contract**: a typed, versioned schema for a loan file (applicant, co-applicant,
   product, requested amount, income evidence and the documents present, each field with a confidence
   and a page reference), in the form the provider receives and the form the pipeline reads;
2. **a client that makes the model a safe dependency**: provider-neutral, retried with backoff and
   jitter, idempotent per file page, budgeted and logged;
3. **a budget report** measured against a realistic night: rupees per file and p95 seconds per stage,
   with the wrong answers counted, before a single slide is made.

Everything runs offline. A fake provider stands in for the vendor and misbehaves the way vendors do,
from a seeded random generator on a virtual clock, so the whole night replays in under a second and
gives the same output every time.

## 10.2 Files

| Path | What it does |
|---|---|
| `godavari_llm/contract.py` | Pydantic models for page and file; `provider_schema()` for strict providers |
| `godavari_llm/provider.py` | the neutral boundary: request, response, usage, typed errors, the protocol, injected clocks |
| `godavari_llm/fake_provider.py` | the fake vendor: latency with a tail, a rate limiter with `retry-after`, an outage 02:04 to 02:07, 5xx, billed timeouts, truncation, refusals, wrappers in prompt mode, five wrong-but-valid answers, prompt caching |
| `godavari_llm/retry.py`, `client.py`, `ledger.py` | backoff and the breaker; `LLMClient` with the store, retries and the repair ladder; the dated price card and ledger |
| `godavari_llm/extractor.py` | `GodavariExtractor.read(bundle)` behind Day 11's seam: classify, escalate, extract, check, re-ask, merge |
| `godavari_llm/synthetic.py` | the synthetic night: 8 to 40 pages, tray order, Telugu labels, the ex-showroom price beside the requested amount |
| `godavari_llm/adapters/anthropic_adapter.py` | optional, not run: the protocol over the Anthropic Messages API |
| `run_nightly_batch.py`, `tests/` | the night and its report; 36 tests |

All paths are under `code/`.

## 10.3 Run it

Tested on Python 3.14.3, Windows 11, 21 October 2026, with the versions pinned in
`code/requirements.txt` (Pydantic 2.12.5, pytest 9.1.1). From the chapter folder:

```bash
python -m venv .venv && . .venv/Scripts/activate      # Linux/macOS: . .venv/bin/activate
pip install -r code/requirements.txt
python -X utf8 -m pytest code/tests -q                # 36 passed in about 0.15 s
python -X utf8 code/run_nightly_batch.py              # the night, about 0.6 s
python -X utf8 code/run_nightly_batch.py --files 20   # the twenty-file check before a demo
python -X utf8 code/run_nightly_batch.py --json-mode prompt   # without constrained decoding
python -X utf8 code/streaming_demo.py
python -X utf8 code/tool_loop_demo.py
```

`-X utf8` keeps Windows consoles happy with the Telugu labels. No API key and no network are needed.

## 10.4 The night, real output

```text
== Godavari nightly SFTP batch (simulated): 60 files, 1282 pages, provider 'fake', json mode 'schema' ==
price card (USD per million tokens, 21 Oct 2026): small 0.10 in / 0.50 out, large 2.00 / 10.00; residency uplift 1.10; Rs 95.00 per USD

calls: 1835 logical, 1909 attempts sent to the provider
  attempt outcomes: circuit_open 1448, ok 1835, overloaded 7, rate_limited 40, server_error 16, store_hit 3, timeout 11
  breaker: 02:04:01 open, 02:05:02 half_open, 02:05:02 open, 02:06:03 half_open, 02:06:03 open, 02:07:04 half_open, 02:07:05 closed; files deferred and re-queued: 23; passes over the queue: 4
  structured output: content_check_failed 13, content_fixed_on_reask 10, content_withheld 3, escalated_to_large 65, refusal 5, truncated 17

wrong-but-valid answers served by the fake model, and what happened to each:
  amount_x10                         stopped (re-asked, withheld or flagged): 1
  income_as_annual                   stopped (re-asked, withheld or flagged): 8
  pan_digit_misread                  stopped (re-asked, withheld or flagged): 5
  picked_the_wrong_amount_line       missed (wrong value accepted): 1
  swap_applicant_and_co_applicant    stopped (re-asked, withheld or flagged): 1
file-level fields vs synthetic truth: correct 294, withheld for review 5, wrong and accepted 1
files: 60 extracted, 11 need review, 0 not finished

cost per file, model calls (Rs): p50 6.34, p95 8.73, max 9.57 (WGL-26-00054, 39 pages); 36-40 page files max 9.57
  budget Rs 12.00 per file: PASS; night total Rs 381.89; per 1,400 files a month about Rs 8,911
  by stage (Rs): classify 12.25, escalate 51.87, extract 314.16, repair 10.05
  tokens: input 1,863,886, cache_read 564,980, cache_write 1,378, output 215,630
  ledger Rs 381.89 vs provider invoice Rs 389.16: Rs 7.27 billed for calls we timed out on (ledger estimate for those: Rs 6.44)

latency per file, processing only (s): classify p50 10.1 p95 14.0 (budget 20); extract p50 9.5 p95 38.0 (budget 90)
  whole file p50 20.7, p95 49.1; 36-40 page files p95 27.2 (n=5, budget 120): PASS
  batch: 02:00:00 to 02:10:07, deadline 08:00:00, slack 5.8 h

re-run of the same night: 0 provider calls, Rs 0.00 new spend (1838 store hits so far)
re-scan of page 33 of KMM-26-00001: 2 new model calls, 52 store hits, Rs 0.77

batch-API what-if: the same tokens at a 50% discount cost Rs 194.58 instead of Rs 389.16; worth it only with a synchronous fallback for anything unfinished by 06:30

wrote data/night-per-file.csv, data/page-extraction.provider-schema.json, data/loan-file-extraction.schema.json, data/sample-extraction.json (GNT-26-00005)
```

## 10.5 Reading it

| Block | What it shows | Explained in |
|---|---|---|
| calls | about 31 calls per file, so about 40,000 a month at 1,400 files; 74 extra attempts, almost all absorbed by one retry; 1,448 calls refused by the open breaker without being sent | 06 |
| breaker | open one second into the outage, a probe a minute, closed at 02:07:05; 23 files deferred, finished on later passes, completed calls not paid twice | 6.6 |
| structured output | shape failures rare with constrained decoding; content failures are the work: 13 failed a check, 10 fixed by a re-ask, 3 withheld | 3.4, 3.5 |
| wrong answers | 16 served, 15 stopped; the wrong-line answer accepted; 294 of 300 fields correct, 5 withheld, 1 wrong and accepted; 11 files to review with reasons | 3.5 |
| cost | median Rs 6.34, worst Rs 9.57, under Rs 12; extraction 82 percent; the ledger Rs 7.27 short of the invoice (billed timeouts) | 6.4, 07 |
| latency | every stage inside budget; 40-page p95 27.2 s | 7.7 |
| idempotency | the whole night again: Rs 0; one re-scanned page: its own two calls | 6.4 |

The fake provider's seed (7) was chosen from the first forty because its night shows all five
wrong-answer variants. Across all forty seeds (2,400 simulated files), the other four variants were
stopped every time (579 of 579) and the wrong-line answer was missed 53 times in 57. That consistency,
not the seed, is the result.

## 10.6 Build it with AI

An FDE in 2026 would have a coding agent draft most of this. The retry loop, the Pydantic models, the
ledger arithmetic and the fake provider are well within what agents write correctly. The value is in
what you give it and what you check.

**Context to give the agent:** the extraction contract fields from the Part file; Day 11's
`ExtractionModel` interface; the rule that no vendor SDK may be imported outside one adapter file; the
error table in section 6.1; the price card with its date and sources; the budgets (Rs 12 per file, p95
120 s for 36 to 40 pages, stage budgets); the constraint that nothing may call a real endpoint (synthetic
data only, the CISO's condition); and the instruction to write tests first for retry, validation and
cost.

**A strong prompt:**

> Build a provider-neutral Python client for page-level document extraction. Constraints: Python 3.12+,
> Pydantic 2.12, pytest; no vendor SDK imports except in `adapters/`. (1) A `ModelProvider` protocol with
> one method that makes exactly one attempt and raises our own error classes, each with `retryable` and
> `counts_against_health` flags; 429 carries `retry_after_s`; a spend-cap 429 is not retryable. (2) An
> `LLMClient.call` that checks a response store by idempotency key before calling, consults a circuit
> breaker, retries with full-jitter exponential backoff using retry-after as a floor, never starts an
> attempt that could not finish inside a per-call deadline, and writes one ledger row per attempt with
> four token counts. (3) `call_structured` that parses, strips only wrappers around the object, retries
> once with a doubled output budget on max_tokens, re-asks once with the validation error, and returns
> None otherwise; it must never patch content. (4) A fake provider, seeded, on an injected virtual clock,
> that simulates 429s, overload windows, billed timeouts, truncation and wrong-but-valid answers. Write
> the tests in `tests/` first, run them, and show me the failures before the implementation. Do not
> call any real API.

**What the agent typically gets right:** the shape of the retry loop; exponential backoff; Pydantic
models and validators; a clean protocol; a plausible fake; most of the tests.

**What it typically gets wrong for this concept (check each):**

| Mistake | How it shows | Fix |
|---|---|---|
| retries everything | `except Exception:` around the call; 400s and spend caps retried four times | the error table; a test per non-retryable class |
| backoff without jitter, or ignoring `retry-after` | `time.sleep(2 ** attempt)` | full jitter; `retry-after` as a floor; a test that draws 500 delays |
| leaves the SDK's own retries on | `anthropic.Anthropic()` with defaults inside a loop of five | `max_retries=0` in the adapter; count attempts in a test |
| idempotency key from a UUID or a timestamp | `request_id = f"{file_id}-{uuid4()}"` | key from content and versions; the re-run must cost zero |
| "repairs" truncated JSON by closing braces | `text + '"}'` | strip wrappers only; a test that truncated input stays invalid |
| stale API shapes | `output_format=`, `temperature=0` on a model that rejects it, `response.content[0].text` when the first block is thinking | read the vendor's current docs for the adapter only; keep shapes out of the rest of the code |
| cost from `max_tokens` or characters, one price for all tokens | `(1024 + len(text)) * PRICE` | usage from the response, four token types, dated card, uplift, rupees |

The two to watch hardest are the idempotency key and the content repair. Both produce code that passes a
happy-path demo and fails expensively in the second week: one by paying twice for every re-run, the
other by inventing a digit in a PAN.

## 10.7 How do you know it's right?

Whether you or an agent wrote it:

1. **Run the tests and read them.** 36 pass. Then read each assertion and ask whether it would fail on
   the bug it names. A retry test that never checks the attempt count proves nothing.
2. **Break it on purpose.** Change `backoff_delay` to return a constant: the jitter test must fail.
   Remove the `retry-after` floor: `test_retry_after_is_a_floor` must fail. Make `lenient_json` close a
   truncated brace: `test_truncated_json_is_not_patched` must fail.
3. **Re-run the night and diff the output.** Same seed, same text. A non-deterministic simulation cannot
   be reviewed.
4. **Re-run twice in one process.** Zero new calls and zero rupees. Anything else is a key problem.
5. **Reconcile cost two ways.** The ledger total against the fake provider's invoice; the difference
   must be explained by billed timeouts and nothing else. Recompute one page by hand (section 7.4).
6. **Count wrong answers, not just errors.** A report with no "wrong and accepted" line is hiding the
   most important number.
7. **Check the budget can fail.** Lower `COST_BUDGET_INR` to 8 and rerun: it must print FAIL. A check
   that cannot fail is decoration.
8. **Grep for vendor imports.** `grep -rn "import anthropic\|import openai\|from anthropic\|from openai" code`
   must hit only `adapters/`.
9. **Read one output end to end.** Open `data/sample-extraction.json`: every field has a page and
   evidence, the review reason is specific, and nothing in it decides the loan.

**Review checklist:**

- [ ] no vendor SDK outside `adapters/`; callers use tiers; model IDs pinned in one place
- [ ] errors typed; 400s, spend caps, refusals and wrong content never retried
- [ ] full jitter, `retry-after` floor, per-attempt timeout, per-call deadline, one retry layer
- [ ] idempotency key from content plus prompt, schema and model versions; store checked first; re-run costs zero
- [ ] circuit breaker on health failures only; deferred work re-queued, not dropped
- [ ] schema strict and versioned; wrappers stripped, content never patched; one re-ask with the error
- [ ] content checks: evidence on the page, value matches evidence, pages agree; failures re-asked once, then withheld
- [ ] ledger row per attempt with four token types; prices dated with sources; rupees per file; reconciled with the invoice
- [ ] budgets per file and per stage that can fail; twenty files measured before any demo
- [ ] no prompt, page text or answer in logs; the response store inside the customer's boundary

## 10.8 What goes into the engagement folder

| Artefact | Used by |
|---|---|
| `worksheet/godavari-llm-budget.md` | Day 19 (the dashboard's thresholds), Day 20 (the first slide), Day 29 (the readout) |
| `data/loan-file-extraction.schema.json` and `data/page-extraction.provider-schema.json` | Day 13 (prompts written against it), Day 14 (the golden set's label format), Day 18 (the review screen) |
| `data/night-per-file.csv` | Day 18 (what the review queue would have held), Day 19 (the cost-per-file baseline) |
| the client package | Day 16 (tools wrap the SOAP calls through it), Day 17 (agent turns go through it), Day 20 (the skeleton) |

## 10.9 Extend it

- Add a price-card row for gpt-5.6-terra (section 7.3) and rerun: what would the night cost on the
  India-geography route in section 8.5's table?
- Implement section 8.4's batch design against the fake provider, with the 06:30 fallback.
- Add a content check that catches the wrong-amount-line answer without failing a correct one (hint: the
  evidence's label), then list what it would miss on a real, messier form.
