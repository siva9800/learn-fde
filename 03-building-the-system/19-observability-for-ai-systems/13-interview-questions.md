# 13 · Interview Questions

> Day 19 · Section 13 of 15 · [Chapter overview](README.md) · Previous: [12 · Mistakes and debugging](12-mistakes-and-debugging.md) · Next: [14 · Exercises](14-exercises.md)

---

**1. What is different about observing an AI system compared with an ordinary web service?**
A wrong answer is a confident, well-formed value, so nothing errors; cost per unit of work varies with the input and
can double overnight; behaviour changes without a deploy (prompt, model snapshot, rules, thresholds); the inputs are
customers' documents, so logging them is a breach; and the best quality signal is the operators' corrections.

**2. A customer asks, "why did this file cost Rs 14?" How do you answer?**
Open the file's trace. The root span has pages and pages sent to the model; the model-call spans have tokens and
rupees per attempt, by stage. For GF-61070: 96 pages, 119 calls, 59 continuation pages that carried no field, Rs 5.99
of the Rs 14.00 spent on them. Then compare with a normal file and ask the branch what changed.

**3. Why put the prompt version, model, rules fingerprint and bands version on every trace?**
Each changes behaviour without a code deploy. Without them on the trace you cannot group cost or quality by release,
and you cannot prove which signed rules decided a file. The compliance head signs a fingerprint; the trace shows it.

**4. What does the OpenTelemetry gen-AI convention give you, and what are its caveats as of late 2026?**
Standard span and attribute names (`gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.prompt.version`) so
traces work in any backend. Caveats: Development status, a recent move to its own repository, names that still change,
input tokens that include cached tokens, and content capture that is opt-in and sensitive. Keep the names in one module.

**5. How do you measure quality in production without ground truth?**
With proxies, each compared with a baseline: corrections per field against the golden set's error rate, with
intervals; review-band corrections against the bands' expected share; spot checks, the only direct measure of
confident-wrong values; rule and envelope fire rates against last week; unsure rates. Read them together, and send
what production sees that the golden set lacks back to the development split.

**6. Correction rates fell by half. Good news?**
Not yet. Either the model improved or the analysts stopped looking. Check dwell time on the look-first field, burst
approvals and the spot checks. If dwell collapsed and spot checks start finding errors, it is rubber-stamping.

**7. Why not alert on the average cost per file?**
Because the average hides the unit. In Godavari's week two the mean was Rs 5.94 while one branch's files cost twice
their baseline for two nights and one file broke the Rs 12 ceiling. Alert per file against the ceiling and per branch
per night against its own baseline; put the average on the budget page.

**8. What must never be logged, and how do you enforce it?**
PAN, Aadhaar, mobiles, names, addresses, page text, prompts, answers, finding messages, free-text notes, query text.
Enforce with an allowlist of keys, each with a validator, none accepting free text; scanners as a second line that
quarantine a span; checks on key and span names; redaction in the write path, never a nightly scrub. Test with the
actual identifiers from the files, because names have no pattern.

**9. The review screen logs the model's value and the analyst's value. Is that a leak?**
No: the screen log is the decision record, inside the customer's boundary, with its own access and retention, and the
golden set needs the values. The leak would be copying those values into telemetry. The trace gets field, reason,
band and stratum.

**10. Who gets paged at a customer during a pilot?**
Only for what hurts the customer now and someone can fix now: the nightly job not finished before the queue opens, a
span quarantined at the logging boundary, the core system and the journal disagreeing. Cost and drift go into the
morning digest to the FDE; per-person signals to the analyst's own team lead; the COO gets a weekly page.

**11. Design three dashboards for one AI deployment.**
One per decision. The engineer's: completeness, cost per unit against the ceiling, latency by stage, errors, drift, the
boundary's counters. The operations lead's: queue, corrections per field against the golden set, overrides, spot
checks. The sponsor's: one number that moves the business case, the pre-registered metrics with honest "not yet", one
paragraph on the week.

**12. Should you sample traces?**
At about 1,400 files a month, no: storage is trivial and head sampling would have dropped the file that explained the
week. At high volume, sample by outcome after completion: keep every error, every cost outlier, every correction, and a
random share of the rest.

**13. The regression gate passed your fix. Is the fix safe?**
Only for the shapes the golden set contains. Godavari's page filter held back zero pages on all 200 golden files, so
the gate passed it without judging it. Ship with that stated, and add long-statement files to the development split.
