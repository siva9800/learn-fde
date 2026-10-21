# 11 · Build It with AI, and How You Know It Is Right

> Day 19 · Section 11 of 15 · [Chapter overview](README.md) · Previous: [10 · Project](10-project-the-godavari-observability-layer.md) · Next: [12 · Mistakes and debugging](12-mistakes-and-debugging.md)

---

## 11.1 The context to give the agent

A coding agent writes instrumentation quickly and well, once it knows what must not be in it. Give it, in this order:

1. **The stages and their owners**: paths to Day 11's `pipeline.py`, `ruleset.py` and `core_write.py`, Day 12's
   `ledger.py` and `client.py`, Day 18's `pilot.py` and `corrections.py`, and the instruction that none of them may be
   edited, only wrapped.
2. **The list of what is never logged** (section 07.1), verbatim, with the sentence "no attribute may accept free text".
3. **Day 12's ledger row as the only source of rupees**, and the price card it already applies.
4. **The OpenTelemetry gen-AI attribute names you want**, pasted from the conventions with the date, and the note that
   `gen_ai.usage.input_tokens` includes cached tokens.
5. **The three readers and their decisions** (section 08.1), so it does not build one dashboard for everyone.
6. **The constraints of the customer's environment**: no internet on the pilot machine, so no CDN, no external fonts,
   no telemetry SaaS.

## 11.2 A strong prompt

```text
You are adding observability to an existing loan-file pipeline. Do not edit any file under 11-*, 12-*, 13-*, 14-*,
15-*, 16-* or 18-*. Import them by path (see 18-verification-and-trust/code/godavari_review/paths.py for the pattern).

Build code/godavari_obs/ with:
- spans.py: a Span (trace_id 32 hex, span_id 16 hex, parent, name, kind, start, end, status, attrs, events) and a
  Tracer with deterministic ids from (run, file id). Times are IST, timezone-aware.
- redact.py: an allowlist SCHEMA mapping every attribute key to a validator (enum, regex for ids, bounded number). No
  key accepts free text. Unknown keys and invalid values are dropped and counted by key and reason, never by value.
  Then scan what is left for PAN, Verhoeff-valid 12-digit numbers, mobiles and e-mails, bounded so hex ids do not match;
  any hit quarantines the span. Span names come from a fixed list.
- store.py: SQLite; write() goes through redact.admit() and is the only way in.
- instrument.py: one model-call span per Day 12 LedgerRow (rupees from the row, not recomputed; input_tokens =
  input + cache_read + cache_write); wrappers for Day 11's ExtractionModel and RuleSet that return exactly what the
  inner object returns and record rule ids and counts, never finding messages.
Write pytest tests first for: rupees in traces equal the ledger; wrappers change no route, finding or note; a span
with a PAN in a free-text key stores nothing identifying; a loosened validator is caught by the scanner.
Show me the tests before the implementation.
```

## 11.3 What the agent gets right

The span and tracer classes, the SQLite schema, the roll-up arithmetic, the HTML table markup and the test scaffolding
are routine for it and usually correct first time. It is also good at turning a ledger row into a span once told to,
and at writing the SVG for a dot plot when given the layout.

## 11.4 The mistakes it makes for this concept

These are the ones to expect. Most are collected in the exercise file, `code/exercises/ai_draft_tracing.py`; the last
two happened while this chapter's own project was being built, and the run report caught both:

| Mistake | Why it matters at Godavari |
|---|---|
| records the prompt and the page text "for debugging" (`gen_ai.input.messages`) | the prompt is a customer's documents; the conventions make it opt-in for this reason |
| records the model's answer (`gen_ai.output.messages`) | it carries the PAN and the names it extracted |
| logs Day 11's finding messages with the rule id | "PAN card says ..., the form says ..." quotes both PANs |
| puts the file number in the span name | unbounded names; the day an id is a PAN, it is in every index |
| copies Day 12's `input_tokens` straight across | under-reports input on every cached call; the convention counts cached tokens in |
| recomputes cost from tokens and one price | two rupee numbers that disagree; ignores tiers, cache pricing and the residency uplift |
| records only the final attempt | retries, escalations and repairs, the expensive part, vanish |
| head-samples one trace in ten | GF-61070 would have been dropped with 90 percent probability |
| alerts on the monthly average | would not have fired in week two (mean Rs 5.94) |
| pages on-call for a cost alert at 02:00 | trains people to ignore pages |
| redacts with a nightly scrub job | the raw lines are already in buffers and backups |
| puts `str(exc)` in the span status | exception messages quote the values that failed validation |
| copies Day 18's correction event with both values | the golden set needs values; the trace store must not have them |
| mixes `datetime.now()` and `datetime.utcnow()` | a review that ends before it starts |
| loads a charting library from a CDN, no escaping | the pilot machine has no internet; an analyst's note becomes markup |
| metrics labelled by file id or analyst name | unbounded series; per-person numbers outside Day 18's agreement |
| identifier scanners with digit-only boundaries | the first run "found" Aadhaar numbers and mobiles inside hex hashes in Day 16's journal and Day 17's audit log |
| two definitions of "median" in one report | the spike alert said Rs 10.66 and the roll-up table said Rs 10.56 for the same night |

## 11.5 How you know it is right

Checks that do not depend on who wrote the code, each a test in `code/tests/`:

1. **Completeness.** Arrivals equal file traces equal distinct file numbers; every trace has every stage and every
   parent exists.
2. **Money.** Trace rupees equal ledger rupees to the paisa; stage totals sum to the same number.
3. **No behaviour change.** The same files with and without wrappers give identical routes, findings and notes; week
   one's screen log is identical, event for event, to Day 18's.
4. **Leaks, tested with real values.** Every PAN, Aadhaar number, mobile and name printed in the pilot's files is
   searched for in the store, the export, the alerts, the report and the dashboards. Names have no pattern, so a
   detector check alone proves nothing about them.
5. **The boundary's own tests.** A hostile span stores and counts nothing identifying; a loosened validator is caught.
6. **Alerts on the right nights**, and none paging; **pages that load nothing** and escape a hostile string; and
   **determinism**: the committed pages are byte for byte the ones the code writes.

## 11.6 Review checklist

- [ ] No file in Days 11 to 18 changed; every import is by path
- [ ] Every attribute key is on the allowlist with a validator; none accepts free text
- [ ] No finding message, prompt, answer, page text, query text or staff name on any span
- [ ] Span names from a fixed list; ids in attributes, not names or metric labels
- [ ] Rupees from the ledger only; estimates shown separately; input tokens include cached tokens
- [ ] Every attempt is a span, errors with `error.type`
- [ ] Prompt release, model, rules fingerprint and bands version on every trace
- [ ] Ceiling per file, not on the average; every alert has an owner, a threshold from a decision, and evidence
- [ ] Three pages, one per decision; static, escaped, no external resource
- [ ] Leak test searches for the actual identifiers in the files, not only patterns
- [ ] Corrections reach the store as reason, band and field, never as values
