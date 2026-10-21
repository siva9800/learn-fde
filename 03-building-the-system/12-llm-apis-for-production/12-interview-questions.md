# 12 · Interview Questions

> Day 12 · Section 12 of 14 · [Chapter overview](README.md) · Previous: [11 · Mistakes and debugging](11-mistakes-and-debugging.md) · Next: [13 · Exercises](13-exercises.md)

---

Thirteen questions in the forms they take in the practical coding and enterprise system-design rounds
(Day 43). Answer out loud first, then compare.

**Q1. You are calling an LLM from a production pipeline. What do you put between your code and the vendor SDK?**

A thin client of my own. Callers send a request with a tier, not a model name; one adapter per vendor
translates it and maps vendor errors to my own typed errors; the client owns the idempotency check, a
circuit breaker, retries with jittered backoff inside a deadline, timeouts from the latency budget, and
a ledger row per attempt with token counts and cost. Nothing else imports the SDK, so a vendor or route
change is one file and one price-card row, then an eval run. (Section 02.)

**Q2. Which errors do you retry?**

The ones that go away and are safe to repeat: 429 after its `retry-after`, overload and 5xx, connection
drops and my own timeouts, all with backoff and a cap. Never a 400 or 413, never auth errors, never a
spend-cap 429 (it has no `retry-after` and will not clear), never a refusal, and never a valid response
with wrong content by repeating the same request. (Section 6.1.)

**Q3. Why jitter?**

Workers that fail together and wait the same time retry together and fail together. Full jitter draws
each wait uniformly below an exponentially growing cap, which spreads the retries and lets the provider
recover. A server's `retry-after` is a floor I never undercut. (Section 6.2.)

**Q4. A call timed out. Did it fail?**

Not necessarily. The provider may have finished and billed it. So my retry is a second billed request,
the ledger marks the timed-out attempt as an estimate, and I reconcile the ledger with the provider's
usage report. For a write to a system of record, a timeout is exactly when you need an idempotency key,
because the first write may have landed. (Section 6.4.)

**Q5. How do you make model calls idempotent?**

A key built from content: the file, the page number, the hash of the page bytes, the stage, the prompt
version, the schema version and the model. The client checks a response store before calling. A
retried call, a re-run of the nightly job and a duplicate upload all produce the same key and cost
nothing; a re-scanned page has new bytes, a new key and pays only for itself. A UUID or timestamp key
defeats the whole point. (Section 6.4.)

**Q6. What do structured outputs guarantee, and what not?**

The shape, through constrained decoding: types, required fields, enums, no extra keys. Not the content.
Documented exceptions remain: refusals, truncation at the output limit, enum capitalisation, unsupported
schema keywords that return 400. And a schema-valid answer can be confidently wrong. (Section 03.)

**Q7. The model returns valid JSON with the wrong value. What does your system do?**

Cheap, certain checks first: the quoted evidence must be on the page, the value must match its own
evidence, pages must agree, and Day 11's rules run in code. On a failure: re-ask once naming the
failed check, never a blind retry; if it still fails, withhold the field and route the file to review
with the reason; record it as a labelled example. And I am honest that some wrong answers pass every
check, which is why there is an eval set and a human approval. (Section 3.5.)

**Q8. How would you repair malformed JSON?**

Only by stripping what is around the object: a code fence, a sentence before or after. I never close a
truncated brace or fix a value, because that invents data. A truncated response is retried once with a
larger output budget; a schema failure is re-asked once with the error; then the page goes to a person.
(Section 3.4.)

**Q9. When would you use tool calling, and when not?**

When the model genuinely decides what to look up next, such as an analyst's open question that needs the
tracker and then the core record. Not to get JSON out (structured outputs), not for a rule (code), not
for a fixed sequence (a workflow in code), and never for an irreversible write without a state machine
and an approval gate. Tools are read-only by default, arguments are validated before running, errors
go back as results, and the loop has turn and tool-call budgets. (Section 04.)

**Q10. When does streaming matter?**

When a person reads the output as it arrives: an explanation on an operator's screen, an assistant's
answer. It changes when the first words appear, not total time or cost. For a nightly batch it buys
nothing and adds partial-response handling. If the first word is slow, a smaller tier or lower effort
helps more than streaming. (Section 05.)

**Q11. How do you set a cost budget for an AI feature?**

Per unit of work, from the business case down: Godavari's case gave about Rs 130 per file for all cloud;
model calls get a ceiling under a tenth of that, Rs 12, which every file must meet, not the average.
I measure it on a realistic sample before any demo, from a ledger with four token types and a dated
price card, and I make the check able to fail. (Section 07.)

**Q12. Where does the cost of a document extraction call actually go?**

Usually output. On the large tier, a page with 1,700 fresh input tokens, 1,380 cached and 820 output is
about 70 percent output by cost, thinking tokens included. So evidence length and reasoning effort matter
more than prompt length, and caching the stable prefix cuts its cost to a twentieth on that tier.
(Section 7.4.)

**Q13. You have a nightly batch with six hours of slack. Batch API?**

Probably, for half price, with two cautions. "Most within an hour" is not a deadline guarantee, so submit
early, poll, and at a cut-off time finish anything outstanding synchronously, using the same idempotency
keys so completed work is not paid twice. And check that the compliant route offers batch at all; some
cloud routes do not. (Section 8.4.)
