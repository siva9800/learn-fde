# 16 · Interview Questions

> Day 16 · Section 16 of 18 · [Chapter overview](README.md) · Previous: [15 · Mistakes and debugging](15-mistakes-and-debugging.md) · Next: [17 · Exercises](17-exercises.md)

---

These come up in the system-design round, the practical coding round and the client simulation. Answer
with the reasoning first, then the mechanism, then the Godavari example if you have one.

## Idempotency and writes

**1. A legacy API's create has no idempotency key. Your call times out. What do you do?**
Do not retry it. A read timeout means the request was sent and nobody knows whether it committed. Record
the write as unknown, wait longer than the system's own transaction timeout, then look it up by a natural
key (here file number and branch) and decide: found with my reference, it happened; found without, someone
else made it; only the shell, it did not happen and I can create; two, a person decides. A connect failure
is different: nothing was sent, so a retry is safe.

**2. Why is "look up before you create" not enough on its own?**
Because the lookup is only as good as the moment it runs. If the server commits after my client gave up,
an immediate retry's lookup sees nothing and creates a second record. In the chapter's run, lookup-then-
retry made zero duplicates when the reply was lost and two when the commit was late. The quiet period
closes that gap.

**3. Where do you keep the idempotency state if the server will not?**
In two places: my own journal (intent before the call, outcome after, no customer data), and the record
itself, by stamping my key in a spare field the owner agrees to, so the lookup can tell my records from
ones a person keyed and anyone can find what I created.

**4. How long should the quiet period be?**
Longer than the longest time the server could still be working on the request: its transaction timeout,
which you get from the owner. At Godavari it is 60 seconds, so 90. If you cannot get the number, resolve
unknowns in the next run, never in the run that made them.

**5. Which writes are naturally idempotent?**
Sets ("status is complete") are, in effect; creates and appends are not. Even a set can have side effects:
Godavari's core appends a history row on every status update, so a careful client reads the current value
and skips an identical write.

## SOAP and contracts

**6. You are given a WSDL. What do you look at first?**
The service address (often a dead development host), the binding style (document/literal is easy;
rpc/encoded is not), the operations I actually need, the mandatory fields and their order, and any
`xsd:import`. Then I ask the owner what the WSDL does not say: rate limits, windows, computed fields,
rules enforced in code rather than schema.

**7. zeep or a hand-built envelope?**
zeep when the WSDL loads: less code, and it checks types, order and `minOccurs` before sending. A hand-built
envelope when it will not, or for recording and debugging, because every element is visible. At Godavari
both exist and the contract tests require them to read every recorded exchange identically.

**8. How do you test against a sandbox that is three months stale and shared with the owner?**
Record it once into a scrubbed cassette and replay it on every build: parse every response with both
clients, compare every request's shape element by element, and diff the served WSDL against a pinned
contract. Known differences from production go in a list with an owner, a test and an expiry date. The
sandbox itself is touched only by the recorder and by the logged calls the owner is watching.

**9. What does the sandbox not tell you?**
Anything newer than its last refresh. Godavari's production rejects two-wheeler applications without a
dealer code since August; the July sandbox accepts them, and the WSDL marks the field optional in both.
Only the owner, or a release note, tells you that. That is why the mapping is reviewed by him.

## Data

**10. What is the metadata translation layer, and why is it underrated?**
A maintained, versioned description of the customer's fields and codes in business language, mapped to
your canonical schema, with an owner and tests. It is how a model sees "applicant is salaried" instead of
`CUST_FLG_3`, how your code refuses an unknown code instead of guessing, and how the next engineer
understands the system. OpenAI's FDE team calls it underrated because it is where customer knowledge
becomes a reusable asset, much like a semantic layer in business intelligence.

**11. Why should an integration never write to the customer's production database directly?**
Because it bypasses everything the system does on the way in: validation, sequences, triggers, the audit
trail, the batch's assumptions. Writes go through the system's API, where the owner can see them. And a
reporting replica must not be written at all; it is a copy.

**12. The customer's data may not be copied. How do you build anything?**
Read it in place, on demand, for one record, for a named person and a stated purpose; cache it in memory
briefly; log every view; keep masked forms and hashes everywhere else; deny identifier columns at the
database, not in your code; keep any index inside their environment. Then prove it with a test that scans
your logs, journals and reports for the identifiers.

**13. You must read an Excel tracker that forty people maintain. What could go wrong?**
Headers on different rows and spelled differently, columns inserted, dates as text in two orders and as
serial numbers, colours that carry meaning, hidden and total rows, formulas with no cached values,
duplicates, typos, two people claiming one row. Find headers by scoring, map through aliases the owners
maintain, parse every cell into a value and a problem, send the unreadable to a person, and never migrate
columns like the customer's name.

## On the job

**14. How do you earn the right to write to a core whose owner has watched three vendors fail?**
Show, do not send designs. Write to the sandbox in week one with a key and a lookup, log every call, and
bring the log. Then a reconciliation every morning built from his system and his access log, written for
him, with every exception a record number and a section on what it could not check. At Godavari his
condition is a month of that before live writes on 8 December.

**15. Integration is late in your plan. What went wrong, and what do you do now?**
Usually it was scheduled as plumbing after the model work, so its unknowns (the sandbox, the account, the
undocumented rules, the owner's trust) surfaced last. Now: get the owner and the customer's engineer in a
room this week, run one logged call end to end, write down every surprise in an agreement, and re-plan from
what the system actually does. Then tell the sponsor the date that is true (Day 30 owns that conversation).

**16. What does an LLM change about integration work in 2026, and what does it not?**
It drafts adapters, mappings, parsers and tests quickly, and it can explain records to users if you give it
the meanings. It does not know what a field means, what the transaction ceiling is, when the batch runs,
or which columns the owner signed off; it fills those gaps with plausible guesses, which in an integration
are duplicates and leaks. The rules live in code below the model.

## Quick-fire round

| Question | One-line answer |
|---|---|
| A read timeout on a create means? | it may have committed; never retry blindly |
| A connect timeout means? | nothing was sent; safe to retry |
| Where does the existence check go? | the system of record, live; never a replica |
| What does `.done` mean in a batch folder? | the manifest is complete; read nothing before it |
| A re-scan of the same file number? | a new version of the documents, the same application |
| zeep's `timeout` versus `operation_timeout`? | loading documents versus making calls |
| What is CL-E017 to the writer? | a deferral, not a failure |
| An unknown code from the core? | fail closed; add it to the mapping with the owner |
| What is in a reconciliation besides "all good"? | every exception by record, counts that tie out, what it could not check |
