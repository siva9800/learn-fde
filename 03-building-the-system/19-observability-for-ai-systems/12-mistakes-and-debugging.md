# 12 · Mistakes and Debugging

> Day 19 · Section 12 of 15 · [Chapter overview](README.md) · Previous: [11 · Build it with AI](11-build-with-ai-and-verification.md) · Next: [13 · Interview questions](13-interview-questions.md)

---

## 12.1 Symptom, cause, fix

| Symptom | Cause | Fix |
|---|---|---|
| the dashboard's monthly cost is under the provider's invoice | timed-out calls were billed by the provider but recorded as estimates, or not at all | show the ledger's estimate beside the cost; reconcile against the invoice monthly (Day 12, section 06) |
| cost per file looks fine, the bill does not | the alert is on the average; one branch or one night is expensive | alert per file against the ceiling and per branch per night against its own baseline (04.3) |
| traces show one model call per page, the ledger shows more | the wrapper records only the final attempt | one span per ledger row, retries and repairs included (03.4) |
| input tokens on the dashboard are lower than the provider's | Day 12's `input_tokens` is uncached input; the convention counts cached tokens in | add cache read and cache write into `gen_ai.usage.input_tokens` (03.3) |
| a file the COO asked about has no trace | head sampling dropped it | do not sample at this volume; if you must, sample by outcome after the trace completes (03.5) |
| a review span ends before it starts | naive local time mixed with UTC | timezone-aware IST everywhere, the offset in every timestamp (09.3) |
| a rule's fire rate jumped and everyone blames the model | nobody split it by channel, branch or release | read the traces by the root span's attributes before concluding (05.5) |
| correction rates fell and everyone celebrated | analysts stopped looking | read corrections with dwell, the forced-look seconds and the spot checks (05.2) |
| the scanner flags hashes as Aadhaar numbers | digit-only boundaries | bound the patterns on letters, digits and the decimal point; tune on your own data (07.3) |
| the trace store holds a customer's name | a free-text attribute (a note, a message, an exception) | no key accepts free text; exceptions recorded as `error.type` from a list (07.3) |
| the team lead sees per-analyst numbers the analysts were never told about | the agreement was not written onto the page | repeat Day 18's terms under the table; route per-person signals to the analyst's own lead only (08.3) |
| on-call ignores pages | cost and drift alerts page at night | three page rules; everything else in the 08:30 digest (08.4) |
| the gate passed a change that broke production | the golden set does not contain the new shape | production signals add candidates to Day 14's development split (05.7) |

## 12.2 A routine for "the number looks wrong"

1. **Find the unit.** Which file, branch, night or release? Start from the alert's trace ids, never from the average.
2. **Open one trace.** Read it top to bottom: pages to the model, calls by stage, retries, the route, the review.
3. **Compare with a normal one.** A Kukatpally file the same night, or a Guntur file from week one. The difference is
   the hypothesis.
4. **Split by the root span's attributes.** Channel, branch, page count, release, filter. If the effect follows one of
   them, you have the cause's neighbourhood.
5. **Ask the person who knows.** The team lead knows what the branch changed; the application-support engineer knows
   what the core system did. The trace tells you where to look and they tell you why.
6. **Fix, then add the line.** The fix stops this incident; the new dashboard line (pages per file, here) stops the
   next one being a surprise.

> **Telugu callback for the video.** "Number thappuga undi ante average chudakandi. Okka trace open cheyandi, normal
> trace pakkana pettandi."
