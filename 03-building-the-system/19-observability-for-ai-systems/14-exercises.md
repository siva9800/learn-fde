# 14 · Exercises

> Day 19 · Section 14 of 15 · [Chapter overview](README.md) · Previous: [13 · Interview questions](13-interview-questions.md) · Next: [15 · Further reading](15-further-reading.md)

---

Learning mode: write the code yourself and use an AI assistant as a tutor ("why does this test fail?"), not as the
author. Run everything in the chapter's virtual environment (section 10.2).

## Level 1 · Warm-up

**1.1 Five questions for a system you know.** For a system you have worked on, write the five morning questions
(section 02) as a table: the evidence that answers each, whether it is exact or a proxy, and who reads it. Mark the
two that are hardest and say why in one sentence each.

**1.2 Predict the output.** Day 12's ledger has three rows for one page of one file: attempt 1 `rate_limited` (0
tokens), attempt 2 `ok` (2,400 input, 1,378 cache read, 0 cache write, 370 output, Rs 0.74), and a later `store_hit` (0
tokens, Rs 0). Before running anything, write down: how many model-call spans `model_call_spans` creates; how many have
status `error` and with what `error.type`; the `gen_ai.usage.input_tokens` on the second span; the rupees the file's
root span adds up. Then check against `instrument.py`.

**1.3 Read a trace.** Load `data/sample-trace-GF-61070.jsonl` with ten lines of Python. Count the model calls whose
`kaagaz.llm.page` is 38 or higher (the appended statement pages), their rupees, and the slowest single call. Compare
with section 3 of `data/run-report.md`.

## Level 2 · Core

**2.1 Break it, then fix it: the token convention.** In `model_call_spans`, set `gen_ai.usage.input_tokens` to
`r.input_tokens` only. Run the tests. Which test fails, and what would a dashboard built on the broken spans have
shown for cached calls? Restore the line.

**2.2 Break it: a "helpful" attribute.** In `route_span`, add `"kaagaz.route.messages": [f.message for f in
result.findings]`, the finding messages an engineer might want "for context". Run the project. Where does the boundary
report it, and does anything reach the store? Now add the key to `SCHEMA` with `lambda v: isinstance(v, list)`. Run
the tests again. In week two, 8 messages carry a PAN the scanner recognises (ENV-PAN-MATCH), 3 carry a misread PAN
that by definition does not fit the PAN pattern (ENV-PAN-FORMAT), and 4 carry the applicant's name (ENV-NAME-MATCH).
Predict which tests fail before you look: one because the scanner quarantines spans, others because it cannot see what
leaked. Explain why the second kind of failure is the one that matters most. Revert both changes.

**2.3 A pages alert.** Add a `pages` alert: a branch's median pages per file on a night more than 1.5 times its
week-one median. Route it to the digest. Show that it fires on Tuesday 15 December for Guntur, and argue in two
sentences why it is a better early warning than the cost spike.

**2.4 "This did not help".** Add a feedback event for the policy panel: a `retrieval_feedback` event on the retrieval
span with one coded reason from a short list you define. Add the keys to `SCHEMA`, add the event name to
`EVENT_NAMES`, simulate three clicks on Thursday, and write a test that a free-text comment on the event is dropped.

## Level 3 · Challenge

**3.1 Review this AI-written work and find what is wrong.** Read `code/exercises/ai_draft_tracing.py`. It was produced
from the prompt "instrument the pipeline with OpenTelemetry-style tracing, track token cost per file, capture analyst
feedback, and give me a dashboard". It runs. List every problem you can find, sorted into privacy, money and
operations, with the fix for each. There are at least fifteen. Then check the answer key below.

**3.2 Tail sampling.** Write `sample_by_outcome(store, share, seed)` that keeps every trace with an error span, every
file over the ceiling, every file with a content correction, and a random `share` of the rest. With `share=0.1`, report
how many of the 120 file traces it keeps, confirm GF-61070 is among them, and compare with what head sampling at 10
percent would have kept, over 1,000 seeds.

**3.3 The COO's paragraph for week three.** Write the "this week in one paragraph" box for Friday 25 December (the
freeze week): cost back to week one, no incident, the policy-panel sync fixed, and still no decided pilot files.
Under 90 words, every number with a source, and one honest sentence on what is not known.

## Answer key for 3.1

| # | Problem | Kind | Fix |
|---|---|---|---|
| 1 | random head sampling at 10 percent, decided before the work | operations | keep everything at this volume; sample by outcome after completion |
| 2 | span name `extract {file_id}` | operations, privacy | fixed span names; the id as an attribute |
| 3 | `gen_ai.input.messages` with the prompt and every page's text | privacy | never record content; the convention makes it opt-in |
| 4 | `gen_ai.output.messages` with the model's answer | privacy | as above |
| 5 | `str(exc)` in the status and a debug log of it | privacy | `error.type` from a fixed list |
| 6 | swallows the exception and returns `{}`, so the pipeline continues with nothing | operations | let the stage's own error handling decide; tracing must not change behaviour |
| 7 | input tokens "uncached only" | money | include cached tokens, per the convention |
| 8 | one price for every model and token type, in dollars, no uplift, recomputed | money | rupees from Day 12's ledger rows |
| 9 | only the final call recorded; retries invisible | money | one span per attempt |
| 10 | `METRICS` keyed by file id | operations | ids on spans, never metric keys |
| 11 | `datetime.now()` for start, `datetime.utcnow()` for end | operations | timezone-aware IST throughout |
| 12 | finding messages logged with the rule id | privacy | rule ids and counts only |
| 13 | feedback with the analyst's name and both values; a metric per analyst name | privacy | pseudonym; reason, band and field only; per-person signals to the team lead |
| 14 | a nightly regex scrub of PANs after writing | privacy | redact in the write path; allowlist first; the regex also misses names, Aadhaar and mobiles |
| 15 | budget check on the monthly average, a stale Rs 83 rate, and a page | money, operations | per-file ceiling from the ledger, digest not page, the trace id attached |
| 16 | dashboard with unescaped cells and a script from a CDN | privacy, operations | escape everything; static, self-contained, a CSP; the pilot machine has no internet |
| 17 | `logging.DEBUG` on, JSON to a shared logger | privacy | telemetry through the store's boundary, not the application log |
| 18 | no prompt version, model, rules fingerprint or trace link on anything | operations | the four versions on every trace; feedback on the review span |
