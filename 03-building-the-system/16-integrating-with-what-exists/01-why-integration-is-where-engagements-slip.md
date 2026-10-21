# 01 · Why Integration Is Where Engagements Slip

> Day 16 · Section 1 of 18 · [Chapter overview](README.md) · Next: [02 · The integration surface](02-the-integration-surface.md)

---

## 1.1 A Thursday night in week 3

It is 02:30 on Thursday 12 November 2026. In the Hyderabad data centre, a job written before most of
Godavari's analysts joined has just moved 27 scanned loan files from the Kukatpally branch folder into the
Hyderabad region folder and registered a shell record for each one in the 2009 core lending system. In
fourteen hours, the analysts will approve ten of them, and for the first time Kaagaz's system, not a
person, will create the applications in the core's sandbox. Tomorrow at the week-3 checkpoint (milestone
M07, Day 8) the core-system owner will look at what happened.

Nothing about the model matters tonight. The extraction from Day 11, the client from Day 12 and the
prompts from Day 13 are finished for this slice. What decides whether the engagement keeps its calendar is
a set of questions nobody puts on a slide:

- One of the 27 files is still being written when the pickup runs. Do you read half a PDF?
- One file arrives at 02:40, after the manifest. Is it tonight's or tomorrow's?
- One create gets no reply. Did the core commit it? If you retry and it did, Godavari has two
  applications for one customer, exactly the four hundred duplicates the last vendor left in 2022.
- The last approval comes at 17:40, inside the window when nothing may write. What happens to it?
- The tracker on Srinivas's team says one file is "keyed". The core says it is still a shell. Who is right?
- The reporting database has the customer's name and PAN in it. May you read them? May you keep them?

Every one of these happens in this chapter's project, and every one is answered in code you can run.

## 1.2 Why integration is where the schedule goes

The Part 3 plan says it plainly: every engagement has a legacy system in it, and the integration is
usually where the schedule goes. There are four reasons, and none of them is that SOAP is hard.

1. **The other system's owner decides, and he decides early.** Godavari's core-system owner has run the
   2009 system for fourteen years and has watched three vendors fail. His words (Day 6, transcript 06):
   "They sent me a design in week eight. By week eight I had already decided." The integration's critical
   path is his trust, and trust is built by showing him logged calls, not documents.
2. **The contract is not the behaviour.** The WSDL says `DLR_CD` is optional; production rejects a
   two-wheeler application without it. The WSDL says nothing about a rate limit; the core answers
   "SERVICE BUSY" at the sixth call in a second. The sandbox is three months behind. You learn the real
   contract by running against it, which is why integration must start in week one (Day 7 put it first).
3. **Failures are silent and expensive.** A duplicate loan record is not an error message; it is a second
   application that someone sanctions, a weekend of manual cleanup, and, at Godavari, an audit
   observation with an analyst's name on it (finding B4).
4. **The data has rules about where it may be.** Customer PII may not leave India and nothing leaves the
   building before the CISO's review (finding B1, decision D08). That constrains every cache, every log
   line and every copy, and it is easy to break by accident in an integration layer.

## 1.3 Why it matters for your career

Core engineering appears in 95 percent or more of the 1,000 FDE postings analysed in 2026, and "in a
codebase you did not write" is part of the job description (CURRICULUM.md). The integration is the most
concrete version of that phrase: a system you did not write, owned by someone who does not report to you,
with behaviour nobody documented. The FDE interview's system-design round listens for exactly this: does
the candidate ask what happens on a timeout, where the idempotency lives, what the sandbox does not
cover, and who owns the integration after handoff. OpenAI's FDE team, as summarised in the ZenML LLMOps
database, describes building "translation or metadata layers that enable LLM access" rather than moving
data, and calls the metadata translation layer an underrated space with significant potential. That
layer is section 08 of this chapter.

## 1.4 The engagement step

Day 6 found the facts this chapter turns into code. Day 11 built an idempotent write against a fake
sandbox. This chapter replaces the fake with the real thing, in the shape the owner described:

| Day 6 finding or code | What this chapter builds |
|---|---|
| DUPLICATE_ON_RETRY: "It creates two applications" | a stand-in that duplicates, a naive client that proves it, a writer that does not |
| IDEMPOTENCY_LOOKUP_EXISTS: "Check with GetApplicationByFileNumber" | lookup before create, Day 11's key stamped in `EXT_REF`, a journal, a quiet period |
| SANDBOX_STALE: "Rules in the sandbox are three months behind" | a stale-sandbox mode, contract tests with a known-drift list that expires |
| BATCH_6PM and "nothing writes between five thirty and eight" | a write window the writer obeys, and a fault it understands when the batch overruns |
| FILE_ORIGIN_SCAN: the 02:00 job | a manifest-driven pickup that handles partial, late, re-run and re-scanned files |
| SHADOW_TRACKER (finding A2) | a tracker reader that trusts nothing, and a migration into the review queue |
| WRITE_CONDITION_LOGGED: "Bring the log" | a nightly reconciliation report built from his system and his access log |

## 1.5 The hard parts, named up front

Three things in this chapter feel wrong at first. That is normal.

1. **"Retry" is not a safe word.** Day 12 made retries routine for model calls, where a repeat costs
   money. For a create on a system with no idempotency key, a repeat costs a duplicate loan. You will
   unlearn the reflex.
2. **The lookup is necessary and not sufficient.** Looking up before creating fixes the lost-reply case
   and still duplicates when the core commits after your client has given up. Section 04 shows both, with
   numbers from a real run.
3. **The boring artefacts are the deliverable.** A mapping file, an agreement, a morning report. They look
   like paperwork. They are what makes the owner say yes on 8 December (M14).

> **Analogy (Telugu audience).** The auto driver. Your new car (the model) still cannot reach the house
> with no street name. The auto driver who knows every lane in the old city, which gully floods in the
> rains and which one is closed after six, is the integration layer, and he charges for it. This chapter
> is about becoming that driver for Godavari's old city.
