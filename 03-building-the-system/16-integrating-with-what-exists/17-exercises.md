# 17 · Exercises

> Day 16 · Section 17 of 18 · [Chapter overview](README.md) · Previous: [16 · Interview questions](16-interview-questions.md) · Next: [18 · Further reading](18-further-reading.md)

---

Learning mode: write the code yourself and use an AI assistant as a tutor ("explain why this lookup is
too early"), not as the author. Every code exercise runs in the chapter's virtual environment with
`python -X utf8 -m pytest code`. Answers to the reasoning parts are in the sections cited.

## Level 1: warm-up

**1.1 Read the WSDL.** Open `code/godavari_integration/wsdl/LendingService.wsdl`. Without running anything,
write down: the four operations; the SOAPAction of `UpdateKYCStatus`; which of `DLR_CD`, `MOB_NO` and
`EXT_REF` are mandatory according to the WSDL; and the three changes from the served file. Then say which
of the three fields production actually requires for a two-wheeler file, and how you know (03.2, 10.4).

**1.2 Predict the output.** In `test_lookup_then_retry_is_not_enough_when_the_commit_is_late`, the stall is
0.6 s and the client timeout 0.3 s. Predict how many applications the first file ends with if the stall is
changed to 0.2 s, and to 2.0 s. Run both and explain the difference in one sentence each (04.3).

**1.3 Sort the outcomes.** For each, say CoreFault, CoreUnavailable, NotSent or AmbiguousOutcome, and
whether a create may be retried: a DNS failure; HTTP 503 with an HTML page; a read timeout; CL-E099; a
reply zeep cannot parse; `Connection aborted` after the request was sent; CL-E052 (03.5).

**1.4 Map five fields.** Write mapping entries, in the owner's words, for `RES_TYP`, `YRS_AT_ADDR`,
`APPR_ID`, `CO_APPL_REL` and `PURP_CD`, each with `ours = false` and a reason. Then write the question
you would ask the owner about each before you could change your mind (08.2).

## Level 2: apply

**2.1 Break it, then fix it.** In `writer.py`, change `SafeCoreWriter._attempt` so that an
`AmbiguousOutcome` is retried immediately instead of being marked UNKNOWN. Run
`tests/test_idempotent_write.py`. Which tests fail, and which still pass? Explain why the
commit-then-stall case might still pass. Revert.

**2.2 Add APPLSTAT H.** The reconciliation reports `APPLSTAT H 'ON HOLD - FRAUD CHECK'`. Add it to the
mapping as version 1.4.0 with a canonical name and a meaning, record a new sign-off with
`translate.write_signoff`, and confirm that `from_core({"APPL_STAT": "H"})` now works and section 6 of the
report says "none". What test would you add so the next unknown code is caught the same way?

**2.3 A new tracker spelling.** A Vijayawada workbook uses "File Ref" for the file number and colours
"waiting" rows orange (`FFFFA500`). Make the reader handle both through the tracker mapping only (no code
change), bump its version, and write a test with a generated workbook.

**2.4 Make UpdateKYCStatus safe.** Add `set_kyc_status(appl_id, status, user)` to the safe writer: read
the current status with `GetApplication`, skip the call if it already matches, obey the write window, and
journal it. Test that two calls with the same status produce one history row in the stand-in.

**2.5 The orphan check.** Section 8 of the report says it cannot find applications carrying our
`EXT_REF` on files we never journaled. Write `find_orphans(owner_rows, journal)` that takes the rows the
owner's query returns (application ID, file number, EXT_REF) and lists any whose key is not in the
journal. Add it to the report as its own section, and write a test where an old script created one.

**2.6 A contract test for the busy fault.** Record a CL-E099 exchange (lower the stand-in's rate limit in
`record_sandbox.py`), add it to the cassette, and write a replay test that both clients classify it as
retryable. What must you change in `ReplaySession` so the new exchange does not steal another test's match?

## Level 3: challenging

**3.1 Review this AI-written code and find what is wrong.** `code/exercises/ai_draft_core_client.py` is a
client an agent wrote from a reasonable prompt. It has at least twelve problems that matter at Godavari.
For each, give the line, the Day 6 finding or owner's sentence it breaks, what would happen and when (the
first week, the first month end, the RBI audit), and a one-line fix. At least three are about data that
must not be copied or logged. Then rank the three you would fix before the M07 demo.

**3.2 Review an AI-written plan.** `worksheet/ai-draft-integration-plan.md` reads well and contains at least
fourteen problems: facts that contradict the discovery pack, decisions that belong to someone else, and
engineering that would duplicate loans or leak data. Write your review as a table (claim, what is wrong,
evidence, correction), and then the three sentences you would say to the sponsor about why the plan's
"two weeks from week 5" is the wrong shape.

**3.3 Design for a second core.** Krishna District Hospital (the capstone, Day 42) has a hospital
information system that exposes HL7 v2 messages over a TCP feed and a nightly CSV of discharges. Fill
`worksheet/integration-inventory-template.md` for it: which of this chapter's rules carry over unchanged,
which change shape (what is the natural key for a discharge? what is "the window"?), and what you would ask
the system's owner in the first meeting.

**3.4 CDC instead of the nightly copy.** The owner offers change data capture from the core's database
log instead of the 05:00 reporting copy. Write a one-page decision note: what it would improve in the
reconciliation, what it would add to the security review (Day 23) and to the residency question (Day 24),
who would own it after handoff, and your recommendation for the 90 days.

**3.5 Your own legacy system.** Pick a system you know that has no idempotency key. Write its four-outcome
table for the main write, its quiet period and where you would get the number, and break your design with
the two stall shapes.

**3.6 The client simulation.** The core-system owner, on the phone at 08:40 on a month-end morning: "I have
two applications for GF-25122 and both have your reference. You told me this could not happen." Write what
you say in the first minute, what you check in the next ten (section 15.6's routine), and the email you
send him by noon. Day 30 owns bad news; this is the integration's version.
